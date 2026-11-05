#!/usr/bin/env python3
"""数学第一课 40s 样片：Qwen TTS 字级时间戳 + 单行字幕 cue。"""
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
TMP = ROOT / ".work"; PUB = ROOT / "public"; SRC = ROOT / "src"
for d in (TMP, PUB, SRC): d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT.parent / "kepu-compare" / "tools"))
import qwen_tts_ts as q

VOICE = "longanlingxin_v3.1"; RATE = 1.05; LEAD, GAP, TAIL = 0.45, 0.4, 0.7
BEATS = [
    {"id":"b01","section":"hook","headline":"开场",
     "text":"天气预报最低 -3℃；读作零下三摄氏度，也可以读负三摄氏度。0℃ 是没有温度吗？",
     "cues":["天气预报最低 -3℃","读作零下三摄氏度","0℃ 是没有温度吗？"]},
    {"id":"b02","section":"rule","headline":"规定",
     "text":"小学学过负数；初中要理解：同一组量，怎么用一套符号表示。关键在「规定」：规定收入为正，记 +200、-150；规定支出为正，记 -200、+150。两种都行，但同一题选一种。",
     "cues":["小学学过负数","同一组相反意义的量","怎么用一套符号表示","关键在「规定」","规定收入为正","记 +200、-150","规定支出为正","记 -200、+150","两种都行","同一题选一种"]},
    {"id":"b03","section":"zero","headline":"0",
     "text":"那 0 呢？0 个苹果是没有；0℃ 是确定温度；0 米海拔是海平面。0 既不是正数，也不是负数，是分界。",
     "cues":["那 0 呢？","0 个苹果是没有","0℃ 是确定温度","0 米海拔是海平面","0 是正负数的分界"]},
    {"id":"b04","section":"line","headline":"数轴",
     "text":"用数轴把大小看得见。先画原点、正方向箭头、单位长度，每格等长。+3 在右 3 格，-3 在左 3 格。右边总比左边大。-3 和 -1 谁大？停两秒，看：-3 在 -1 左边，所以 -3 < -1。",
     "cues":["用数轴把大小看得见","先画原点","正方向画箭头","单位长度每格等长","+3 在右 3 格","-3 在左 3 格","右边总比左边大","-3 和 -1 谁大？","停两秒","-3 在 -1 左边","所以 -3 < -1"]},
]

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit("失败：%s\n%s" % (" ".join(cmd), p.stderr[-400:]))
    return p

def dur(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)]).stdout)

def silence(path, seconds):
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","%.3f"%seconds,"-c:a","pcm_s16le",str(path)])

lead=TMP/"lead.wav"; gap=TMP/"gap.wav"; tail=TMP/"tail.wav"
silence(lead,LEAD); silence(gap,GAP); silence(tail,TAIL)
items=[lead]; beats=[]; cues=[]; words_map={}; anchors={}; t=LEAD
totals={"calls":0,"input":0,"output":0,"total":0,"chars":0}; rows=[]
for i,b in enumerate(BEATS):
    r=q.synthesize(b["text"], VOICE, rate=RATE)
    mp3=TMP/(b["id"]+".mp3"); mp3.write_bytes(r["audio"])
    wav=TMP/(b["id"]+".wav")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp3),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(wav)])
    d=dur(wav); bstart=t
    beats.append({"id":b["id"],"section":b["section"],"headline":b["headline"],"text":b["text"],"start":round(bstart,3),"end":round(bstart+d,3),"duration":round(d,3)})
    beat_cues=q.cue_times(b["text"], r["words"], bstart, b["cues"])
    cues.extend(beat_cues)
    words_map[b["id"]]={"text":b["text"],"words":r["words"]}
    # anchors for S2 active state / S4 answer
    for phrase in ["规定收入为正","规定支出为正","-3 在 -1 左边"]:
        p=b["text"].replace(" ","").find(phrase.replace(" ",""))
        if p>=0:
            # map phrase start to char time
            norm="".join(w.get("text","") for w in r["words"]).replace(" ","")
            p2=norm.find(phrase.replace(" ",""))
            if p2>=0:
                acc=0; found=None
                for w2 in r["words"]:
                    ln=len(w2.get("text","").replace(" ","")) or 1
                    if p2 < acc+ln:
                        found=bstart+w2["begin_time"]/1000+(p2-acc)/ln*((w2["end_time"]-w2["begin_time"])/1000)
                        break
                    acc+=ln
                if found is not None: anchors[phrase]=round(found,3)
    u=r["usage"]; rows.append({"id":b["id"],"input_tokens":u.get("input_tokens",0),"output_tokens":u.get("output_tokens",0),"total_tokens":u.get("total_tokens",0),"characters":u.get("characters",0)})
    for k,s in (("input","input_tokens"),("output","output_tokens"),("total","total_tokens"),("chars","characters")):
        totals[k]+=int(u.get(s) or 0)
    totals["calls"]+=1
    items.append(wav); t+=d
    if i<len(BEATS)-1: items.append(gap); t+=GAP
items.append(tail)
listf=TMP/"list.txt"; listf.write_text("".join("file '%s'\n"%str(p.resolve()) for p in items),encoding="utf-8")
voice=PUB/"voice.wav"
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listf),"-c","copy",str(voice)])
duration=dur(voice)
timeline={"fps":30,"width":1920,"height":1080,"duration":round(duration,3),"frames":int(round(duration*30)),"beats":beats}
(SRC/"timeline.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"words.json").write_text(json.dumps(words_map,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"anchors.json").write_text(json.dumps(anchors,ensure_ascii=False,indent=2),encoding="utf-8")
now=datetime.now(); name="tts-math-sample-"+now.strftime("%Y%m%d-%H%M%S")+".json"
report={"generated_at":now.isoformat(timespec="seconds"),"voice":VOICE,"rate":RATE,"rows":rows,"totals":totals,"duration":duration,"paths":str(ROOT)}
(ROOT/"TTS_BILLING_MATH_SAMPLE.md").write_text("# TTS 计费 · 数学第一课 40s 样片\n\n- 音色：%s（rate %.2f）\n\n| 指标 | 合计 |\n|---|---|\n| 调用 | %d |\n| 输入 tokens | %d |\n| 输出 tokens | %d |\n| 总 tokens | %d |\n| API characters | %d |\n| 音频 | %.2fs |\n"%(VOICE,RATE,totals["calls"],totals["input"],totals["output"],totals["total"],totals["chars"],duration),encoding="utf-8")
print(json.dumps({"duration":duration,"frames":timeline["frames"],"cues":len(cues),"anchors":anchors,"totals":totals},ensure_ascii=False))
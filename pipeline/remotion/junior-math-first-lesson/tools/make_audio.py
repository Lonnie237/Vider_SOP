#!/usr/bin/env python3
"""数学第一课 S1–S4 样片：严格字幕对齐 + 锚点 + 2s 思考窗。"""
import json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / ".work"; PUB = ROOT / "public"; SRC = ROOT / "src"
for d in (TMP, PUB, SRC): d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT.parent / "kepu-compare" / "tools"))
import qwen_tts_ts as q

VOICE = "longanlingxin_v3.1"; RATE = 1.05; LEAD, GAP, TAIL = 0.45, 0.4, 0.65
BEATS = [
    {"id":"b01","section":"hook","headline":"开场",
     "text":"天气预报最低零下三摄氏度。这个数写作负三，也读作负三摄氏度。零摄氏度是没有温度吗？",
     "cues":["天气预报最低零下三摄氏度","这个数写作负三","也读作负三摄氏度","零摄氏度是没有温度吗"]},
    {"id":"b02","section":"rule","headline":"规定",
     "text":"小学学过负数。初中要理解：同一组量，怎么用一套符号表示。关键在「规定」。收入二百，支出一百五十。规定收入为正，记正二百、负一百五十；规定支出为正，记负二百、正一百五十。两种都行，但同一题选一种。正号、负号，不是加减法。",
     "cues":["小学学过负数","初中要理解","同一组量","怎么用一套符号表示","关键在「规定」","收入二百","支出一百五十","规定收入为正","记正二百、负一百五十","规定支出为正","记负二百、正一百五十","两种都行","但同一题选一种","正号、负号","不是加减法"]},
    {"id":"b03","section":"zero","headline":"0",
     "text":"那零呢？零个苹果，是一个也没有。但零摄氏度不是没有温度，它是温度计上的确定刻度。零米海拔也不是没有高度，它是海平面。零既不是正数，也不是负数，是分界。",
     "cues":["那零呢","零个苹果","是一个也没有","零摄氏度不是没有温度","它是温度计上的确定刻度","零米海拔也不是没有高度","它是海平面","零既不是正数","也不是负数","是分界"]},
    {"id":"b04a","section":"line","headline":"数轴",
     "text":"用数轴把大小看得见。一条直线，规定原点、正方向、单位长度。正方向画箭头，通常向右；每一格一样长。正三在右边三个单位，负三在左边三个单位。右边总比左边大。先猜：负三和负一，谁大？",
     "cues":["用数轴把大小看得见","一条直线","规定原点","正方向","单位长度","正方向画箭头","通常向右","每一格一样长","正三在右边三个单位","负三在左边三个单位","右边总比左边大","负三和负一，谁大"],"pause_after":2.0},
    {"id":"b04b","section":"line","headline":"数轴",
     "text":"负三在负一左边，所以负三小于负一。",
     "cues":["负三在负一左边","所以负三小于负一"]},
]
ANCHORS = ["规定收入为正","规定支出为正","两种都行","零个苹果","零摄氏度","零米海拔","零既不是正数","是分界","正三在右边","负三在左边","负三和负一","负三在负一左边","这个数写作负三","零摄氏度是没有温度"]

def norm(s):
    return re.sub(r"[，。：；、！？「」“”\"'（）()\s]", "", s)

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit("失败：%s\n%s" % (" ".join(cmd), p.stderr[-500:]))
    return p

def dur(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)]).stdout)

def silence(path, seconds):
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","%.3f"%seconds,"-c:a","pcm_s16le",str(path)])

def char_times(words):
    chars=[]
    for w in words:
        t=w.get("begin_time",0)/1000.0; e=w.get("end_time",0)/1000.0
        txt=norm(w.get("text",""))
        n=max(1,len(txt))
        for i in range(n): chars.append((t+(e-t)*i/n, t+(e-t)*(i+1)/n))
    return chars

def strict_cues(text, words, start, cues):
    chars=char_times(words)
    nw="".join(norm(w.get("text","")) for w in words)
    out=[]; cursor=0
    for cue in cues:
        nc=norm(cue); pos=nw.find(nc,cursor)
        if pos<0:
            raise SystemExit("cue 未命中：%r（cursor=%d，words=%r）" % (cue,cursor,nw))
        q=pos+len(nc); cursor=q
        out.append({"text":cue,"start":round(start+chars[pos][0],3),"end":round(start+chars[q-1][1],3)})
    return out

def phrase_time(beat, words, phrase):
    nw="".join(norm(w.get("text","")) for w in words); np=norm(phrase); p=nw.find(np)
    if p<0: return None
    chars=char_times(words)
    return round(beat["start"]+chars[p][0],3)

lead=TMP/"lead.wav"; gap=TMP/"gap.wav"; tail=TMP/"tail.wav"
silence(lead,LEAD); silence(gap,GAP); silence(tail,TAIL)
items=[lead]; beats=[]; cues=[]; words_map={}; anchors={}; t=LEAD
tot={"calls":0,"input":0,"output":0,"total":0,"chars":0}; rows=[]
for i,b in enumerate(BEATS):
    r=q.synthesize(b["text"], VOICE, rate=RATE)
    mp3=TMP/(b["id"]+".mp3"); mp3.write_bytes(r["audio"])
    wav=TMP/(b["id"]+".wav")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp3),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(wav)])
    d=dur(wav); bstart=t
    be={"id":b["id"],"section":b["section"],"headline":b["headline"],"text":b["text"],"start":round(bstart,3),"end":round(bstart+d,3),"duration":round(d,3)}
    beats.append(be)
    cue_list=strict_cues(b["text"],r["words"],bstart,b["cues"])
    cues.extend(cue_list)
    words_map[b["id"]]={"text":b["text"],"words":r["words"]}
    for phrase in ANCHORS:
        v=phrase_time(be,r["words"],phrase)
        if v is not None: anchors[phrase]=v
    u=r["usage"]; rows.append({"id":b["id"],"input_tokens":u.get("input_tokens",0),"output_tokens":u.get("output_tokens",0),"total_tokens":u.get("total_tokens",0),"characters":u.get("characters",0)})
    for k,s in (("input","input_tokens"),("output","output_tokens"),("total","total_tokens"),("chars","characters")):
        tot[k]+=int(u.get(s) or 0)
    tot["calls"]+=1
    items.append(wav); t+=d
    if b.get("pause_after"):
        sp=TMP/("pause-"+b["id"]+".wav"); silence(sp,float(b["pause_after"])); items.append(sp); t+=float(b["pause_after"])
    elif i<len(BEATS)-1:
        items.append(gap); t+=GAP
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
now=datetime.now()
report={"generated_at":now.isoformat(timespec="seconds"),"voice":VOICE,"rate":RATE,"rows":rows,"totals":tot,"duration":duration,"anchors":anchors}
B=ROOT/"billing"; B.mkdir(exist_ok=True)
(B/("tts-math-sample-"+now.strftime("%Y%m%d-%H%M%S")+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
(ROOT/"TTS_BILLING_MATH_SAMPLE.md").write_text("# TTS 计费 · 数学第一课 S1–S4 样片\n\n- 音色：%s（rate %.2f）\n\n| 指标 | 合计 |\n|---|---|\n| 调用 | %d |\n| 输入 tokens | %d |\n| 输出 tokens | %d |\n| 总 tokens | %d |\n| API characters | %d |\n| 音频 | %.2fs |\n"%(VOICE,RATE,tot["calls"],tot["input"],tot["output"],tot["total"],tot["chars"],duration),encoding="utf-8")
print(json.dumps({"duration":duration,"frames":timeline["frames"],"cues":len(cues),"anchors":len(anchors),"totals":tot},ensure_ascii=False))
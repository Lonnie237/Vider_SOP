#!/usr/bin/env python3
"""数学第一课全片 S0–S7：严格字幕对齐 + 锚点 + 预测停顿 + 两遍 loudnorm。

旁白依据 research/2026-11-05-初中数学第一课-脚本v4.md §8，改写为 TTS 中文读法；
cue 全部为 TTS 文本精确子串（生成时断言命中）；锚点取首次命中，避免跨镜串扰。
"""
import json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / ".work"; PUB = ROOT / "public"; SRC = ROOT / "src"; OUT = ROOT / "out"
for d in (TMP, PUB, SRC, OUT): d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT.parent / "kepu-compare" / "tools"))
import qwen_tts_ts as q

VOICE = "longanlingxin_v3.1"; RATE = 0.75
COVER, GAP, HOLD, ANSWER = 4.0, 0.4, 2.0, 1.5  # S0 封面；句间；S7 思考 HOLD；答案展示
BEATS = [
    {"id":"b1","scene":"S1","headline":"开场",
     "text":"天气预报说明天最低零下三摄氏度。这个数写作负三，读作零下三摄氏度，也可以读负三摄氏度。可为什么数学里要写成负三，而不是每次写零下三？零摄氏度又是不是没有温度？",
     "cues":["天气预报说明天最低零下三摄氏度","这个数写作负三","读作零下三摄氏度","也可以读负三摄氏度","可为什么数学里要写成负三","而不是每次写零下三","零摄氏度又是不是没有温度"]},
    {"id":"b2","scene":"S2","headline":"规定",
     "text":"小学六年级你学过负数：温度、存折。初中第一课要往前走一步：不是记住零下写负号，而是理解，同一组相反意义的量，怎么用一套符号统一表示。关键在规定。比如存折：收入二百，支出一百五十。规定收入为正，就记正二百、负一百五十；规定支出为正，就记负二百、正一百五十。两种规定都行，但同一道题里只能选一种。注意：正二百前面的符号是正号，不是加法；负一百五十前面的符号是负号，不是减法。",
     "cues":["小学六年级你学过负数","温度、存折","初中第一课要往前走一步","不是记住零下写负号","而是理解","同一组相反意义的量","怎么用一套符号统一表示","关键在规定","比如存折","收入二百","支出一百五十","规定收入为正","就记正二百、负一百五十","规定支出为正","就记负二百、正一百五十","两种规定都行","但同一道题里只能选一种","注意","正二百前面的符号是正号","不是加法","负一百五十前面的符号是负号","不是减法"]},
    {"id":"b3","scene":"S3","headline":"0",
     "text":"那零呢？零个苹果，确实是一个也没有。但零摄氏度不是没有温度，它是温度计上的一个确定刻度；零米海拔也不是没有高度，它是海平面。所以零有两种用法：记数时表示没有；作刻度或基准时，是一个确定的点。零既不是正数，也不是负数，它是正负数的分界。",
     "cues":["那零呢","零个苹果","确实是一个也没有","但零摄氏度不是没有温度","它是温度计上的一个确定刻度","零米海拔也不是没有高度","它是海平面","所以零有两种用法","记数时表示没有","作刻度或基准时","是一个确定的点","零既不是正数","也不是负数","它是正负数的分界"]},
    {"id":"b4a","scene":"S4","headline":"数轴",
     "text":"怎么把相反和大小看得见？用数轴。一条直线，规定原点、正方向、单位长度。原点就是零；正方向画箭头，通常向右；单位长度就是一格代表多少，每一格必须一样长。正三在原点右边三个单位，负三在左边三个单位。数轴上，右边的数总比左边大。先别急着信：负三和负一，谁大？",
     "cues":["怎么把相反和大小看得见","用数轴","一条直线","规定原点","正方向","单位长度","原点就是零","正方向画箭头","通常向右","单位长度就是一格代表多少","每一格必须一样长","正三在原点右边三个单位","负三在左边三个单位","数轴上","右边的数总比左边大","先别急着信","负三和负一，谁大"],"pause_after":2.0},
    {"id":"b4b","scene":"S4","headline":"数轴",
     "text":"看数轴：负三在负一左边，所以负三小于负一。",
     "cues":["看数轴","负三在负一左边","所以负三小于负一"]},
    {"id":"b5a","scene":"S5","headline":"比较",
     "text":"再看一组：负一百和负一，谁大？先猜一猜。",
     "cues":["再看一组","负一百和负一，谁大","先猜一猜"],"pause_after":1.5},
    {"id":"b5b","scene":"S5","headline":"比较",
     "text":"看数轴：负一百在负一左边，所以负一百小于负一。注意，不是数字一百比一大，负一百就更大；负号后面的数越大，位置越靠左，值反而越小。先猜，再用数轴验证。",
     "cues":["看数轴","负一百在负一左边","所以负一百小于负一","注意","不是数字一百比一大","负一百就更大","负号后面的数越大","位置越靠左","值反而越小","先猜","再用数轴验证"]},
    {"id":"b6a","scene":"S6","headline":"三个坑",
     "text":"最后做三个小检查。第一，零个苹果和零摄氏度：一个表示没有，一个是确定温度。",
     "cues":["最后做三个小检查","第一","零个苹果和零摄氏度","一个表示没有","一个是确定温度"]},
    {"id":"b6b","scene":"S6","headline":"三个坑",
     "text":"第二，负三，和三减五。负三前面的符号是负号；三减五中间的符号是减号。",
     "cues":["第二","负三，和三减五","负三前面的符号是负号","三减五中间的符号是减号"]},
    {"id":"b6c1","scene":"S6","headline":"三个坑",
     "text":"第三，负五和负二，谁小？先猜。",
     "cues":["第三","负五和负二，谁小","先猜"],"pause_after":1.5},
    {"id":"b6c2","scene":"S6","headline":"三个坑",
     "text":"看数轴：负五在负二左边，所以负五小于负二。",
     "cues":["看数轴","负五在负二左边","所以负五小于负二"]},
    {"id":"b7","scene":"S7","headline":"回收",
     "text":"第一课记三个工具：先规定正方向；零是分界；数轴看位置。接下来，我们学有理数的分类，再用数轴看相反数和绝对值。留一个问题：在数轴上，从负二到三，要走几个单位长度？数完告诉我。",
     "cues":["第一课记三个工具","先规定正方向","零是分界","数轴看位置","接下来","我们学有理数的分类","再用数轴看相反数和绝对值","留一个问题","在数轴上","从负二到三","要走几个单位长度","数完告诉我"]},
]
ANCHORS = ["这个数写作负三","读作零下三摄氏度","也可以读负三摄氏度","零摄氏度又是不是没有温度",
           "规定收入为正","规定支出为正","两种规定都行","正二百前面的符号是正号","负一百五十前面的符号是负号",
           "零个苹果","零摄氏度不是没有温度","零米海拔","所以零有两种用法","零既不是正数","它是正负数的分界",
           "原点就是零","正方向画箭头","单位长度就是一格代表多少","每一格必须一样长","正三在原点右边","负三在左边","右边的数总比左边大","负三和负一","负三在负一左边",
           "负一百和负一","负一百在负一左边","负号后面的数越大","位置越靠左",
           "第一零个苹果","零个苹果和零摄氏度","一个表示没有","一个是确定温度","第二负三","负三前面的符号是负号","三减五中间的符号是减号","第三负五","负五和负二","负五在负二左边",
           "先规定正方向","零是分界","数轴看位置","我们学有理数的分类","再用数轴看相反数和绝对值","从负二到三"]

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

def measure(path, target=-16):
    p = subprocess.run(["ffmpeg","-hide_banner","-i",str(path),"-af","loudnorm=I=%d:TP=-1.5:LRA=11:print_format=json"%target,"-f","null","-"],capture_output=True,text=True)
    text=(p.stderr or "")+(p.stdout or ""); s=text.rfind("{"); e=text.rfind("}")
    if s<0 or e<=s: raise SystemExit("loudnorm 测量失败")
    return json.loads(text[s:e+1])

def srt_ts(t):
    ms=int(round(t*1000)); h=ms//3600000; m=ms%3600000//60000; s=ms%60000//1000; r=ms%1000
    return "%02d:%02d:%02d,%03d"%(h,m,s,r)

cover=TMP/"cover.wav"; gap=TMP/"gap.wav"; hold=TMP/"hold.wav"
silence(cover,COVER); silence(gap,GAP); silence(hold,HOLD+ANSWER)
items=[cover]; beats=[]; cues=[]; words_map={}; anchors={}; t=COVER
tot={"calls":0,"input":0,"output":0,"total":0,"chars":0}; rows=[]
for i,b in enumerate(BEATS):
    r=q.synthesize(b["text"], VOICE, rate=RATE)
    mp3=TMP/(b["id"]+".mp3"); mp3.write_bytes(r["audio"])
    wav=TMP/(b["id"]+".wav")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp3),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(wav)])
    d=dur(wav); bstart=t
    be={"id":b["id"],"scene":b["scene"],"headline":b["headline"],"text":b["text"],"start":round(bstart,3),"end":round(bstart+d,3),"duration":round(d,3)}
    beats.append(be)
    cues.extend(strict_cues(b["text"],r["words"],bstart,b["cues"]))
    words_map[b["id"]]={"text":b["text"],"words":r["words"]}
    for phrase in ANCHORS:
        if phrase in anchors: continue  # 首次命中优先，防止后镜同词覆盖
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
items.append(hold)
listf=TMP/"list.txt"; listf.write_text("".join("file '%s'\n"%str(p.resolve()) for p in items),encoding="utf-8")
raw=TMP/"voice-full-raw.wav"
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listf),"-c","copy",str(raw)])
before=measure(raw)
voice=PUB/"voice-full.wav"
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(raw),
     "-af","loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"%(
         before["input_i"],before["input_tp"],before["input_lra"],before["input_thresh"],before["target_offset"]),
     "-ar","48000","-ac","1","-c:a","pcm_s16le",str(voice)])
after=measure(voice)
duration=dur(voice)
assert abs(duration-dur(raw))<0.05, "loudnorm 改变了时长"
missing=[a for a in ANCHORS if a not in anchors]
assert not missing, "锚点未命中：%r"%missing
timeline={"fps":30,"width":1920,"height":1080,"duration":round(duration,3),"frames":int(round(duration*30)),
          "cover":COVER,"hold":HOLD,"answer":ANSWER,"lufs_before":float(before["input_i"]),"lufs_after":float(after["input_i"]),"beats":beats}
(SRC/"timeline-full.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"cues-full.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"words-full.json").write_text(json.dumps(words_map,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"anchors-full.json").write_text(json.dumps(anchors,ensure_ascii=False,indent=2),encoding="utf-8")
srt="".join("%d\n%s --> %s\n%s\n\n"%(i+1,srt_ts(c["start"]),srt_ts(c["end"]),c["text"]) for i,c in enumerate(cues))
(OUT/"full.srt").write_text(srt,encoding="utf-8")
now=datetime.now()
report={"generated_at":now.isoformat(timespec="seconds"),"voice":VOICE,"rate":RATE,"rows":rows,"totals":tot,"duration":duration,"anchors":anchors}
B=ROOT/"billing"; B.mkdir(exist_ok=True)
(B/("tts-math-full-"+now.strftime("%Y%m%d-%H%M%S")+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
(ROOT/"TTS_BILLING_MATH_FULL.md").write_text("# TTS 计费 · 数学第一课全片 S0–S7\n\n- 音色：%s（rate %.2f）\n\n| 指标 | 合计 |\n|---|---|\n| 调用 | %d |\n| 输入 tokens | %d |\n| 输出 tokens | %d |\n| 总 tokens | %d |\n| API characters | %d |\n| 音频 | %.2fs |\n| 响度 | %.1f → %.1f LUFS |\n"%(
    VOICE,RATE,tot["calls"],tot["input"],tot["output"],tot["total"],tot["chars"],duration,float(before["input_i"]),float(after["input_i"])),encoding="utf-8")
print(json.dumps({"duration":duration,"frames":timeline["frames"],"cues":len(cues),"anchors":len(anchors),"lufs":[before["input_i"],after["input_i"]],"totals":tot},ensure_ascii=False))
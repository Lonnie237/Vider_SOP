#!/usr/bin/env python3
import json, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/".work-v"; SRC=ROOT/"src"; PUB=ROOT/"public"
for d in (TMP,SRC,PUB): d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT.parents[1]/"remotion"/"kepu-compare"/"tools"))
import qwen_tts_ts as q
VOICE="longanlingxin_v3.1"; RATE=0.95
TEXT="每天早上九点十五，汇率中间价更新。还在手动复制？把网址和字段交给它，每天九点三十自动出表。WorkBuddy 搜网站采集工程师，扫码打开。"
CUES=["每天早上九点十五","汇率中间价更新","还在手动复制","把网址和字段交给它","每天九点三十自动出表","搜网站采集工程师","扫码打开"]
def norm(s): return re.sub(r"[，。：；、！？「」“”\"'（）()\s]","",s)
def run(c):
    p=subprocess.run(c,capture_output=True,text=True)
    if p.returncode: raise SystemExit(p.stderr[-400:])
    return p
def dur(p): return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)]).stdout)
def silence(p,s): run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","%.3f"%s,"-c:a","pcm_s16le",str(p)])
lead=TMP/"lead.wav"; tail=TMP/"tail.wav"; silence(lead,0.35); silence(tail,0.7)
r=q.synthesize(TEXT,VOICE,rate=RATE)
(TMP/"v.mp3").write_bytes(r["audio"])
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(TMP/"v.mp3"),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(TMP/"v.wav")])
d=dur(TMP/"v.wav")
nw="".join(norm(w.get("text","")) for w in r["words"])
chars=[]
for w in r["words"]:
    t=w.get("begin_time",0)/1000; e=w.get("end_time",0)/1000; n=max(1,len(norm(w.get("text",""))))
    for i in range(n): chars.append((t+(e-t)*i/n,t+(e-t)*(i+1)/n))
cues=[]; cursor=0
for c in CUES:
    nc=norm(c); p=nw.find(nc,cursor)
    if p<0: raise SystemExit("cue miss "+c+" / "+nw)
    q2=p+len(nc); cursor=q2
    cues.append({"text":c,"start":round(0.35+chars[p][0],3),"end":round(0.35+chars[q2-1][1],3)})
listf=TMP/"list.txt"; listf.write_text("file '%s'\nfile '%s'\nfile '%s'\n"%(str(lead.resolve()),str(TMP/"v.wav"),str(tail.resolve())),encoding="utf-8")
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listf),"-c","copy",str(PUB/"voice-vertical.wav")])
total=dur(PUB/"voice-vertical.wav")
timeline={"fps":30,"width":1080,"height":1920,"duration":round(total,3),"frames":int(round(total*30))}
(SRC/"timeline-vertical.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"cues-vertical.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"words-vertical.json").write_text(json.dumps(r["words"],ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"duration":total,"frames":timeline["frames"],"cues":len(cues),"tokens":r["usage"]},ensure_ascii=False))

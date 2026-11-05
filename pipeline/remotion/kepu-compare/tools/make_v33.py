#!/usr/bin/env python3
"""v3.3 全片：Qwen TTS 字级时间戳 + 单行静态字幕 + 锚点 cue。"""
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".work"; PUB = ROOT / "public"; SRC = ROOT / "src"; BILLING = ROOT / "billing"
for d in (TMP, PUB, SRC, BILLING):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tools"))
import qwen_tts_ts as q

VOICE = "longanlingxin_v3.1"; RATE = 1.05; LEAD, GAP, TAIL = 0.45, 0.42, 0.9
BEATS = json.loads((SRC / "script-v2.json").read_text(encoding="utf-8"))
CUES = {
 "b01": ["周一早上九点", "你打开电脑", "左边是没写完的周报", "右边是等着修的 bug", "如果只能装一个 AI 工作台", "你装哪个？"],
 "b02": ["很多人以为", "WorkBuddy 和 Qoder", "只是两个更聪明的聊天框", "其实从第一天起", "它们走的就是两条路"],
 "b03": ["它们都是 AI 工作台", "能拆任务、调工具", "把结果直接交给你", "区别在主场", "WorkBuddy 是腾讯的", "办公工作台", "Qoder 是阿里的", "编程工作台"],
 "b04": ["先看上下文", "WorkBuddy 读的是文档", "表格、会议纪要", "还有腾讯文档和企业微信", "Qoder 读的是代码", "仓库、PR 和终端"],
 "b05": ["再看产出", "一个把 Word、Excel", "PPT、报告放到你桌上", "一个把代码、测试", "提交记录和 PR", "交到仓库里"],
 "b06": ["最后看形态", "WorkBuddy 是桌面工作台", "长在腾讯办公生态里", "Qoder 是 IDE、插件", "CLI 和云端 Agent", "长在开发者工作流里"],
 "b07": ["那为什么两家各推一款？", "因为腾讯有 CodeBuddy", "管编程、WorkBuddy 管办公", "阿里有 Qoder 管代码", "QoderWork 管办公", "不是重复造轮子", "是同一能力的两条产品线"],
 "b08": ["普通人怎么选？", "问三个问题", "你每天打开的是文档", "还是 IDE？", "产出交给老板", "还是代码库？", "你已经在用腾讯文档、企微", "还是阿里云、开发者工具？"],
 "b09": ["办公为主", "选 WorkBuddy", "开发为主", "选 Qoder", "两个都干", "先用免费版各试一周"],
 "b10": ["价格和功能会变", "商用前看合规", "工具是壳", "工作流才是核心", "你每天的工作", "更像哪一边？"],
}

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit("失败：%s\n%s" % (" ".join(cmd), p.stderr[-400:]))
    return p

def dur(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)]).stdout)

def silence(path, seconds):
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","%.3f"%seconds,"-c:a","pcm_s16le",str(path)])

lead = TMP/"v33-lead.wav"; gap = TMP/"v33-gap.wav"; tail = TMP/"v33-tail.wav"
silence(lead, LEAD); silence(gap, GAP); silence(tail, TAIL)
items=[lead]; beats=[]; cues=[]; words_map={}; t=LEAD
totals={"input":0,"output":0,"total":0,"chars":0,"calls":0}; rows=[]
for i,b in enumerate(BEATS):
    r=q.synthesize(b["text"], VOICE, rate=RATE)
    mp3=TMP/(b["id"]+".mp3"); mp3.write_bytes(r["audio"])
    wav=TMP/(b["id"]+".wav")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp3),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(wav)])
    d=dur(wav); bstart=t
    beats.append({"id":b["id"],"section":b["section"],"headline":b["headline"],"text":b["text"],"start":round(bstart,3),"end":round(bstart+d,3),"duration":round(d,3)})
    beat_cues=q.cue_times(b["text"], r["words"], bstart, CUES[b["id"]])
    for c in beat_cues:
        c["tokens"] = []
    cues.extend(beat_cues)
    words_map[b["id"]]={"text":b["text"],"words":r["words"]}
    u=r["usage"]; row={"id":b["id"],"chars":len(b["text"]),"input_tokens":u.get("input_tokens",0),"output_tokens":u.get("output_tokens",0),"total_tokens":u.get("total_tokens",0),"characters":u.get("characters",0)}
    rows.append(row)
    for k,s in (("input","input_tokens"),("output","output_tokens"),("total","total_tokens"),("chars","characters")):
        totals[k]+=int(u.get(s) or 0)
    totals["calls"]+=1
    items.append(wav); t+=d
    if i<len(BEATS)-1: items.append(gap); t+=GAP
items.append(tail)
listf=TMP/"v33-list.txt"; listf.write_text("".join("file '%s'\n"%str(p.resolve()) for p in items),encoding="utf-8")
voice=PUB/"voice-v33.wav"
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listf),"-c","copy",str(voice)])
duration=dur(voice)
timeline={"fps":30,"width":1920,"height":1080,"duration":round(duration,3),"frames":int(round(duration*30)),"beats":beats}
(SRC/"timeline-v33.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"cues-v33.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding="utf-8")
(SRC/"words-v33.json").write_text(json.dumps(words_map,ensure_ascii=False,indent=2),encoding="utf-8")
now=datetime.now(); name="tts-v33-"+now.strftime("%Y%m%d-%H%M%S")+".json"
report={"generated_at":now.isoformat(timespec="seconds"),"voice":VOICE,"rate":RATE,"rows":rows,"totals":totals,"duration":duration}
(BILLING/name).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
lines=["# TTS 计费 · v3.3 全片","","- 音色：%s（rate %.2f）"%(VOICE,RATE),"- 明细：%s"%name,"","| 指标 | 合计 |","|---|---|","| 调用 | %d |"%totals["calls"],"| 输入 tokens | %d |"%totals["input"],"| 输出 tokens | %d |"%totals["output"],"| 总 tokens | %d |"%totals["total"],"| API characters | %d |"%totals["chars"],"| 音频 | %.2fs |"%duration]
(ROOT/"TTS_BILLING_V33.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"duration":duration,"frames":timeline["frames"],"cues":len(cues),"totals":totals,"billing":name},ensure_ascii=False))

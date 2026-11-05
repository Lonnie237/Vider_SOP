import json, subprocess
from pathlib import Path
ROOT = Path(".")
PUB = ROOT / "public"
TMP = ROOT / ".work"
TMP.mkdir(exist_ok=True)
src = PUB / "voice-v2.wav"

# 片段：b01 + 间隔 + b03 + 间隔 + b04
segs = [
    (0.0, 10.222, "s1"),
    (18.137, 29.659, "s2"),
    (30.079, 39.431, "s3"),
]
files = []
for a, b, name in segs:
    out = TMP / ("v3s-" + name + ".wav")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(a),"-t",str(b-a),"-i",str(src),"-ar","48000","-ac","1","-c:a","pcm_s16le",str(out)], check=True)
    files.append(out)
# 0.6s 尾静音
tail = TMP / "v3s-tail.wav"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","0.6","-c:a","pcm_s16le",str(tail)], check=True)
files.append(tail)
listf = TMP / "v3s-list.txt"
listf.write_text("".join("file '%s'\n" % str(p.resolve()) for p in files), encoding="utf-8")
outwav = PUB / "voice-v3-sample.wav"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listf),"-c","copy",str(outwav)], check=True)
d = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(outwav)],capture_output=True,text=True).stdout)
beats = [
    {"id":"b01","section":"hook","headline":"周一 9:00","text":"周一早上九点，你打开电脑：左边是没写完的周报，右边是等着修的 bug。如果只能装一个 AI 工作台，你装哪个？","start":0.45,"end":9.802,"duration":9.352},
    {"id":"b03","section":"define","headline":"一句话定义","text":"它们都是 AI 工作台：能拆任务、调工具、把结果直接交给你。区别在主场：WorkBuddy 是腾讯的办公工作台，Qoder 是阿里的编程工作台。","start":10.642,"end":21.744,"duration":11.102},
    {"id":"b04","section":"context","headline":"差异① 上下文","text":"先看上下文。WorkBuddy 读的是文档、表格、会议纪要，还有腾讯文档和企业微信；Qoder 读的是代码、仓库、PR 和终端。","start":22.164,"end":31.516,"duration":9.352},
]
timeline = {"fps":30,"width":1920,"height":1080,"duration":round(d,3),"frames":int(round(d*30)),"beats":beats}
(ROOT/"src"/"timeline-v3-sample.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")

# cues：按字数比例分配，每条 0.9s 起
cue_texts = {
 "b01": ["周一早上九点", "你打开电脑", "左边是没写完的周报", "右边是等着修的 bug", "如果只能装一个 AI 工作台", "你装哪个？"],
 "b03": ["它们都是 AI 工作台", "能拆任务、调工具", "把结果直接交给你", "区别在主场", "WorkBuddy 是腾讯的办公工作台", "Qoder 是阿里的编程工作台"],
 "b04": ["先看上下文", "WorkBuddy 读文档、表格", "会议纪要和腾讯文档", "Qoder 读代码、仓库", "PR 和终端"],
}
cues = []
for b in beats:
    texts = cue_texts[b["id"]]
    total_chars = sum(len(x) for x in texts)
    dur = b["duration"]
    t = b["start"]
    for i, text in enumerate(texts):
        share = dur * len(text) / total_chars
        # 最后一条吃掉剩余，避免累计误差
        if i == len(texts) - 1:
            end = b["end"]
        else:
            end = t + max(0.9, share)
        cues.append({"start":round(t,3),"end":round(end,3),"text":text})
        t = end
    # 若最后超出，压回
    if t > b["end"]:
        cues[-1]["end"] = b["end"]
(ROOT/"src"/"cues-v3-sample.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"duration":d,"frames":timeline["frames"],"cues":len(cues),"cues_data":cues},ensure_ascii=False)[:1200])
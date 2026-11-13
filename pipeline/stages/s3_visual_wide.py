#!/usr/bin/env python3
"""S3 视觉（长教程 16:9）：用 Pillow 渲染逐 beat 横版知识卡，再用 ffmpeg 拼成无声底片。"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

W, H = 1920, 1080
MARGIN = 120
ACCENTS = {
    "hook": (245, 158, 11),
    "point": (56, 189, 248),
    "reason": (167, 139, 250),
    "method": (52, 211, 153),
    "cta": (244, 114, 182),
    "transition": (148, 163, 184),
}
ROLE_LABELS = {"hook": "钩子", "point": "结论", "reason": "原因", "method": "方法",
               "cta": "行动引导", "transition": "过渡"}


def parse_args():
    p = argparse.ArgumentParser(description="S3 渲染横版知识卡与底片")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def gradient():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    top, bottom = (11, 18, 32), (17, 24, 39)
    for y in range(H):
        ratio = y / max(1, H - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def draw_grid(img):
    from PIL import Image, ImageDraw
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, W, 160):
        d.line([(x, 0), (x, H)], fill=(148, 163, 184, 18), width=1)
    for y in range(0, H, 160):
        d.line([(0, y), (W, y)], fill=(148, 163, 184, 18), width=1)
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))


def chip(draw, xy, text, font, fill, color):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle([x, y, x + w + 44, y + h + 26], radius=14, fill=fill)
    draw.text((x + 22, y + 13 - bbox[1]), text, font=font, fill=color)


def render_card(path, beat, index, total, accent, is_tail=False):
    from PIL import Image, ImageDraw, ImageFont
    img = gradient()
    draw_grid(img)
    draw = ImageDraw.Draw(img)
    fp = common.find_cjk_font()
    f_tag = ImageFont.truetype(fp, 28)
    f_index = ImageFont.truetype(fp, 40)
    f_role = ImageFont.truetype(fp, 30)
    title_size = 112 if beat.get("role") == "hook" else 92
    f_title = ImageFont.truetype(fp, title_size)

    if is_tail:
        chip(draw, (MARGIN, 90), "长教程 · 剪辑工作流", f_tag, (30, 41, 59), (226, 232, 240))
        lines = beat["headline"].split("\n")
        total_h = len(lines) * int(title_size * 1.3)
        y = (H - total_h) // 2 - 40
        for line in lines:
            draw.text((W // 2, y), line, font=f_title, fill=(241, 245, 249), anchor="ma")
            y += int(title_size * 1.3)
        draw.line([(W // 2 - 100, y + 26), (W // 2 + 100, y + 26)], fill=accent, width=8)
        draw.text((W // 2, y + 86), beat["text"], font=f_role, fill=(148, 163, 184), anchor="ma")
        img.save(path)
        return

    chip(draw, (MARGIN, 76), "长教程 · 剪辑工作流", f_tag, (30, 41, 59), (226, 232, 240))
    draw.text((W - MARGIN, 88), "EP.01", font=f_tag, fill=(100, 116, 139), anchor="ra")
    draw.text((W - MARGIN, 160), "%02d / %02d" % (index, total), font=f_index, fill=accent, anchor="ra")

    max_width = W - MARGIN * 2 - 180
    lines = []
    for seg in beat["headline"].split("\n"):
        for line in common.wrap_text(draw, seg, f_title, max_width):
            lines.append(line)
    line_h = int(title_size * 1.28)
    block_h = len(lines) * line_h
    y = (H - block_h) // 2 - 20
    for line in lines:
        draw.text((MARGIN, y), line, font=f_title, fill=(248, 250, 252))
        y += line_h
    bar_y = y + 28
    draw.rectangle([MARGIN, bar_y, MARGIN + 140, bar_y + 8], fill=accent)
    draw.text((MARGIN, bar_y + 30), ROLE_LABELS.get(beat["role"], beat["role"]), font=f_role,
              fill=(100, 116, 139))
    img.save(path)


def render_segment(card, duration, out):
    frames = max(2, int(round(duration * 30)))
    zoom = ("zoompan=z='min(zoom+0.0004,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            "d=%d:s=1920x1080:fps=30" % frames)
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(card), "-vf", zoom, "-frames:v", str(frames),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", str(out)])


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    voice = common.load_json(run_dir / "_pipeline" / "voice.json")
    beats = voice["beats"]
    cards_dir = common.ensure_dir(run_dir / "01-素材" / "视频" / "cards")
    seg_dir = common.ensure_dir(run_dir / "_pipeline" / "segments")
    if args.force:
        for d in (cards_dir, seg_dir):
            for f in d.glob("*"):
                if f.is_file():
                    f.unlink()

    lead = float(voice.get("lead_in_s", 0.4))
    segments = []
    for i, beat in enumerate(beats, 1):
        card = cards_dir / ("%02d-%s.png" % (i, beat["id"]))
        accent = ACCENTS.get(beat["role"], ACCENTS["transition"])
        render_card(card, beat, i, len(beats), accent)
        screen = (beats[i]["start"] - beat["start"]) if i < len(beats) else beat["duration"]
        if i == 1:
            screen += lead
        seg = seg_dir / ("%02d.mp4" % i)
        render_segment(card, screen, seg)
        segments.append(str(seg))

    tail = {"headline": "把清单\n用起来", "text": "关注，下一条讲素材整理", "role": "cta"}
    tail_card = cards_dir / "99-tail.png"
    render_card(tail_card, tail, len(beats) + 1, len(beats), ACCENTS["cta"], is_tail=True)
    tail_seg = seg_dir / "99-tail.mp4"
    render_segment(tail_card, voice["tail_s"], tail_seg)
    segments.append(str(tail_seg))

    list_path = run_dir / "_pipeline" / "segments.txt"
    list_path.write_text("".join("file '%s'\n" % s.replace("'", "'\\''") for s in segments), encoding="utf-8")
    base = run_dir / "03-导出" / "preview" / "base.mp4"
    base.parent.mkdir(parents=True, exist_ok=True)
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(list_path),
                "-c", "copy", "-movflags", "+faststart", str(base)])

    cover = run_dir / "05-交付" / "封面.png"
    cover.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cards_dir / ("01-%s.png" % beats[0]["id"]), cover)

    info = common.media_summary(base)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(base), common.repo_rel(cover)],
        "metrics": {"cards": len(beats) + 1, "video": info, "voice_duration_s": voice["total_duration_s"]},
        "note": "横版底片 %ss" % info["duration_s"],
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

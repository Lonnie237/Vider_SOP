#!/usr/bin/env python3
"""D4 数据动画渲染：按 t 逐帧绘制条形竞速 / 折线 / 环图，管道给 ffmpeg。

参考 Moessif/code-video-showcase 的渲染契约：画面是 t 的纯函数；
逐帧渲染 + 帧数校验 + 静帧/接触表 QA。
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

TOP_COLOR = (10, 7, 16)
BOTTOM_COLOR = (20, 10, 26)
ACCENT = (255, 90, 74)
VIOLET = (123, 92, 255)
TEXT = (245, 243, 250)
MUTED = (160, 148, 175)


def parse_args():
    p = argparse.ArgumentParser(description="D4 数据动画渲染")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def hash01(n, seed=1):
    x = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
    x = (x ^ (x >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFFFF) / 0xFFFFFF


def hex_rgb(value, fallback=(255, 255, 255)):
    try:
        value = str(value).lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return fallback


def year_at(t, keyframes):
    if not keyframes:
        return 2019.0
    if t <= keyframes[0]["t"]:
        return float(keyframes[0]["year"])
    if t >= keyframes[-1]["t"]:
        return float(keyframes[-1]["year"])
    for a, b in zip(keyframes, keyframes[1:]):
        if a["t"] <= t <= b["t"]:
            u = (t - a["t"]) / max(1e-6, (b["t"] - a["t"]))
            return lerp(float(a["year"]), float(b["year"]), ease_in_out(u))
    return float(keyframes[-1]["year"])


def values_at(dataset, year):
    years = dataset["years"]
    step = years[1] - years[0] if len(years) > 1 else 1
    pos = (year - years[0]) / step
    i = int(math.floor(pos))
    i = max(0, min(len(years) - 2, i))
    u = clamp(pos - i)
    out = []
    for s in dataset["series"]:
        v0 = float(s["values"][i])
        v1 = float(s["values"][i + 1])
        out.append({"name": s["name"], "color": s.get("color", "#FFFFFF"),
                    "value": lerp(v0, v1, ease_in_out(u))})
    return out


class Renderer:
    def __init__(self, storyboard, dataset):
        self.sb = storyboard
        self.dataset = dataset
        self.W = storyboard["width"]
        self.H = storyboard["height"]
        self.fps = storyboard["fps"]
        self.total = storyboard["duration_s"]
        self.title_end = next(s["end"] for s in storyboard["scenes"] if s["kind"] == "title")
        self.race = next(s for s in storyboard["scenes"] if s["kind"] == "race")
        self.cta = next(s for s in storyboard["scenes"] if s["kind"] == "cta")
        self.keyframes = storyboard["year_keyframes"]
        self.chart = storyboard["chart"]
        self.kind = self.chart.get("kind", "bar-race")
        self.summary = storyboard["summary"]
        self.font_path = common.find_cjk_font()
        self._fonts = {}
        self._bg = self.build_background()
        self._y = {}
        self._max_value = max(max(s["values"]) for s in dataset["series"])

    def font(self, size):
        if size not in self._fonts:
            from PIL import ImageFont
            self._fonts[size] = ImageFont.truetype(self.font_path, size)
        return self._fonts[size]

    def build_background(self):
        from PIL import Image, ImageDraw, ImageFilter
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)
        for y in range(self.H):
            r = y / max(1, self.H - 1)
            color = tuple(int(TOP_COLOR[i] + (BOTTOM_COLOR[i] - TOP_COLOR[i]) * r) for i in range(3))
            draw.line([(0, y), (self.W, y)], fill=color + (255,))
        glow = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([-160, -120, 760, 720], fill=VIOLET + (80,))
        gd.ellipse([self.W - 760, self.H - 620, self.W + 200, self.H + 160], fill=ACCENT + (50,))
        glow = glow.filter(ImageFilter.GaussianBlur(130))
        img = Image.alpha_composite(img, glow)
        grid = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grid)
        for x in range(0, self.W, 96):
            gd.line([(x, 0), (x, self.H)], fill=(255, 255, 255, 10), width=1)
        for y in range(0, self.H, 96):
            gd.line([(0, y), (self.W, y)], fill=(255, 255, 255, 10), width=1)
        img = Image.alpha_composite(img, grid)
        draw = ImageDraw.Draw(img)
        draw.text((96, 54), self.chart["title"], font=self.font(38), fill=TEXT + (255,))
        draw.text((96, 102), self.chart.get("subtitle", ""), font=self.font(24), fill=MUTED + (255,))
        label = "示例数据"
        chip = self.font(22)
        bbox = draw.textbbox((0, 0), label, font=chip)
        cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x0 = self.W - 96 - cw - 40
        draw.rounded_rectangle([x0, 54, self.W - 96, 54 + ch + 24], radius=12,
                               fill=(44, 30, 44, 255), outline=(120, 80, 90, 255), width=1)
        draw.text((x0 + 20, 54 + 12 - bbox[1]), label, font=chip, fill=(255, 190, 170, 255))
        draw.text((96, self.H - 58), self.chart.get("footnote", ""), font=self.font(22), fill=(140, 128, 155, 255))
        return img

    def reset(self):
        self._y = {}

    def draw_particles(self, layer, t):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        for i in range(36):
            px = 80 + hash01(i, 11) * (self.W - 160)
            speed = 6 + hash01(i, 23) * 18
            py = (self.H - (t * speed + hash01(i, 31) * self.H)) % self.H
            r = 1.2 + hash01(i, 41) * 2.4
            alpha = 40 + int(60 * (0.5 + 0.5 * math.sin(t * 1.7 + i)))
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, alpha))

    def draw_title(self, layer, t):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        p = clamp(t / max(0.6, self.title_end))
        alpha = int(255 * ease_out_cubic(p))
        y = 420 - 30 * ease_out_cubic(p)
        headline = self.sb["scenes"][0].get("headline") or "七年，谁在增长"
        draw.text((self.W // 2, y), headline, font=self.font(120), fill=TEXT + (alpha,), anchor="ma")
        draw.rectangle([self.W // 2 - 90, y + 190, self.W // 2 + 90, y + 198], fill=ACCENT + (alpha,))
        draw.text((self.W // 2, y + 240), self.chart.get("subtitle", ""), font=self.font(38),
                  fill=MUTED + (alpha,), anchor="ma")
        draw.text((self.W // 2, y + 310), self.chart.get("footnote", ""), font=self.font(24),
                  fill=(120, 110, 135, alpha), anchor="ma")

    def draw_big_year(self, layer, year):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        draw.text((self.W - 104, 120), str(int(round(year))), font=self.font(100),
                  fill=(255, 255, 255, 34), stroke_width=2, stroke_fill=(255, 255, 255, 36), anchor="ra")

    def draw_insight(self, layer, t, box):
        from PIL import ImageDraw
        start = float(self.race.get("insight_start", self.race["end"]))
        if t < start:
            return
        p = clamp((t - start) / max(0.6, self.race["end"] - start))
        a = int(255 * ease_out_cubic(p))
        lift = 22 * (1 - ease_out_cubic(p))
        draw = ImageDraw.Draw(layer)
        shifted = [box[0], box[1] + lift, box[2], box[3] + lift]
        draw.rounded_rectangle(shifted, radius=18, fill=(255, 255, 255, 14),
                               outline=(255, 255, 255, 45), width=1)
        draw.text((shifted[0] + 30, shifted[1] + 24), "结论", font=self.font(20), fill=ACCENT + (a,))
        draw.text((shifted[0] + 30, shifted[1] + 56), self.chart["insight"].get("text", ""),
                  font=self.font(30), fill=TEXT + (a,))
        draw.text((shifted[0] + 30, shifted[1] + 104), self.chart["insight"].get("sub", ""),
                  font=self.font(20), fill=MUTED + (a,))

    # ---------- 条形竞速 ----------
    def draw_bar_race(self, layer, t, snap=False):
        from PIL import Image, ImageDraw, ImageFilter
        draw = ImageDraw.Draw(layer)
        year = year_at(t, self.keyframes)
        values = values_at(self.dataset, year)
        values.sort(key=lambda x: x["value"], reverse=True)
        top, row_h, bar_h = 260, 72, 38
        label_x, bar_x, bar_max = 110, 470, 1120
        scale = bar_max / max(1e-6, self._max_value)
        self.draw_big_year(layer, year)

        for idx, item in enumerate(values):
            target_y = top + idx * row_h
            if snap or item["name"] not in self._y:
                self._y[item["name"]] = target_y
            else:
                self._y[item["name"]] += (target_y - self._y[item["name"]]) * 0.2
            y = self._y[item["name"]]
            is_top = idx == 0
            accent = (255, 90, 74) if is_top else hex_rgb(item["color"])
            width = max(24, item["value"] * scale)
            draw.rounded_rectangle([label_x - 24, y - 8, self.W - 90, y + 54], radius=10,
                                   fill=(255, 255, 255, 8))
            draw.text((label_x, y + 24), item["name"], font=self.font(30),
                      fill=TEXT + (255,) if is_top else (200, 195, 210, 255), anchor="lm")
            if is_top:
                glow = Image.new("RGBA", (int(width) + 120, 110), (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                gd.rounded_rectangle([60, 30, 60 + width, 70], radius=12, fill=ACCENT + (110,))
                glow = glow.filter(ImageFilter.GaussianBlur(16))
                layer.paste(glow, (int(bar_x) - 60, int(y) - 32), glow)
            draw.rounded_rectangle([bar_x, y, bar_x + width, y + bar_h], radius=12, fill=accent + (255,))
            draw.text((bar_x + width + 16, y + bar_h // 2), "%.1f" % item["value"], font=self.font(28),
                      fill=(255, 255, 255, 240) if is_top else (205, 200, 218, 255), anchor="lm")
            if is_top:
                draw.text((bar_x + width + 16, y + bar_h - 2), self.chart["unit"], font=self.font(16),
                          fill=MUTED + (220,), anchor="lm")
        self.draw_insight(layer, t, [1240, 744, self.W - 96, 896])

    # ---------- 折线 / 面积 ----------
    def draw_line_race(self, layer, t):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        years = self.dataset["years"]
        year = year_at(t, self.keyframes)
        self.draw_big_year(layer, year)
        x0, x1 = 150, self.W - 170
        y0, y1 = 700, 250
        ymax = max(2.0, math.ceil(self._max_value * 1.1 / 2) * 2)
        highlight = self.summary.get("highlight_name") or self.dataset["series"][0]["name"]

        def xy(yr, value):
            ux = (yr - years[0]) / max(1e-6, (years[-1] - years[0]))
            uy = clamp(value / ymax, 0, 1)
            return x0 + ux * (x1 - x0), y0 - uy * (y0 - y1)

        # 网格与刻度
        ticks = list(range(0, int(ymax) + 1, 2))
        for value in ticks:
            _, yy = xy(years[0], value)
            draw.line([(x0, yy), (x1, yy)], fill=(255, 255, 255, 18), width=1)
            draw.text((x0 - 18, yy), "%d" % value, font=self.font(22), fill=MUTED + (220,), anchor="rm")
        for yr in years:
            xx, _ = xy(yr, 0)
            draw.line([(xx, y0), (xx, y0 + 8)], fill=(255, 255, 255, 40), width=1)
            draw.text((xx, y0 + 22), str(yr), font=self.font(22), fill=MUTED + (230,), anchor="ma")

        # 当前年份之前的点
        series_data = []
        for s in self.dataset["series"]:
            pts = []
            for i, yr in enumerate(years):
                if yr > year:
                    break
                pts.append(xy(yr, float(s["values"][i])))
            if pts and year > years[0]:
                idx = min(len(years) - 1, int(math.floor(year - years[0])))
                if idx + 1 < len(years):
                    frac = clamp(year - years[idx])
                    val = lerp(float(s["values"][idx]), float(s["values"][idx + 1]), frac)
                    pts.append(xy(year, val))
            series_data.append((s, pts))

        # 面积（高亮序列）
        for s, pts in series_data:
            if s["name"] != highlight or len(pts) < 2:
                continue
            poly = pts + [(pts[-1][0], y0), (pts[0][0], y0)]
            draw.polygon(poly, fill=ACCENT + (26,))

        # 其他线
        for s, pts in series_data:
            if s["name"] == highlight or len(pts) < 2:
                continue
            draw.line(pts, fill=hex_rgb(s.get("color")) + (150,), width=4, joint="curve")
            draw.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
                         fill=hex_rgb(s.get("color")) + (200,))

        # 高亮线
        for s, pts in series_data:
            if s["name"] != highlight or len(pts) < 2:
                continue
            draw.line(pts, fill=ACCENT + (70,), width=18, joint="curve")
            draw.line(pts, fill=ACCENT + (255,), width=6, joint="curve")
            px, py = pts[-1]
            draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=ACCENT + (255,))
            value = values_at(self.dataset, year)
            current = next((v["value"] for v in value if v["name"] == highlight), 0)
            label = "%.1f" % current
            draw.text((px + 16, py - 26), label, font=self.font(34), fill=TEXT + (255,))
            draw.text((px + 16, py + 6), self.chart["unit"], font=self.font(18), fill=MUTED + (235,))

        # 图例
        legend_x = x0
        for s in self.dataset["series"]:
            color = ACCENT if s["name"] == highlight else hex_rgb(s.get("color"))
            draw.ellipse([legend_x, 178, legend_x + 12, 190], fill=color + (255,))
            draw.text((legend_x + 20, 184), s["name"], font=self.font(20), fill=TEXT + (220,), anchor="lm")
            legend_x += 215
        self.draw_insight(layer, t, [1240, 744, self.W - 96, 896])

    # ---------- 环图 ----------
    def draw_donut(self, layer, t):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        shares = self.summary.get("shares") or []
        total = float(self.summary.get("final_total") or 0)
        highlight = self.summary.get("highlight_name")
        p = clamp((t - self.race["start"]) / max(1.5, (self.race["end"] - self.race["start"]) * 0.6))
        sweep = 360.0 * ease_out_cubic(p)
        cx, cy, outer, width = 660, 500, 270, 88
        box = [cx - outer, cy - outer, cx + outer, cy + outer]
        start = -90.0
        for item in shares:
            share_angle = item["share"] / 100.0 * 360.0
            drawn = clamp(sweep - (start + 90.0), 0, share_angle)
            if drawn > 0:
                color = hex_rgb(item.get("color"))
                if item["name"] == highlight:
                    draw.arc(box, start, start + drawn, fill=ACCENT + (70,), width=width + 14)
                    color = ACCENT
                draw.arc(box, start, start + drawn, fill=color + (235,), width=width)
            start += share_angle
        # 中心
        value_now = total * ease_out_cubic(p)
        draw.text((cx, cy - 24), "%.1f" % value_now, font=self.font(96), fill=TEXT + (255,), anchor="mm")
        draw.text((cx, cy + 58), self.chart["unit"] + " · 2026 年合计", font=self.font(26),
                  fill=MUTED + (240,), anchor="mm")
        # 图例
        lx, ly = 1180, 250
        for item in shares:
            color = ACCENT if item["name"] == highlight else hex_rgb(item.get("color"))
            draw.rounded_rectangle([lx, ly, lx + 18, ly + 18], radius=5, fill=color + (255,))
            draw.text((lx + 30, ly - 2), item["name"], font=self.font(26), fill=TEXT + (230,), anchor="lm")
            draw.text((lx + 300, ly + 8), "%.1f" % item["value"], font=self.font(24),
                      fill=TEXT + (230,), anchor="rm")
            draw.text((lx + 380, ly + 8), "%.1f%%" % item["share"], font=self.font(22),
                      fill=MUTED + (230,), anchor="rm")
            ly += 78
        self.draw_insight(layer, t, [96, 744, 760, 896])

    def draw_cta(self, layer, t):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(layer)
        p = clamp((t - self.cta["start"]) / max(0.8, self.cta["end"] - self.cta["start"]))
        a = int(255 * ease_out_cubic(p))
        draw.text((self.W // 2, 390), "数据是示例", font=self.font(96), fill=TEXT + (a,), anchor="ma")
        draw.text((self.W // 2, 510), "方法是可复用的", font=self.font(96), fill=(255, 160, 140, a), anchor="ma")
        draw.rectangle([self.W // 2 - 90, 650, self.W // 2 + 90, 658], fill=ACCENT + (a,))
        draw.text((self.W // 2, 720), "下一条：怎么找到可信的真实数据", font=self.font(34),
                  fill=MUTED + (a,), anchor="ma")
        draw.text((self.W // 2, 790), self.chart.get("footnote", ""), font=self.font(22),
                  fill=(110, 100, 125, a), anchor="ma")

    def draw_frame(self, t, snap=False):
        from PIL import Image
        layer = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.draw_particles(layer, t)
        if t < self.title_end:
            self.draw_title(layer, t)
        elif t < self.cta["start"]:
            if self.kind == "line":
                self.draw_line_race(layer, t)
            elif self.kind == "donut":
                self.draw_donut(layer, t)
            else:
                self.draw_bar_race(layer, t, snap=snap)
        else:
            self.draw_cta(layer, t)
        img = Image.alpha_composite(self._bg.copy(), layer)
        return img.convert("RGB")


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    sb = common.load_json(run_dir / "_pipeline" / "storyboard.json")
    data = common.load_json(run_dir / "_pipeline" / "data.json")
    renderer = Renderer(sb, data["dataset"])
    fps = renderer.fps
    frames = int(round(renderer.total * fps))
    out_dir = common.ensure_dir(run_dir / "03-导出" / "preview")
    base = out_dir / "base.mp4"
    stills_dir = common.ensure_dir(run_dir / "_pipeline" / "stills")

    still_times = [0.5, renderer.title_end + 0.6, (renderer.race["start"] + renderer.race["end"]) / 2,
                   float(renderer.race.get("insight_start", renderer.race["end"])) + 0.8,
                   renderer.cta["start"] + 0.8]
    still_paths = []
    renderer.reset()
    for i, st in enumerate(still_times, 1):
        img = renderer.draw_frame(min(st, renderer.total - 0.05), snap=True)
        p = stills_dir / ("still-%02d-%04.1fs.png" % (i, st))
        img.save(p)
        still_paths.append(str(p))

    renderer.reset()
    cover = renderer.draw_frame(min(0.9, renderer.total - 0.05), snap=True)
    cover_path = run_dir / "05-交付" / "封面.png"
    cover_path.parent.mkdir(parents=True, exist_ok=True)
    cover.save(cover_path)

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (renderer.W, renderer.H), "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(base)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            img = renderer.draw_frame(i / fps)
            proc.stdin.write(img.tobytes())
            if i % 120 == 0:
                proc.stdin.flush()
        proc.stdin.close()
        stderr = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
        if code != 0:
            raise common.StageError("ffmpeg 编码失败（exit %d）：%s" % (code, stderr[-800:]))
    except BrokenPipeError:
        raise common.StageError("ffmpeg 管道断开：%s" % proc.stderr.read().decode("utf-8", "replace")[-800:])

    info = common.media_summary(base)
    probe = common.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(base)])
    actual_frames = int(probe.stdout.strip() or 0)
    if actual_frames != frames:
        raise common.StageError("帧数不符：期望 %d，实际 %d" % (frames, actual_frames))

    contact = run_dir / "_pipeline" / "contact-sheet.jpg"
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(base),
                "-vf", "fps=1,scale=240:-1,tile=8x6:padding=4:margin=4",
                "-frames:v", "1", str(contact)])

    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(base), common.repo_rel(cover_path), common.repo_rel(contact)] + [
            common.repo_rel(Path(p)) for p in still_paths],
        "metrics": {"frames": frames, "fps": fps, "duration_s": info["duration_s"],
                    "video": info, "stills": len(still_paths), "chart": renderer.kind},
        "note": "%d 帧 / %.1fs，%s 逐帧渲染完成" % (frames, info["duration_s"], renderer.kind),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
#!/usr/bin/env python3
"""Claude-styled statusline for Claude Code.

Line 1: model pill, directory, git branch
Line 2: gradient context meter, session cost, 5h/7d rate limits, reset time
"""
import json
import os
import subprocess
import sys
from datetime import datetime


def fg(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[38;2;{r};{g};{b}m"


def bg(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[48;2;{r};{g};{b}m"


ORANGE = "#D97757"
IVORY = "#E8E6DC"
GRAY = "#8A8578"
MUTED = "#6B675C"
DIM = "#4A463C"
GREEN = "#7D9B76"
RED = "#C15F3C"
INK = "#1F1E1B"
RESET = "\033[0m"
SEP = f"  {fg(DIM)}│{RESET}  "


def severity(pct):
    return fg(GREEN) if pct < 60 else fg(ORANGE) if pct < 85 else fg(RED)


def meter(pct, cells=10):
    # filled cells shade green -> orange -> red as the bar grows
    filled = min(cells, round(pct / 100 * cells))
    out = []
    for i in range(cells):
        if i < filled:
            zone = (i + 1) / cells * 100
            out.append(f"{severity(zone)}▰")
        else:
            out.append(f"{fg(DIM)}▱")
    return "".join(out) + RESET


def fmt_tokens(n):
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{s}M"
    if n >= 1_000:
        return f"{round(n / 1_000)}k"
    return str(n)


def short_path(path, home):
    if path.startswith(home):
        path = "~" + path[len(home):]
    parts = path.split("/")
    if len(parts) > 4:
        path = "…/" + "/".join(parts[-3:])
    return path


def main():
    d = json.load(sys.stdin)

    model = (d.get("model") or {}).get("display_name") or "Claude"
    cwd = (d.get("workspace") or {}).get("current_dir") or d.get("cwd") or ""
    ctx = d.get("context_window") or {}
    cost = (d.get("cost") or {}).get("total_cost_usd")
    limits = d.get("rate_limits") or {}

    # --- line 1: model pill · dir · branch --------------------------------
    pill = (
        f"{fg(ORANGE)}{RESET}"
        f"{bg(ORANGE)}{fg(INK)}✻ {model}{RESET}"
        f"{fg(ORANGE)}{RESET}"
    )
    line1 = [pill]
    if cwd:
        line1.append(f"{fg(IVORY)} {short_path(cwd, os.path.expanduser('~'))}{RESET}")
    try:
        branch = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=1,
        ).stdout.strip()
    except Exception:
        branch = ""
    if branch:
        line1.append(f"{fg(GRAY)} {branch}{RESET}")
    print(" " + "  ".join(line1))

    # --- line 2: context meter · cost · rate limits · reset ---------------
    parts = []

    size = ctx.get("context_window_size") or 200_000
    used = (ctx.get("total_input_tokens") or 0) + (ctx.get("total_output_tokens") or 0)
    pct = ctx.get("used_percentage")
    if pct is None:
        pct = used * 100.0 / size
    parts.append(
        f"{meter(pct)} {severity(pct)}{pct:.0f}%{RESET} "
        f"{fg(MUTED)}{fmt_tokens(used)} / {fmt_tokens(size)}{RESET}"
    )

    if cost is not None:
        parts.append(f"{fg(GRAY)}{RESET} {fg(IVORY)}${cost:.2f}{RESET}")

    five = limits.get("five_hour") or {}
    seven = limits.get("seven_day") or {}
    rl = []
    if five.get("used_percentage") is not None:
        p = five["used_percentage"]
        rl.append(f"{fg(MUTED)}5h{RESET} {severity(p)}{p:.0f}%{RESET}")
    if seven.get("used_percentage") is not None:
        p = seven["used_percentage"]
        rl.append(f"{fg(MUTED)}7d{RESET} {severity(p)}{p:.0f}%{RESET}")
    if rl:
        parts.append(f"{fg(GRAY)}{RESET} " + f" {fg(DIM)}·{RESET} ".join(rl))

    resets_at = five.get("resets_at")
    if resets_at:
        dt = datetime.fromtimestamp(resets_at)
        when = dt.strftime("%-I:%M %p") if dt.date() == datetime.now().date() \
            else dt.strftime("%a %-I:%M %p")
        parts.append(f"{fg(GRAY)}{RESET} {fg(GRAY)}{when}{RESET}")

    print(" " + SEP.join(parts))


if __name__ == "__main__":
    main()

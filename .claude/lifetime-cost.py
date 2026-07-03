#!/usr/bin/env python3
"""Estimate lifetime Claude Code spend from local transcripts.

Sums token usage across ~/.claude/projects/**/*.jsonl and prices it with
current per-MTok rates (cache writes at 1.25x input, cache reads at 0.1x input).
Prints a compact formatted total (e.g. "$12.34", "$1.2k"). This is an estimate,
not a billing figure.
"""
import glob
import json
import os
import sys

# (input_per_mtok, output_per_mtok). Matched by longest key that is a
# substring of the transcript's model id.
PRICES = {
    "claude-fable-5": (10.0, 50.0),
    "claude-mythos-5": (10.0, 50.0),
    "claude-opus-4": (5.0, 25.0),      # 4.8 / 4.7 / 4.6 / 4.5 / 4.1 / 4.0
    "claude-opus": (15.0, 75.0),       # opus 3 (legacy)
    "claude-sonnet-5": (3.0, 15.0),
    "claude-sonnet-4": (3.0, 15.0),
    "claude-sonnet": (3.0, 15.0),
    "claude-haiku-4": (1.0, 5.0),
    "claude-haiku": (1.0, 5.0),        # haiku 3.5 / 3
    "claude-3-opus": (15.0, 75.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-sonnet": (3.0, 15.0),
    "claude-3-5-haiku": (1.0, 5.0),
    "claude-3-haiku": (0.25, 1.25),
}
DEFAULT_PRICE = (5.0, 25.0)  # unknown model -> assume Opus-tier


def price_for(model):
    if not model:
        return DEFAULT_PRICE
    best = None
    for key, price in PRICES.items():
        if key in model and (best is None or len(key) > len(best[0])):
            best = (key, price)
    return best[1] if best else DEFAULT_PRICE


def fmt(total):
    if total >= 1000:
        return f"${total / 1000:.1f}k".replace(".0k", "k")
    if total >= 100:
        return f"${total:.0f}"
    return f"${total:.2f}"


def main():
    root = os.path.expanduser("~/.claude/projects")
    total = 0.0
    for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or '"usage"' not in line:
                        continue
                    try:
                        obj = json.loads(line)
                    except ValueError:
                        continue
                    msg = obj.get("message")
                    if not isinstance(msg, dict):
                        continue
                    usage = msg.get("usage")
                    if not isinstance(usage, dict):
                        continue
                    inp, out = price_for(msg.get("model"))
                    ntok_in = usage.get("input_tokens", 0) or 0
                    ntok_out = usage.get("output_tokens", 0) or 0
                    ntok_cw = usage.get("cache_creation_input_tokens", 0) or 0
                    ntok_cr = usage.get("cache_read_input_tokens", 0) or 0
                    total += (
                        ntok_in * inp
                        + ntok_cw * inp * 1.25
                        + ntok_cr * inp * 0.10
                        + ntok_out * out
                    ) / 1_000_000
        except OSError:
            continue
    sys.stdout.write(fmt(total))


if __name__ == "__main__":
    main()

#!/bin/bash
# Claude Code status line: renders via oh-my-posh's `claude` subcommand, and
# injects an estimated lifetime spend as POSH_LIFETIME_COST for the theme.
#
# The lifetime figure is cached with a TTL; when stale it refreshes in the
# background so the status line never blocks on transcript parsing.

CONFIG="$HOME/.claude/claude-omp.json"
CALC="$HOME/.claude/lifetime-cost.py"
CACHE="$HOME/.claude/.lifetime-cost"
TTL=300  # seconds

# Read Claude Code's JSON payload from stdin once; oh-my-posh needs it too.
INPUT="$(cat)"

now=$(date +%s)
mtime=0
[ -f "$CACHE" ] && mtime=$(stat -f %m "$CACHE" 2>/dev/null || echo 0)

if [ ! -s "$CACHE" ]; then
    # No cache yet: compute once synchronously so the segment appears.
    python3 "$CALC" > "$CACHE" 2>/dev/null
elif [ $((now - mtime)) -ge "$TTL" ]; then
    # Stale: use the old value now, refresh in the background for next time.
    touch "$CACHE"  # debounce so parallel renders don't all spawn a refresh
    ( python3 "$CALC" > "$CACHE.tmp" 2>/dev/null && mv "$CACHE.tmp" "$CACHE" ) &
fi

POSH_LIFETIME_COST="$(cat "$CACHE" 2>/dev/null)"
export POSH_LIFETIME_COST

printf '%s' "$INPUT" | oh-my-posh claude --config "$CONFIG"

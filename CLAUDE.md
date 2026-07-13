# Repository Guide

The tracked repository holds configuration for OpenCode, a local CLI proxy, and Claude Code status lines. It has no tracked package manifests, install scripts, repository-provided build or test commands, README, or contributing guide.

Work from the repository root. Inspect the files that exist, validate only what has a supported local check, and avoid inventing setup or startup steps.

## Inspect The Configuration

```sh
git status --short
sed -n '1,240p' opencode.json
sed -n '1,200p' cliproxyapi.conf
```

Begin with `git status --short` so you can preserve unrelated work. Read the configuration before changing it. Several paths referenced by `opencode.json` are currently missing:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/guidelines.md`
- `.cursor/rules/*.md`

Treat these as unresolved references. Do not describe them as available project guidance.

Run the checks supported by the files in this repository:

```sh
python3 -m json.tool .claude/claude-statusline.omp.json >/dev/null
python3 -m py_compile .claude/statusline.py .claude/lifetime-cost.py
bash -n .claude/statusline-command.sh
```

Do not validate `opencode.json` with `python3 -m json.tool`. The file uses JSONC-like syntax, including trailing commas, despite its `.json` extension.

There is no repository command for validating `opencode.json`. OpenCode itself loads the configuration when it starts and rejects invalid configuration. After changing `opencode.json`, quit and restart OpenCode. Use the current schema at <https://opencode.ai/config.json> when checking field names and shapes.

## OpenCode Configuration

```sh
sed -n '1,240p' opencode.json
```

`opencode.json` is the project OpenCode configuration. It declares the published OpenCode schema and currently configures:

- `zsh` as the shell.
- A local provider named `cli`.
- `http://localhost:8317/v1` as the `cli` provider base URL.
- The `opencode-goal-plugin` plugin.
- A `goal` command using the `build` agent.
- A remote `context7` MCP server at `https://mcp.context7.com/mcp/oauth`.

Keep the `$schema` declaration when editing this file. Preserve fields outside the requested change. Confirm uncertain options against the current official schema, then restart OpenCode to load the result.

## CLI Proxy Configuration

```sh
sed -n '1,200p' cliproxyapi.conf
```

`cliproxyapi.conf` is the CLI proxy configuration. It sets the proxy port to `8317`, matching the port used by the local `cli` provider in `opencode.json`.

This repository does not contain a command or script for starting the proxy. Keep documentation limited to the configuration that can be inspected here.

## Claude Status Lines

```sh
bash -n .claude/statusline-command.sh
python3 -m py_compile .claude/statusline.py .claude/lifetime-cost.py
python3 -m json.tool .claude/claude-statusline.omp.json >/dev/null
```

`.claude/statusline-command.sh` accepts Claude Code JSON and feeds it to `oh-my-posh`. It also invokes `.claude/lifetime-cost.py` through paths under `$HOME/.claude`.

These are repository files. There is no installer here, and nothing in this repository proves they are copied into `$HOME/.claude` automatically. Keep repository paths and home-directory paths distinct when changing or documenting the script.

`.claude/statusline.py` is a separate Python status line implementation. Check it independently rather than assuming it follows the shell wrapper.

## Lifetime Cost Estimate

```sh
python3 .claude/lifetime-cost.py
```

`.claude/lifetime-cost.py` scans `~/.claude/projects/**/*.jsonl` and prints an estimated lifetime total. Describe the output as an estimate. It is not a billing statement or an authoritative account balance.

## House Rules

### Design

Write simple, boring units that do one job.

Inject dependencies rather than hiding them behind global state or implicit construction. Prefer composition when behavior needs to be combined. Add an abstraction only when the current change requires it. Do not build speculative extension points for possible future work.

### Names And Comments

Names must carry meaning. Choose names that explain the role, value, or behavior without requiring a nearby comment.

Use comments only to explain constraints, tradeoffs, or why a decision exists. Do not use comments to restate what the code already says.

### Pull Requests

Keep each pull request small and focused on one purpose.

When work is blocked or contains multiple concerns, sequence it into separate pull requests. State the required ordering so reviewers know which change must land first.

### Sources

Trust current official documentation over memory. Configuration formats, tool behavior, and supported options can change.

When searching the web for technical guidance, include `2026` in the search query. Verify the result against the current official documentation before applying it.

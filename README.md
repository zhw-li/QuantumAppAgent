<div align="center">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/logo-dark.svg">
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/logo-light.svg">
      <img alt="TYQA Logo" src="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/logo-dark.svg" width="80%">
    </picture>
</div>

<div align="center">
<a href="https://github.com/zhw-li/QuantumAppAgent/blob/main/LICENSE"><picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/badge-license-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/badge-license-dark.svg">
  <img alt="License Apache 2.0" src="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/badge-license-light.svg" height="28">
</picture></a>
</div>

---

<div align="center">
<a href="https://github.com/zhw-li/QuantumAppAgent"><img src="https://readme-typing-svg.demolab.com?font=Sans-Serif&pause=1000&color=64B5F6&center=true&vCenter=true&width=435&lines=TianYan+Quantum+Agent;Quantum+Applications%2C+End+to+End" alt="Typing SVG" /></a>
</div>

<div align="center">

**English | [简体中文](./README.zh-CN.md)**

</div>

**TYQA (TianYan Quantum Agent, 天衍量智) is a self-evolving multi-agent framework for building validated quantum applications and TianYan quantum-cloud showcases end to end.
It combines planning, research, coding, debugging, analysis, and delivery agents with the [cqlib](https://github.com/cqlib-quantum/cqlib) quantum SDK, so a project can move from business or research intent to classical baselines, quantum methods, backend APIs, QCCP showcase pages, and verification evidence in one reviewable workflow.**

> [!NOTE]
> The canonical repository is **`zhw-li/QuantumAppAgent`**. The Python package name, install target, and primary CLI command are lowercase **`tyqa`**; uppercase `TYQA` is kept for display and as a compatibility CLI alias.

## ✨ Features
- **🤖 Multi-Agent Team** — 6 sub-agents (plan, research, code, debug, analyze, write) working in concert.
- **⚛️ Quantum Algorithm Stack** — `cqlib-sdk` routes to QAOA, VQE, quantum ML, and hybrid quantum-classical pipelines.
- **☁️ TianYan Cloud Integration** — generate `qccp-web` SFC showcase pages, backend APIs, and deployment artifacts in one pass.
- **🔬 Six-Phase Quantum Workflow** — Intake → baseline → quantum method → app packaging → verification → write-up.
- **🧠 Self-Evolving Memory** — User profile and observations auto-distilled each turn, growing across sessions.
- **🌐 Multi-Provider** — Anthropic, OpenAI, Google, MiniMax, NVIDIA — one config to switch.
- **📱 Multi-Channel** — CLI as the hub; Telegram, Slack, Feishu, WeChat, and more — one agent session.
- **🖥️ Desktop WebUI** — Workspace-panel web app, one terminal via `--ui webui`.
- **🔄 Code Generation Modes** — More Effort (iterative refinement), continuously improving code quality.
- **⚡ Adaptive Tools & Context** — Per-turn tool selection and dynamic system-prompt rewriting keep only what's relevant.
- **🔌 MCP & Skills** — Plug in MCP servers or install skills from GitHub on the fly.

## 🧪 Quantum Application Examples

Legacy quantum application demos live under [`quantum_app_example/`](./quantum_app_example). They are useful reference artifacts for classical baselines, quantum methods, verification reports, and TianYan-cloud showcase pages, but they predate the current `application_manifest.json` validator contract and should not be treated as current release-compliant application packages until manifests are added.

| Example | Quantum method | Classical baseline | Primary metric |
| --- | --- | --- | --- |
| [`Finance_QAOA`](./quantum_app_example/Finance_QAOA) | QAOA portfolio selection | Markowitz mean-variance + brute force | `cost_gap_percent` |
| [`MaxCut_QAOA`](./quantum_app_example/MaxCut_QAOA) | QAOA graph partitioning | brute-force enumeration | `cost_gap_percent` |
| [`UC_QAOA`](./quantum_app_example/UC_QAOA) | QAOA unit commitment (power systems) | brute-force search | `optimality_gap_percent` |
| [`H2_VQE`](./quantum_app_example/H2_VQE) | VQE H₂ ground-state energy | exact diagonalization | energy error vs chemical accuracy (1.6 mHa) |
| [`Finance_QRC`](./quantum_app_example/Finance_QRC) | Quantum reservoir computing (stock prediction) | Echo State Network | RMSE |

## 🏗️ Framework Architecture

TYQA drives every project through a staged quantum-application lifecycle, composing the right skills at each phase:

```
solution-landscape / evidence-navigator   ←  methods, datasets, baselines, prior results
        │
application-intake / delivery-planning  ←  application framing, validation & artifact plan
        │
   application-pipeline               ←  stage-gated execution (baseline → quantum → app → verify)
        │
cqlib-sdk → cqlib-qaoa / cqlib-vqe   ←  quantum algorithm + quantum_report.json
          / cqlib-qml / cqlib-hybrid
        │
qccp-ui → qccp-frontend /     ←  cloud showcase UI + API/service + deploy evidence
                 qccp-service  ←  FastAPI app service by default; Java qccp-service integration when explicit
        │
delivery-writing / delivery-review /       ←  report, README, INTEGRATE notes, slides
showcase-slides
```

Not every project needs every phase — the starting point matches what you already have. The stage gates and skill-routing rules live in [`tyqa/skills/application-pipeline/SKILL.md`](./tyqa/skills/application-pipeline/SKILL.md); the built-in quantum-algorithm skills are documented under [`tyqa/skills/`](./tyqa/skills).

### Skill Name Migration

The built-in lifecycle skills were renamed from research-writing names to quantum-application delivery names. There are no compatibility aliases; update local references to the new IDs.

| Old skill ID | New skill ID |
| --- | --- |
| `research-ideation` | `application-intake` |
| `paper-navigator` | `evidence-navigator` |
| `research-survey` | `solution-landscape` |
| `paper-planning` | `delivery-planning` |
| `experiment-pipeline` | `application-pipeline` |
| `experiment-craft` | `application-debugging` |
| `experiment-iterative-coder` | `implementation-iteration` |
| `paper-writing` | `delivery-writing` |
| `paper-review` | `delivery-review` |
| `paper-rebuttal` | `stakeholder-response` |
| `academic-slides` | `showcase-slides` |
| `evo-memory` | `application-memory` |

## 📖 Table of Contents

- [📦 Installation](#-installation)
- [🔑 Configuration](#-configuration)
- [⚡ Quick Start](#-quick-start)
- [🍪 Examples & Recipes](#-examples--recipes)
- [🔌 MCP Integration](#-mcp-integration)
- [📱 Channels](#-channels)
- [🎯 Roadmap](#-ᯓ-roadmap)
- [🤝 Contributing](#-contributing)
- [📚 Acknowledgments](#-acknowledgments)

## 📦 Installation

> [!IMPORTANT]
> Requires **Python 3.11 or 3.12** (`>=3.11,<3.13`). The reliable installation path today is **source checkout + editable install**. Do not rely on PyPI, `uv tool install`, or a pre-built Docker image until release artifacts are published and verified.

### Recommended: source checkout + conda

```bash
git clone https://github.com/zhw-li/QuantumAppAgent.git
cd QuantumAppAgent

conda create -n tyqa python=3.11 -y
conda activate tyqa

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

If you already have the repository checkout, start from `cd QuantumAppAgent`.

### Alternative: standard venv

```bash
git clone https://github.com/zhw-li/QuantumAppAgent.git
cd QuantumAppAgent

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### Verify the install

```bash
python -m pytest tests/test_skill_descriptions.py -q
tyqa -h
```

For broader local validation:

```bash
python -m pytest tests/test_prompts.py tests/test_skill_descriptions.py tests/test_quantum_application_validation.py -q
```

### Update an existing source checkout

```bash
git pull
conda activate tyqa
python -m pip install -e ".[dev]"
```

### Optional channel dependencies

Messaging channel integrations require extra dependencies. Install only what you need from the source checkout:

```bash
python -m pip install -e ".[telegram]"     # Telegram
python -m pip install -e ".[discord]"      # Discord
python -m pip install -e ".[slack]"        # Slack
python -m pip install -e ".[wechat]"       # WeChat
python -m pip install -e ".[qq]"           # QQ
python -m pip install -e ".[feishu]"       # Feishu
python -m pip install -e ".[all-channels]" # everything
```

### 🐳 Docker

There is currently **no published, user-ready TYQA Docker image**. The Dockerfile is kept for local packaging checks and controlled deployments. Build the image from this checkout when you need a containerized run:

```bash
docker build -t tyqa:local .
```

Then run the locally built image:

```bash
docker run -it --rm \
  --env-file .env \
  -v "$(pwd)/workspace:/workspace" \
  -v tyqa-data:/home/tyqa/.tyqa \
  tyqa:local
```

What the mounts are for:

| Mount | Purpose |
| --- | --- |
| `--env-file .env` | API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, …) |
| `./workspace:/workspace` | The agent's working directory |
| `tyqa-data:/home/tyqa/.tyqa` | Persistent app state: sessions DB, global skills, memories, and `config.yaml`/`mcp.yaml` |

> [!IMPORTANT]
> The image runs as a non-root user (`tyqa`, UID `1000`). For the `./workspace` bind mount, the host directory must be writable by that UID. If your host user ID differs, either `chown -R 1000:1000 ./workspace` once, or pass `--user "$(id -u):$(id -g)"` on every `docker run` so the container takes on your UID.
>
> The **iMessage** channel is not usable from the container because it needs the `imsg` CLI to communicate with macOS Messages.app. Run TYQA directly on macOS if you need iMessage.

Or use `docker compose` after building from the local Dockerfile:

```bash
docker compose build
docker compose run --rm tyqa
```

> [!NOTE]
> Optional extras are not bundled in the local image. Add them only when needed:
> - **`stt`** (speech-to-text via `faster-whisper`) and **`oauth`** (`ccproxy-api`)
> - **TinyTeX / LaTeX** (`pdflatex`, `latexmk`) for delivery-writing skills
>
> Prefer adding Python extras directly in the project Dockerfile's `uv sync` step so the image is built from the same source checkout. For LaTeX, install a pinned TinyTeX or system TeX package in a derived image only when delivery-writing workflows require it.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🔑 Configuration

The easiest way to configure API keys is the interactive wizard:

```bash
tyqa onboard
```

> [!TIP]
> It walks you through provider selection, key validation, model choice, and workspace mode.
> Supports OAuth sign-in for CLI coding agent subscribers — no API key needed.

![onboard](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_onboard.png)

<details>
<summary> 📟 Manual configuration via environment variables </summary>

Set at least one LLM provider key and (optionally) a search key:

```bash
# Pick one LLM provider
export ANTHROPIC_API_KEY="sk-..."   # Claude  — console.anthropic.com
export OPENAI_API_KEY="sk-..."      # GPT    — platform.openai.com
export GOOGLE_API_KEY="AI..."       # Gemini  — aistudio.google.com/api-keys
export MINIMAX_API_KEY="sk-..."     # MiniMax — platform.minimaxi.com (China, default) or platform.minimax.io (Global)
export MINIMAX_BASE_URL="https://api.minimax.io/anthropic"  # only needed for Global keys (default: https://api.minimaxi.com/anthropic)
export NVIDIA_API_KEY="nvapi-..."   # NIM    — build.nvidia.com

# Web search (optional)
export TAVILY_API_KEY="tvly-..."    # app.tavily.com
```

Or use `tyqa config set` to persist keys in `~/.config/tyqa/config.yaml`.

Alternatively, copy the example `.env` file for project-level configuration:

```bash
cp .env.example .env  # then fill in your keys
```

> ⚠️ Never commit `.env` files with real keys. It is already in `.gitignore`.

</details>

<p align="right"><a href="#top">🔝Back to top</a></p>

## ⚡ Quick Start

```bash
tyqa  # or TYQA — interactive mode (TUI by default)
```

![demo](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_cli.png)

> Run `tyqa -h` for all CLI options.

![cli help](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_cli_help.png)

> [!TIP]
> Prefer a browser? Run `tyqa --ui webui` for the web workspace UI. Need to copy long outputs? Use `--ui cli` for classic mode where native terminal copy works freely. On macOS, [iTerm2](https://iterm2.com/) users can also hold `⌥ Option` while dragging to select, then `⌘+C`.

<details>
<summary>Common examples</summary>

```bash
tyqa                            # interactive mode (TUI by default)
tyqa -p "your question"        # single-shot mode
tyqa --workdir /path/to/project # open in a specific directory
tyqa -m run                     # isolated per-session workspace
tyqa --ui cli                   # classic CLI (lightweight)
tyqa --ui webui                 # browser workspace UI (needs Node/npx)
tyqa serve                      # headless mode — channels only, no interactive prompt
tyqa deploy                     # standalone LangGraph server for external UIs / SDK clients
```

</details>

<details>
<summary>Desktop WebUI</summary>

Set the UI backend to `webui` and a fresh `tyqa` session launches a deploy-style LangGraph server **and** the [`@evoscientist/webui`](https://www.npmjs.com/package/@evoscientist/webui) front-end in one terminal — no second process to manage:

```bash
tyqa config set ui_backend webui   # persist; or one-off with `tyqa --ui webui`
tyqa                               # opens http://localhost:4716
tyqa config set webui_port 4800    # change the front-end port (must differ from the langgraph dev port)
```

Requires **Node.js 24 LTS** (for `npx`); the first launch downloads `@evoscientist/webui` and needs network. Note: the WebUI does not show your CLI/TUI chat history, and `-p` / `--resume` fall back to the classic CLI.

</details>

<details>
<summary>Action Approval</summary>

By default, shell commands (`execute` tool) require human approval before running. To skip approval prompts:

```bash
# Per-session: auto-approve via CLI flag
tyqa --auto-approve
tyqa -p "query" --auto-approve

# Persistent: set in config (applies to all future sessions)
tyqa config set auto_approve true

# Or allow only specific command prefixes
tyqa config set shell_allow_list "python,pip,pytest,ruff,git"
```

During a session you can also reply **3** (Approve all) at any approval prompt to auto-approve for the rest of that session.

> [!CAUTION]
> **Dangerous mode** lifts the workspace sandbox entirely — the agent can read, write, and delete files **anywhere on the real filesystem** (privileged commands like `sudo`/`rm -rf /` are still blocked). It implies `--auto-approve` (no prompts). Use only when you fully trust the task.
>
> ```bash
> tyqa --dangerous                       # per-session
> tyqa config set dangerous_mode true    # persistent
> ```

</details>

<details>
<summary>Agent Questions</summary>

The agent can proactively ask you questions when it needs clarification (e.g., dataset choice, experiment direction). This is enabled by default. To disable:

```bash
# Persistent: set in config
tyqa config set enable_ask_user false

# Re-enable
tyqa config set enable_ask_user true
```

</details>

<details>
<summary>In-session commands</summary>

| Command | Description |
| ------- | ----------- |
| `/current` | Show current session info |
| `/threads` | List recent sessions |
| `/resume` | Resume a previous session |
| `/delete` | Delete a saved session |
| `/new` | Start a new session |
| `/clear` | Clear chat history |
| `/skills` | List installed skills |
| `/install-skill <src>` | Add a skill from path or GitHub |
| `/uninstall-skill <name>` | Remove an installed skill |
| `/mcp` | Manage MCP servers |
| `/channel` | Configure messaging channels |
| `/help` | Show available commands |
| `/exit` | Quit |

</details>

<details>
<summary>Script Inference</summary>

```python
from tyqa import tyqa_agent
from langchain_core.messages import HumanMessage
from tyqa.utils import format_messages

thread = {"configurable": {"thread_id": "1"}}
last_len = 0

for state in tyqa_agent.stream(
    {"messages": [HumanMessage(content="Hi?")]},
    config=thread,
    stream_mode="values",
):
    msgs = state["messages"]
    if len(msgs) > last_len:
        format_messages(msgs[last_len:])
        last_len = len(msgs)
```

</details>

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🍪 Examples & Recipes

- **Quantum applications** — see [`quantum_app_example/`](./quantum_app_example) for the five end-to-end QAOA / VQE / QRC showcases above.
- **Other examples & recipes** — a curated collection of usage patterns and deployment recipes: 👉 [browse all](https://github.com/zhw-li/QuantumAppAgent/tree/main/docs#-examples--recipes)

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🔌 MCP Integration

Add external tools via [MCP](https://modelcontextprotocol.io/) servers with a single command:

```bash
# Usage
tyqa mcp add <name> <command> [-- args...]

# Example
tyqa mcp add sequential-thinking npx -- -y @modelcontextprotocol/server-sequential-thinking
```

> [!TIP]
> For command options, config fields, tool routing, wildcard filtering, and troubleshooting, see the **[MCP Integration Guide](https://github.com/zhw-li/QuantumAppAgent/tree/main/tyqa/mcp#model-context-protocol-integration)**.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 📱 Channels

Connect messaging platforms so they share the same agent session as the CLI:

```bash
# Usage
tyqa channel setup <channel>

# Example
tyqa channel setup telegram
```

Multiple channels can run concurrently — comma-separate names in the config:

```yaml
channel_enabled: "telegram,slack,feishu,qq"
```

The channel can also be started interactively with `/channel` in the CLI session.

> [!TIP]
> For per-channel setup guides, capability matrix, architecture details, and troubleshooting, see the **[Channel Integration Guide](https://github.com/zhw-li/QuantumAppAgent/tree/main/tyqa/channels#channels)**.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🎯 ᯓ➤ Roadmap

Done:
- [x] 🖥️ Full-screen TUI and classic CLI interfaces
- [x] ⚛️ cqlib quantum-algorithm skill stack (QAOA / VQE / QML / hybrid)
- [x] ☁️ TianYan cloud showcase generation (qccp-web SFC + backend service)
- [x] 🔬 Six-phase quantum-application pipeline with stage gates
- [x] 🧪 Five end-to-end quantum application examples
- [x] 🧠 Self-evolving memory across sessions
- [x] 👋 Human-on-the-loop action approval & agent-initiated clarification
- [x] 📺 Desktop WebUI with workspace panels

Coming next:
- [ ] 🏷️ Finish release cleanup after the `tyqa` migration (compatibility aliases, config migration, published artifacts)
- [ ] ⚙️ Real quantum-hardware backends (beyond the cqlib simulator)
- [ ] 🧩 More quantum application examples across domains
- [ ] 📊 Benchmark suite for quantum-application workflows
- [ ] 📹 Demo and tutorial

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🤝 Contributing

We welcome contributions from developers, researchers, and AI coding agents. Our [Contributing Guidelines](./CONTRIBUTING.md) cover architecture, patterns, extension guides, and code standards to help you contribute safely and effectively.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 📚 Acknowledgments

TYQA is built on outstanding open-source works:

- [**EvoScientist**](https://arxiv.org/abs/2603.08127) — The original self-evolving multi-agent AI scientist framework that inspired and seeded this project.
- [**cqlib**](https://github.com/cqlib-quantum/cqlib) — The quantum SDK powering the algorithm layer (circuits, simulators, QCIS).
- [**LangChain**](https://github.com/langchain-ai/langchain) / [**DeepAgents**](https://github.com/langchain-ai/deepagents) / [**LangGraph**](https://github.com/langchain-ai/langgraph) — The agent framework stack.

We thank the authors for their valuable contributions to the open-source community.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

<p align="right"><a href="#top">🔝Back to top</a></p>

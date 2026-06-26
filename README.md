<div align="center">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/logo-dark.svg">
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/logo-light.svg">
      <img alt="TYQA Logo" src="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/logo-dark.svg" width="80%">
    </picture>
</div>

<div align="center">
<a href="https://github.com/EvoScientist/EvoScientist/blob/main/LICENSE"><picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/badge-license-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/badge-license-dark.svg">
  <img alt="License Apache 2.0" src="https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/badge-license-light.svg" height="28">
</picture></a>
</div>

---

<div align="center">
<a href="https://github.com/zhw-li/TYQA"><img src="https://readme-typing-svg.demolab.com?font=Sans-Serif&pause=1000&color=64B5F6&center=true&vCenter=true&width=435&lines=TianYan+Quantum+Agent;Quantum+Applications%2C+End+to+End" alt="Typing SVG" /></a>
</div>

<div align="center">

**English | [简体中文](./README.zh-CN.md)**

</div>

**TYQA (TianYan Quantum Agent, 天衍量智) is a self-evolving agent framework that moves a research question from idea to a validated quantum application and cloud showcase — end to end.
Built on the [EvoScientist](https://github.com/EvoScientist/EvoScientist) agent harness and the [cqlib](https://github.com/cqlib-quantum/cqlib) quantum SDK, it orchestrates specialized sub-agents to survey methods, establish classical baselines, build the quantum algorithm, package a runnable application, generate the TianYan (天衍) quantum-cloud showcase UI, and verify the evidence — growing its skills and memory across cycles.**

> [!NOTE]
> The project is rebranding to **tyqa**. For now the Python package name, the `EvoSci` / `evosci` CLI commands, and the `~/.config/evoscientist/` config path still use the upstream `EvoScientist` identifiers and remain fully functional. The full stack rename (package, CLI, config directory, env vars) is tracked as a follow-up.

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

Ready-to-run quantum applications live under [`quantum_app_example/`](./quantum_app_example). Each ships with a classical baseline, a quantum method, a verification report, and a TianYan-cloud SFC showcase page.

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
research-survey / paper-navigator   ←  methods, datasets, baselines, prior results
        │
research-ideation / paper-planning  ←  application framing, validation & artifact plan
        │
   experiment-pipeline               ←  stage-gated execution (baseline → quantum → app → verify)
        │
cqlib-sdk → cqlib-qaoa / cqlib-vqe   ←  quantum algorithm + quantum_report.json
          / cqlib-qml / cqlib-hybrid
        │
qccp-ui → qccp-frontend /     ←  cloud showcase UI + API/service + deploy evidence
                 qccp-service  ←  FastAPI app service by default; Java qccp-service integration when explicit
        │
paper-writing / paper-review /       ←  report, README, INTEGRATE notes, slides
academic-slides
```

Not every project needs every phase — the starting point matches what you already have. The stage gates and skill-routing rules live in [`EvoScientist/skills/experiment-pipeline/SKILL.md`](./EvoScientist/skills/experiment-pipeline/SKILL.md); the built-in quantum-algorithm skills are documented under [`EvoScientist/skills/`](./EvoScientist/skills).

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

> [!TIP]
> Requires **Python 3.11+** (**< 3.14**). We recommend [**uv**](https://docs.astral.sh/uv/) or **conda** for dependency management and virtual environments. Prefer to skip a local Python install entirely? Jump to [🐳 Docker](#-docker).

<details>
<summary> 🪛 Install uv (if you don't have it)</summary>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

### Quick Install

```bash
uv tool install EvoScientist
```

> [!NOTE]
> To update an existing installation to the latest version, use `uv tool upgrade`:
> ```bash
> uv tool upgrade EvoScientist
> ```

Or install into the current environment instead:

```bash
uv pip install EvoScientist
```

### Latest from GitHub

To get the latest patches before a [PyPI](https://pypi.org/project/EvoScientist/) release:

```bash
uv pip install git+https://github.com/EvoScientist/EvoScientist.git
```

### Development Install

```bash
git clone https://github.com/EvoScientist/EvoScientist.git
cd EvoScientist
uv sync --dev
```

enable pre-commit hooks:
```bash
uv run pre-commit install
```

<details>
<summary> Using conda</summary>

```bash
conda create -n EvoSci python=3.11 -y
conda activate EvoSci
pip install -e ".[dev]"
```

</details>

<details>
<summary> Using PyPi</summary>

```bash
pip install EvoScientist          # quick install
pip install -e ".[dev]"           # development install
```

</details>

<details>
<summary> Optional: Channel dependencies</summary>

Messaging channel integrations require extra dependencies. Install only what you need:

```bash
uv pip install "EvoScientist[telegram]"     # Telegram
uv pip install "EvoScientist[discord]"      # Discord
uv pip install "EvoScientist[slack]"        # Slack
uv pip install "EvoScientist[wechat]"       # WeChat
uv pip install "EvoScientist[qq]"           # QQ
uv pip install "EvoScientist[feishu]"       # Feishu
uv pip install "EvoScientist[all-channels]" # everything
```

</details>

<details>
<summary> Upgrade to the latest code base </summary>

```bash
git pull && uv sync --dev
```

</details>

### 🐳 Docker

A pre-built image is published to [GitHub Container Registry](https://github.com/EvoScientist/EvoScientist/pkgs/container/evoscientist) with everything `evosci onboard` would otherwise install for you:

- Python 3.11, EvoScientist, and the cross-platform messaging channels (i.e., `EvoScientist[all-channels]`)
- **`uv`** — used by the MCP registry to install Python MCP servers on demand
- **Node.js 24 LTS + `npx`** — required by the majority of MCP servers

The **iMessage** channel isn't usable from the container — it requires the `imsg` CLI talking to macOS's Messages.app, which is host-OS-specific. Run the agent directly on macOS if you need iMessage.

Running the agent in a container also **sandboxes the agent's shell access** — file edits and shell commands stay confined to volumes you explicitly mount.

```bash
docker run -it --rm \
  --env-file .env \
  -v "$(pwd)/workspace:/workspace" \
  -v evosci-data:/home/evosci/.evoscientist \
  ghcr.io/evoscientist/evoscientist:latest
```

What the mounts are for:

| Mount | Purpose |
| --- | --- |
| `--env-file .env` | API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, …) |
| `./workspace:/workspace` | The agent's working directory |
| `evosci-data:/home/evosci/.evoscientist` | Persistent app state: sessions DB, global skills, memories, and `config.yaml`/`mcp.yaml` |

> [!IMPORTANT]
> The image runs as a non-root user (`evosci`, UID `1000`). For the `./workspace` bind mount, the host directory must be writable by that UID. If your host user ID differs, either `chown -R 1000:1000 ./workspace` once, or pass `--user "$(id -u):$(id -g)"` on every `docker run` so the container takes on your UID.

Or use `docker compose` (a starter [`docker-compose.yml`](./docker-compose.yml) is included):

```bash
docker compose run --rm evoscientist
```

To build the image locally instead of pulling:

```bash
docker build -t evoscientist:dev .
```

> [!NOTE]
> Not bundled — install on demand by deriving from the image:
> - **`stt`** (speech-to-text via `faster-whisper`) and **`oauth`** (`ccproxy-api`)
> - **TinyTeX / LaTeX** (`pdflatex`, `latexmk`) for paper-writing skills
>
> ```dockerfile
> FROM ghcr.io/evoscientist/evoscientist:latest
>
> # Python extras
> USER root
> RUN uv pip install --python /opt/venv/bin/python "EvoScientist[stt,oauth]"
> USER evosci
>
> # TinyTeX
> # The official install method is `curl | sh`; if you'd rather not
> # pipe an unpinned remote script into a shell, fetch a specific TinyTeX
> # release tarball from https://github.com/rstudio/tinytex-releases, verify
> # its checksum, and extract to /home/evosci/.TinyTeX instead.
> RUN curl -sL https://yihui.org/tinytex/install-bin-unix.sh | sh \
>  && /home/evosci/.TinyTeX/bin/*/tlmgr install latexmk
> ```

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🔑 Configuration

The easiest way to configure API keys is the interactive wizard:

```bash
EvoSci onboard
```

> [!TIP]
> It walks you through provider selection, key validation, model choice, and workspace mode.
> Supports OAuth sign-in for CLI coding agent subscribers — no API key needed.

![onboard](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_onboard.png)

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

Or use `EvoSci config set` to persist keys in `~/.config/evoscientist/config.yaml`.

Alternatively, copy the example `.env` file for project-level configuration:

```bash
cp .env.example .env  # then fill in your keys
```

> ⚠️ Never commit `.env` files with real keys. It is already in `.gitignore`.

</details>

<p align="right"><a href="#top">🔝Back to top</a></p>

## ⚡ Quick Start

```bash
EvoSci  # or EvoScientist — interactive mode (TUI by default)
```

![demo](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_cli.png)

> Run `EvoSci -h` for all CLI options.

![cli help](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_cli_help.png)

> [!TIP]
> Prefer a browser? Run `EvoSci --ui webui` for the web workspace UI. Need to copy long outputs? Use `--ui cli` for classic mode where native terminal copy works freely. On macOS, [iTerm2](https://iterm2.com/) users can also hold `⌥ Option` while dragging to select, then `⌘+C`.

<details>
<summary>Common examples</summary>

```bash
EvoSci                            # interactive mode (TUI by default)
EvoSci -p "your question"        # single-shot mode
EvoSci --workdir /path/to/project # open in a specific directory
EvoSci -m run                     # isolated per-session workspace
EvoSci --ui cli                   # classic CLI (lightweight)
EvoSci --ui webui                 # browser workspace UI (needs Node/npx)
EvoSci serve                      # headless mode — channels only, no interactive prompt
EvoSci deploy                     # standalone LangGraph server for external UIs / SDK clients
```

</details>

<details>
<summary>Desktop WebUI</summary>

Set the UI backend to `webui` and a fresh `EvoSci` session launches a deploy-style LangGraph server **and** the [`@evoscientist/webui`](https://www.npmjs.com/package/@evoscientist/webui) front-end in one terminal — no second process to manage:

```bash
EvoSci config set ui_backend webui   # persist; or one-off with `EvoSci --ui webui`
EvoSci                               # opens http://localhost:4716
EvoSci config set webui_port 4800    # change the front-end port (must differ from the langgraph dev port)
```

Requires **Node.js 24 LTS** (for `npx`); the first launch downloads `@evoscientist/webui` and needs network. Note: the WebUI does not show your CLI/TUI chat history, and `-p` / `--resume` fall back to the classic CLI.

</details>

<details>
<summary>Action Approval</summary>

By default, shell commands (`execute` tool) require human approval before running. To skip approval prompts:

```bash
# Per-session: auto-approve via CLI flag
EvoSci --auto-approve
EvoSci -p "query" --auto-approve

# Persistent: set in config (applies to all future sessions)
EvoSci config set auto_approve true

# Or allow only specific command prefixes
EvoSci config set shell_allow_list "python,pip,pytest,ruff,git"
```

During a session you can also reply **3** (Approve all) at any approval prompt to auto-approve for the rest of that session.

> [!CAUTION]
> **Dangerous mode** lifts the workspace sandbox entirely — the agent can read, write, and delete files **anywhere on the real filesystem** (privileged commands like `sudo`/`rm -rf /` are still blocked). It implies `--auto-approve` (no prompts). Use only when you fully trust the task.
>
> ```bash
> EvoSci --dangerous                       # per-session
> EvoSci config set dangerous_mode true    # persistent
> ```

</details>

<details>
<summary>Agent Questions</summary>

The agent can proactively ask you questions when it needs clarification (e.g., dataset choice, experiment direction). This is enabled by default. To disable:

```bash
# Persistent: set in config
EvoSci config set enable_ask_user false

# Re-enable
EvoSci config set enable_ask_user true
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
from EvoScientist import EvoScientist_agent
from langchain_core.messages import HumanMessage
from EvoScientist.utils import format_messages

thread = {"configurable": {"thread_id": "1"}}
last_len = 0

for state in EvoScientist_agent.stream(
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
- **Other examples & recipes** — a curated collection of usage patterns and deployment recipes: 👉 [browse all](https://github.com/EvoScientist/EvoScientist/tree/main/docs#-examples--recipes)

<p align="right"><a href="#top">🔝Back to top</a></p>

## 🔌 MCP Integration

Add external tools via [MCP](https://modelcontextprotocol.io/) servers with a single command:

```bash
# Usage
EvoSci mcp add <name> <command> [-- args...]

# Example
EvoSci mcp add sequential-thinking npx -- -y @modelcontextprotocol/server-sequential-thinking
```

> [!TIP]
> For command options, config fields, tool routing, wildcard filtering, and troubleshooting, see the **[MCP Integration Guide](https://github.com/EvoScientist/EvoScientist/tree/main/EvoScientist/mcp#model-context-protocol-integration)**.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 📱 Channels

Connect messaging platforms so they share the same agent session as the CLI:

```bash
# Usage
EvoSci channel setup <channel>

# Example
EvoSci channel setup telegram
```

Multiple channels can run concurrently — comma-separate names in the config:

```yaml
channel_enabled: "telegram,slack,feishu,qq"
```

The channel can also be started interactively with `/channel` in the CLI session.

> [!TIP]
> For per-channel setup guides, capability matrix, architecture details, and troubleshooting, see the **[Channel Integration Guide](https://github.com/EvoScientist/EvoScientist/tree/main/EvoScientist/channels#channels)**.

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
- [ ] 🏷️ Full-stack rename to `tyqa` (package, CLI, config directory, env vars)
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

- [**EvoScientist**](https://github.com/EvoScientist/EvoScientist) — The self-evolving multi-agent harness this project extends.
- [**cqlib**](https://github.com/cqlib-quantum/cqlib) — The quantum SDK powering the algorithm layer (circuits, simulators, QCIS).
- [**LangChain**](https://github.com/langchain-ai/langchain) / [**DeepAgents**](https://github.com/langchain-ai/deepagents) / [**LangGraph**](https://github.com/langchain-ai/langgraph) — The agent framework stack.

We thank the authors for their valuable contributions to the open-source community.

<p align="right"><a href="#top">🔝Back to top</a></p>

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

<p align="right"><a href="#top">🔝Back to top</a></p>

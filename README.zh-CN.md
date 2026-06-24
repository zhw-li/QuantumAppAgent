 > [!WARNING]
 > 这是社区翻译版本，欢迎修正！

---

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

**[English](./README.md) | 简体中文**

</div>

**TYQA（TianYan Quantum Agent，天衍量智）是一个自进化智能体框架，把一个研究问题从想法推进到可验证的量子应用与云端展示——端到端覆盖全流程。
它基于 [EvoScientist](https://github.com/EvoScientist/EvoScientist) 智能体框架与 [cqlib](https://github.com/cqlib-quantum/cqlib) 量子 SDK 构建，编排多个专职子智能体完成：调研方法、建立经典基线、构建量子算法、打包可运行应用、生成天衍（TianYan）量子云展示界面，并验证证据——在每一轮中持续进化自身的技能与记忆。**

> [!NOTE]
> 本项目正在更名为 **tyqa**。目前 Python 包名、`EvoSci` / `evosci` CLI 命令以及 `~/.config/evoscientist/` 配置路径仍沿用上游 `EvoScientist` 的标识，且功能完全正常。全栈改名（包名、CLI、配置目录、环境变量）将作为后续版本推进。

## ✨ 特性

- **🤖 多智能体协作** — 6 个子智能体（规划、调研、编码、调试、分析、写作）协同工作。
- **⚛️ 量子算法栈** — `cqlib-sdk` 路由到 QAOA、VQE、量子机器学习与混合量子-经典流程。
- **☁️ 天衍云集成** — 一键生成 `qccp-web` SFC 展示页面、后端 API 与部署产物。
- **🔬 六阶段量子工作流** — 需求采集 → 基线 → 量子方法 → 应用打包 → 验证 → 撰写。
- **🧠 自进化记忆** — 用户画像与观察记录每轮自动提炼，跨会话持续进化。
- **🌐 多模型供应商** — Anthropic、OpenAI、Google、MiniMax、NVIDIA——一处配置，随时切换。
- **📱 多渠道接入** — CLI 为中心；Telegram、Slack、飞书、微信等——共享同一智能体会话。
- **🖥️ Desktop WebUI** — 单终端 `--ui webui` 启动带工作区面板的 Web 应用。
- **🔄 代码生成模式** — More Effort（迭代精修），持续迭代提升代码生成质量。
- **⚡ 自适应工具与上下文** — 每轮智能筛选工具、动态改写系统提示词，只保留相关内容。
- **🔌 MCP 与 Skills** — 即插即用 MCP 服务器，或从 GitHub 一键安装技能包。

## 🧪 量子应用示例

开箱即用的量子应用位于 [`quantum_app_example/`](./quantum_app_example)。每个示例都包含经典基线、量子方法、验证报告以及天衍云 SFC 展示页面。

| 示例 | 量子方法 | 经典基线 | 主要指标 |
| --- | --- | --- | --- |
| [`Finance_QAOA`](./quantum_app_example/Finance_QAOA) | QAOA 组合投资优化 | Markowitz 均值-方差 + 暴力搜索 | `cost_gap_percent` |
| [`MaxCut_QAOA`](./quantum_app_example/MaxCut_QAOA) | QAOA 图划分 | 暴力枚举 | `cost_gap_percent` |
| [`UC_QAOA`](./quantum_app_example/UC_QAOA) | QAOA 机组调度（电力系统） | 暴力搜索 | `optimality_gap_percent` |
| [`H2_VQE`](./quantum_app_example/H2_VQE) | VQE 氢分子基态能量 | 精确对角化 | 能量误差 vs 化学精度（1.6 mHa） |
| [`Finance_QRC`](./quantum_app_example/Finance_QRC) | 量子储层计算（股票预测） | Echo State Network | RMSE |

## 🏗️ 框架架构

TYQA 通过分阶段的量子应用生命周期驱动每个项目，在各阶段编排相应的技能：

```
research-survey / paper-navigator   ←  方法、数据集、基线、已有结果
        │
research-ideation / paper-planning  ←  应用定位、验证与产物计划
        │
   experiment-pipeline               ←  阶段门禁执行（基线 → 量子 → 应用 → 验证）
        │
cqlib-sdk → cqlib-qaoa / cqlib-vqe   ←  量子算法 + quantum_report.json
          / cqlib-qml / cqlib-hybrid
        │
ui-design-spec → qccp-frontend /     ←  云展示 UI + API/服务 + 部署证据
                 qccp-service
        │
paper-writing / paper-review /       ←  报告、README、INTEGRATE 说明、幻灯片
academic-slides
```

并非每个项目都需要走完全部阶段——起点取决于你已有的内容。阶段门禁与技能路由规则详见 [`skills/experiment-pipeline/SKILL.md`](./skills/experiment-pipeline/SKILL.md)；量子算法技能文档位于 [`skills/`](./skills)。

## 📖 目录

- [📦 安装](#-安装)
- [🔑 配置](#-配置)
- [⚡ 快速上手](#-快速上手)
- [🍪 示例与实践](#-示例与实践)
- [🔌 MCP 集成](#-mcp-集成)
- [📱 渠道接入](#-渠道接入)
- [🎯 路线图](#-ᯓ-路线图)
- [🤝 贡献](#-贡献)
- [📚 致谢](#-致谢)

## 📦 安装

> [!TIP]
> 需要 **Python 3.11+**（**< 3.14**）。推荐使用 [**uv**](https://docs.astral.sh/uv/) 或 **conda** 进行依赖管理和虚拟环境管理。想完全跳过本地 Python 安装？直接跳转到 [🐳 Docker](#-docker)。

<details>
<summary>🪛 安装 uv（如果尚未安装）</summary>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

### 快速安装

```bash
uv tool install EvoScientist
```

> [!NOTE]
> 更新已安装的版本到最新，请使用 `uv tool upgrade`：
> ```bash
> uv tool upgrade EvoScientist
> ```

或安装到当前环境：

```bash
uv pip install EvoScientist
```

### 从 GitHub 安装最新版本

获取 [PyPI](https://pypi.org/project/EvoScientist/) 发布前的最新补丁：

```bash
uv pip install git+https://github.com/EvoScientist/EvoScientist.git
```

### 开发安装

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
<summary> 使用 conda</summary>

```bash
conda create -n EvoSci python=3.11 -y
conda activate EvoSci
pip install -e ".[dev]"
```

</details>

<details>
<summary> 使用 PyPi</summary>

```bash
pip install EvoScientist          # quick install
pip install -e ".[dev]"           # development install
```

</details>

<details>
<summary> 可选：渠道依赖</summary>

消息渠道集成需要额外依赖，按需安装即可：

```bash
uv pip install "EvoScientist[telegram]"     # Telegram
uv pip install "EvoScientist[discord]"      # Discord
uv pip install "EvoScientist[slack]"        # Slack
uv pip install "EvoScientist[wechat]"       # 微信
uv pip install "EvoScientist[qq]"           # QQ
uv pip install "EvoScientist[feishu]"       # 飞书
uv pip install "EvoScientist[all-channels]" # 全部
```

</details>

<details>
<summary> 升级到最新代码库</summary>

```bash
git pull && uv sync --dev
```

</details>

### 🐳 Docker

我们在 [GitHub Container Registry](https://github.com/EvoScientist/EvoScientist/pkgs/container/evoscientist) 上发布了一份预构建镜像，已经包含 `evosci onboard` 通常会为你安装的所有内容：

- Python 3.11、EvoScientist 以及全部跨平台消息渠道（即 `EvoScientist[all-channels]`）
- **`uv`** —— 用于 MCP 注册表按需安装 Python 类 MCP 服务器
- **Node.js 24 LTS + `npx`** —— 大多数 MCP 服务器依赖此运行时

容器中**无法使用 iMessage 渠道**——它需要 `imsg` CLI 与 macOS 的 Messages.app 通信，仅限宿主操作系统。如需 iMessage，请直接在 macOS 上运行。

在容器中运行还会**沙箱化智能体的 Shell 访问**——文件编辑和 Shell 命令仅限于你显式挂载的卷。

```bash
docker run -it --rm \
  --env-file .env \
  -v "$(pwd)/workspace:/workspace" \
  -v evosci-data:/home/evosci/.evoscientist \
  ghcr.io/evoscientist/evoscientist:latest
```

各挂载的用途：

| 挂载 | 用途 |
| --- | --- |
| `--env-file .env` | API 密钥（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY` 等） |
| `./workspace:/workspace` | 智能体的工作目录 |
| `evosci-data:/home/evosci/.evoscientist` | 持久化应用状态：会话数据库、全局技能、记忆，以及 `config.yaml` / `mcp.yaml` |

> [!IMPORTANT]
> 镜像以非 root 用户运行（`evosci`，UID `1000`）。`./workspace` bind 挂载的宿主目录必须可被该 UID 写入。如果你的宿主用户 ID 不同，可以一次性 `chown -R 1000:1000 ./workspace`，或在每次 `docker run` 时加上 `--user "$(id -u):$(id -g)"`，让容器使用你的 UID。

也可使用 `docker compose`（仓库自带一个起步用的 [`docker-compose.yml`](./docker-compose.yml)）：

```bash
docker compose run --rm evoscientist
```

如果想本地构建而不是拉取镜像：

```bash
docker build -t evoscientist:dev .
```

> [!NOTE]
> 镜像中**未捆绑**以下内容，需要时基于镜像派生安装：
> - **`stt`**（基于 `faster-whisper` 的语音转文字）和 **`oauth`**（`ccproxy-api`）
> - **TinyTeX / LaTeX**（`pdflatex`、`latexmk`），供论文写作类技能使用
>
> ```dockerfile
> FROM ghcr.io/evoscientist/evoscientist:latest
>
> # Python 额外组件
> USER root
> RUN uv pip install --python /opt/venv/bin/python "EvoScientist[stt,oauth]"
> USER evosci
>
> # TinyTeX
> # 官方安装方式是 `curl | sh`；如果你不想把未固定版本的远程脚本
> # 直接管入 shell，可以从 https://github.com/rstudio/tinytex-releases
> # 下载特定版本的 TinyTeX 发布包，校验校验和后解压到
> # /home/evosci/.TinyTeX。
> RUN curl -sL https://yihui.org/tinytex/install-bin-unix.sh | sh \
>  && /home/evosci/.TinyTeX/bin/*/tlmgr install latexmk
> ```

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🔑 配置

最简单的方式是使用交互式配置向导：

```bash
EvoSci onboard
```

> [!TIP]
> 向导将引导你完成供应商选择、密钥验证、模型选择和工作区模式设置。
> 支持 CLI 编程智能体订阅用户通过 OAuth 直连——无需 API Key。

![onboard](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_onboard.png)

<details>
<summary> 📟 通过环境变量手动配置</summary>

至少设置一个 LLM 供应商密钥，搜索密钥为可选项：

```bash
# 选择一个 LLM 供应商
export ANTHROPIC_API_KEY="sk-..."   # Claude  — console.anthropic.com
export OPENAI_API_KEY="sk-..."      # GPT    — platform.openai.com
export GOOGLE_API_KEY="AI..."       # Gemini  — aistudio.google.com/api-keys
export MINIMAX_API_KEY="sk-..."     # MiniMax — platform.minimaxi.com（默认，中国大陆）或 platform.minimax.io（国际版）
export MINIMAX_BASE_URL="https://api.minimax.io/anthropic"  # 仅国际版需要设置（默认: https://api.minimaxi.com/anthropic）
export NVIDIA_API_KEY="nvapi-..."   # NIM    — build.nvidia.com

# 网络搜索（可选）
export TAVILY_API_KEY="tvly-..."    # app.tavily.com
```

也可以使用 `EvoSci config set` 将密钥持久化到 `~/.config/evoscientist/config.yaml`。

或者复制示例 `.env` 文件用于项目级配置：

```bash
cp .env.example .env  # 填入你的密钥
```

> ⚠️ 切勿将包含真实密钥的 `.env` 文件提交到版本库。该文件已在 `.gitignore` 中。

</details>

<p align="right"><a href="#top">🔝回到顶部</a></p>

## ⚡ 快速上手

```bash
EvoSci  # 或 EvoScientist — 交互模式（默认 TUI）
```

![demo](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_cli.png)

> 运行 `EvoSci -h` 查看全部 CLI 选项。

![cli help](https://raw.githubusercontent.com/EvoScientist/EvoScientist/main/.github/assets/EvoScientist_cli_help.png)

> [!TIP]
> 想用浏览器？运行 `EvoSci --ui webui` 打开 Web 工作区界面。需要复制长输出？使用 `--ui cli` 切换到经典模式，即可使用终端原生复制。macOS [iTerm2](https://iterm2.com/) 用户也可以按住 `⌥ Option` 拖选文字，再 `⌘+C` 复制。

<details>
<summary>常用示例</summary>

```bash
EvoSci                            # 交互模式（默认 TUI）
EvoSci -p "你的问题"              # 单次查询模式
EvoSci --workdir /path/to/project # 在指定目录下启动
EvoSci -m run                     # 隔离的会话级工作区
EvoSci --ui cli                   # 经典 CLI（轻量）
EvoSci --ui webui                 # 浏览器工作区界面（需 Node/npx）
EvoSci serve                      # 无头模式——仅渠道，无交互提示符
EvoSci deploy                     # 独立 LangGraph 服务器——供外部 UI / SDK 客户端使用
```

</details>

<details>
<summary>Desktop WebUI</summary>

将 UI 后端设为 `webui`，全新的 `EvoSci` 会话便会在单个终端里同时启动 deploy 式 LangGraph 服务器**和** [`@evoscientist/webui`](https://www.npmjs.com/package/@evoscientist/webui) 前端，无需管理第二个进程：

```bash
EvoSci config set ui_backend webui   # 持久化；或用 `EvoSci --ui webui` 临时启用
EvoSci                               # 打开 http://localhost:4716
EvoSci config set webui_port 4800    # 修改前端端口（须与 langgraph dev 端口不同）
```

需要 **Node.js 24 LTS**（提供 `npx`）；首次启动会下载 `@evoscientist/webui`，需要联网。注意：WebUI 不会显示 CLI/TUI 的历史会话，且 `-p` / `--resume` 会回退到经典 CLI。

</details>

<details>
<summary>操作审批</summary>

默认情况下，Shell 命令（`execute` 工具）执行前需要人工审批。跳过审批提示的方式：

```bash
# 单次会话：通过 CLI 参数启用自动审批
EvoSci --auto-approve
EvoSci -p "query" --auto-approve

# 持久化：写入配置（对所有后续会话生效）
EvoSci config set auto_approve true

# 或仅放行特定命令前缀
EvoSci config set shell_allow_list "python,pip,pytest,ruff,git"
```

会话中也可以在审批提示时回复 **3**（Approve all），仅对当次会话自动审批后续所有操作。

> [!CAUTION]
> **危险模式（Dangerous mode）** 会完全解除工作区沙箱——智能体可以读写、删除**真实文件系统上任意位置**的文件（`sudo`/`rm -rf /` 等高危命令仍被拦截）。它隐含 `--auto-approve`（不再提示审批）。请仅在你完全信任该任务时使用。
>
> ```bash
> EvoSci --dangerous                       # 单次会话
> EvoSci config set dangerous_mode true    # 持久化
> ```

</details>

<details>
<summary>智能体提问</summary>

智能体可以在需要澄清时主动向你提问（例如数据集选择、实验方向等）。此功能默认开启。关闭方式：

```bash
# 持久化：写入配置
EvoSci config set enable_ask_user false

# 重新开启
EvoSci config set enable_ask_user true
```

</details>

<details>
<summary>会话内命令</summary>

| 命令 | 说明 |
| ---- | ---- |
| `/current` | 显示当前会话信息 |
| `/threads` | 列出最近的会话 |
| `/resume` | 恢复之前的会话 |
| `/delete` | 删除已保存的会话 |
| `/new` | 开始新会话 |
| `/clear` | 清除聊天记录 |
| `/skills` | 列出已安装的技能包 |
| `/install-skill <src>` | 从本地路径或 GitHub 安装技能包 |
| `/uninstall-skill <name>` | 卸载已安装的技能包 |
| `/mcp` | 管理 MCP 服务器 |
| `/channel` | 配置消息渠道 |
| `/help` | 显示可用命令 |
| `/exit` | 退出 |

</details>

<details>
<summary>脚本调用</summary>

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

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🍪 示例与实践

- **量子应用** — 见 [`quantum_app_example/`](./quantum_app_example)，包含上文 5 个端到端的 QAOA / VQE / QRC 展示示例。
- **其他示例与实践** — 官方示例、进阶用法和部署配方合集：👉 [浏览全部 →](docs/README.md)

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🔌 MCP 集成

通过 [MCP](https://modelcontextprotocol.io/) 服务器一条命令即可添加外部工具：

```bash
# 用法
EvoSci mcp add <name> <command> [-- args...]

# 示例
EvoSci mcp add sequential-thinking npx -- -y @modelcontextprotocol/server-sequential-thinking
```

> [!TIP]
> 关于命令选项、配置字段、工具路由、通配符过滤和故障排查，请参阅 **[MCP 集成指南](https://github.com/EvoScientist/EvoScientist/tree/main/EvoScientist/mcp#model-context-protocol-integration)**。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 📱 渠道接入

连接消息平台，使其与 CLI 共享同一智能体会话：

```bash
# 用法
EvoSci channel setup <channel>

# 示例
EvoSci channel setup telegram
```

多个渠道可同时运行——在配置中用逗号分隔：

```yaml
channel_enabled: "telegram,slack,feishu,qq"
```

也可以在 CLI 会话中通过 `/channel` 交互式启动渠道。

> [!TIP]
> 关于各渠道设置指南、功能矩阵、架构详情和故障排查，请参阅 **[渠道集成指南](https://github.com/EvoScientist/EvoScientist/tree/main/EvoScientist/channels#channels)**。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🎯 ᯓ➤ 路线图

已完成：
- [x] 🖥️ 全屏 TUI 和经典 CLI 双界面
- [x] ⚛️ cqlib 量子算法技能栈（QAOA / VQE / QML / 混合）
- [x] ☁️ 天衍云展示生成（qccp-web SFC + 后端服务）
- [x] 🔬 带阶段门禁的六阶段量子应用流水线
- [x] 🧪 五个端到端量子应用示例
- [x] 🧠 跨会话自进化记忆
- [x] 👋 Human-on-the-loop 操作审批与智能体主动澄清
- [x] 📺 带工作区面板的桌面 WebUI

下一步：
- [ ] 🏷️ 全栈更名为 `tyqa`（包名、CLI、配置目录、环境变量）
- [ ] ⚙️ 接入真实量子硬件后端（超越 cqlib 模拟器）
- [ ] 🧩 跨领域的更多量子应用示例
- [ ] 📊 量子应用工作流基准测试套件
- [ ] 📹 Demo 与教程

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🤝 贡献

我们欢迎各层次的开发者、研究者以及 AI 编程助手参与贡献。我们的 [贡献指南](./CONTRIBUTING.md) 涵盖架构说明、设计模式、扩展指南和代码规范，帮助你安全高效地参与项目开发。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 📚 致谢

TYQA 基于以下优秀的开源项目构建：

- [**EvoScientist**](https://github.com/EvoScientist/EvoScientist) — 本项目所扩展的自进化多智能体框架。
- [**cqlib**](https://github.com/cqlib-quantum/cqlib) — 驱动算法层的量子 SDK（电路、模拟器、QCIS）。
- [**LangChain**](https://github.com/langchain-ai/langchain) / [**DeepAgents**](https://github.com/langchain-ai/deepagents) / [**LangGraph**](https://github.com/langchain-ai/langgraph) — 智能体框架技术栈。

感谢以上项目作者对开源社区的宝贵贡献。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 📜 许可证

本项目基于 Apache License 2.0 开源——详情请见 [LICENSE](./LICENSE) 文件。

<p align="right"><a href="#top">🔝回到顶部</a></p>

<div align="center">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/logo-dark.svg">
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/logo-light.svg">
      <img alt="TYQA Logo" src=".github/assets/TYQA.png" width="80%">
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

**[English](./README.md) | 简体中文**

</div>

**TYQA（TianYan Quantum Agent，天衍量智）是面向量子应用交付的自进化多智能体框架，用于端到端构建可验证的量子应用与天衍量子云展示。
它将规划、调研、编码、调试、分析和交付智能体与 [cqlib](https://github.com/cqlib-quantum/cqlib) 量子 SDK 结合，把业务或科研需求推进为经典基线、量子方法、后端 API、QCCP 展示页面和验证证据，形成可复核的一体化交付流程。**

> [!NOTE]
> canonical 仓库为 **`zhw-li/QuantumAppAgent`**。Python 包名、安装目标和主 CLI 命令仍为小写 **`tyqa`**；大写 `TYQA` 仅作为展示名和兼容 CLI alias 保留。

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

历史量子应用 demo 位于 [`quantum_app_example/`](./quantum_app_example)。这些示例可作为经典基线、量子方法、验证报告和天衍云展示页面的参考产物，但它们早于当前 `application_manifest.json` validator 合同；在补齐 manifest 前，不应视为符合当前发布框架的应用包。

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
solution-landscape / evidence-navigator   ←  方法、数据集、基线、已有结果
        │
application-intake / delivery-planning  ←  应用定位、验证与产物计划
        │
   application-pipeline               ←  阶段门禁执行（基线 → 量子 → 应用 → 验证）
        │
cqlib-sdk → cqlib-qaoa / cqlib-vqe   ←  量子算法 + quantum_report.json
          / cqlib-qml / cqlib-hybrid
        │
qccp-ui → qccp-frontend /     ←  云展示 UI + API/服务 + 部署证据
                 qccp-service  ←  默认 FastAPI 应用服务；明确 Java 集成时走 qccp-service Java 路径
        │
delivery-writing / delivery-review /       ←  报告、README、INTEGRATE 说明、幻灯片
showcase-slides
```

并非每个项目都需要走完全部阶段——起点取决于你已有的内容。阶段门禁与技能路由规则详见 [`tyqa/skills/application-pipeline/SKILL.md`](./tyqa/skills/application-pipeline/SKILL.md)；内置量子算法技能文档位于 [`tyqa/skills/`](./tyqa/skills)。

### Skill

内置生命周期 skill。

| skill ID |
| --- |
| `application-intake` |
| `evidence-navigator` |
| `solution-landscape` |
| `delivery-planning` |
| `application-pipeline` |
| `application-debugging` |
| `implementation-iteration` |
| `delivery-writing` |
| `delivery-review` |
| `stakeholder-response` |
| `showcase-slides` |
| `application-memory` |

## 📖 目录

- [✨ 特性](#-特性)
- [🧪 量子应用示例](#-量子应用示例)
- [🏗️ 框架架构](#️-框架架构)
  - [Skill](#skill)
- [📖 目录](#-目录)
- [📦 安装](#-安装)
  - [推荐方式：源码 checkout + conda](#推荐方式源码-checkout--conda)
  - [备选方式：标准 venv](#备选方式标准-venv)
  - [验证安装](#验证安装)
  - [更新已有源码 checkout](#更新已有源码-checkout)
  - [可选渠道依赖](#可选渠道依赖)
  - [🐳 Docker](#-docker)
- [🔑 配置](#-配置)
- [⚡ 快速上手](#-快速上手)
- [🍪 示例与实践](#-示例与实践)
- [🔌 MCP 集成](#-mcp-集成)
- [📱 渠道接入](#-渠道接入)
- [🎯 ᯓ➤ 路线图](#-ᯓ-路线图)
- [🤝 贡献](#-贡献)
- [📚 致谢](#-致谢)
- [📜 许可证](#-许可证)

## 📦 安装

> [!IMPORTANT]
> 需要 **Python 3.11 或 3.12**（`>=3.11,<3.13`）。目前最可靠的安装方式是 **源码 checkout + editable install**。在正式发布并验证 PyPI 包、`uv tool install` 包或预构建 Docker 镜像前，不建议把它们作为主安装路径。

### 推荐方式：源码 checkout + conda

```bash
git clone https://github.com/zhw-li/QuantumAppAgent.git
cd QuantumAppAgent

conda create -n tyqa python=3.11 -y
conda activate tyqa

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

如果你已经有本仓库 checkout，直接从 `cd QuantumAppAgent` 开始即可。

### 备选方式：标准 venv

```bash
git clone https://github.com/zhw-li/QuantumAppAgent.git
cd QuantumAppAgent

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### 验证安装

```bash
python -m pytest tests/test_skill_descriptions.py -q
tyqa -h
```

更完整的本地验证可运行：

```bash
python -m pytest tests/test_prompts.py tests/test_skill_descriptions.py tests/test_quantum_application_validation.py -q
```

### 更新已有源码 checkout

```bash
git pull
conda activate tyqa
python -m pip install -e ".[dev]"
```

### 可选渠道依赖

消息渠道集成需要额外依赖。请在源码 checkout 中按需安装：

```bash
python -m pip install -e ".[telegram]"     # Telegram
python -m pip install -e ".[discord]"      # Discord
python -m pip install -e ".[slack]"        # Slack
python -m pip install -e ".[wechat]"       # 微信
python -m pip install -e ".[qq]"           # QQ
python -m pip install -e ".[feishu]"       # 飞书
python -m pip install -e ".[all-channels]" # 全部
```

### 🐳 Docker

当前还没有可直接面向用户使用的 TYQA 预构建 Docker 镜像。仓库中的 Dockerfile 主要用于本地打包检查和受控部署；如果需要容器化运行，请从当前 checkout 本地构建：

```bash
docker build -t tyqa:local .
```

然后运行本地镜像：

```bash
docker run -it --rm \
  --env-file .env \
  -v "$(pwd)/workspace:/workspace" \
  -v tyqa-data:/home/tyqa/.tyqa \
  tyqa:local
```

各挂载的用途：

| 挂载 | 用途 |
| --- | --- |
| `--env-file .env` | API 密钥（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY` 等） |
| `./workspace:/workspace` | 智能体的工作目录 |
| `tyqa-data:/home/tyqa/.tyqa` | 持久化应用状态：会话数据库、全局技能、记忆，以及 `config.yaml` / `mcp.yaml` |

> [!IMPORTANT]
> 镜像以非 root 用户运行（`tyqa`，UID `1000`）。`./workspace` bind 挂载的宿主目录必须可被该 UID 写入。如果你的宿主用户 ID 不同，可以一次性 `chown -R 1000:1000 ./workspace`，或在每次 `docker run` 时加上 `--user "$(id -u):$(id -g)"`，让容器使用你的 UID。
>
> 容器中无法使用 iMessage 渠道，因为它需要 `imsg` CLI 与 macOS 的 Messages.app 通信。如需 iMessage，请直接在 macOS 上运行 TYQA。

也可通过 `docker compose` 从本地 Dockerfile 构建并运行：

```bash
docker compose build
docker compose run --rm tyqa
```

> [!NOTE]
> 本地镜像默认不捆绑以下可选组件，需要时再派生安装：
> - **`stt`**（基于 `faster-whisper` 的语音转文字）和 **`oauth`**（`ccproxy-api`）
> - **TinyTeX / LaTeX**（`pdflatex`、`latexmk`），供论文写作类技能使用
>
> Python 额外组件建议直接加到项目 Dockerfile 的 `uv sync` 步骤中，确保镜像仍从同一份源码 checkout 构建。LaTeX 只在 delivery-writing 工作流确实需要时，再通过派生镜像安装固定版本的 TinyTeX 或系统 TeX 包。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🔑 配置

最简单的方式是使用交互式配置向导：

```bash
tyqa onboard
```

> [!TIP]
> 向导将引导你完成供应商选择、密钥验证、模型选择和工作区模式设置。
> 支持 CLI 编程智能体订阅用户通过 OAuth 直连——无需 API Key。

![onboard](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_onboard.png)

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

也可以使用 `tyqa config set` 将密钥持久化到 `~/.config/tyqa/config.yaml`。

或者复制示例 `.env` 文件用于项目级配置：

```bash
cp .env.example .env  # 填入你的密钥
```

> ⚠️ 切勿将包含真实密钥的 `.env` 文件提交到版本库。该文件已在 `.gitignore` 中。

</details>

<p align="right"><a href="#top">🔝回到顶部</a></p>

## ⚡ 快速上手

```bash
tyqa  # 或 TYQA — 交互模式（默认 TUI）
```

![demo](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_cli.png)

> 运行 `tyqa -h` 查看全部 CLI 选项。

![cli help](https://raw.githubusercontent.com/zhw-li/QuantumAppAgent/main/.github/assets/tyqa_cli_help.png)

> [!TIP]
> 想用浏览器？运行 `tyqa --ui webui` 打开 Web 工作区界面。需要复制长输出？使用 `--ui cli` 切换到经典模式，即可使用终端原生复制。macOS [iTerm2](https://iterm2.com/) 用户也可以按住 `⌥ Option` 拖选文字，再 `⌘+C` 复制。

<details>
<summary>常用示例</summary>

```bash
tyqa                            # 交互模式（默认 TUI）
tyqa -p "你的问题"              # 单次查询模式
tyqa --workdir /path/to/project # 在指定目录下启动
tyqa -m run                     # 隔离的会话级工作区
tyqa --ui cli                   # 经典 CLI（轻量）
tyqa --ui webui                 # 浏览器工作区界面（需 Node/npx）
tyqa serve                      # 无头模式——仅渠道，无交互提示符
tyqa deploy                     # 独立 LangGraph 服务器——供外部 UI / SDK 客户端使用
```

</details>

<details>
<summary>Desktop WebUI</summary>

将 UI 后端设为 `webui`，全新的 `tyqa` 会话便会在单个终端里同时启动 deploy 式 LangGraph 服务器**和** [`@evoscientist/webui`](https://www.npmjs.com/package/@evoscientist/webui) 前端，无需管理第二个进程：

```bash
tyqa config set ui_backend webui   # 持久化；或用 `tyqa --ui webui` 临时启用
tyqa                               # 打开 http://localhost:4716
tyqa config set webui_port 4800    # 修改前端端口（须与 langgraph dev 端口不同）
```

需要 **Node.js 24 LTS**（提供 `npx`）；首次启动会下载 `@evoscientist/webui`，需要联网。注意：WebUI 不会显示 CLI/TUI 的历史会话，且 `-p` / `--resume` 会回退到经典 CLI。

</details>

<details>
<summary>操作审批</summary>

默认情况下，Shell 命令（`execute` 工具）执行前需要人工审批。跳过审批提示的方式：

```bash
# 单次会话：通过 CLI 参数启用自动审批
tyqa --auto-approve
tyqa -p "query" --auto-approve

# 持久化：写入配置（对所有后续会话生效）
tyqa config set auto_approve true

# 或仅放行特定命令前缀
tyqa config set shell_allow_list "python,pip,pytest,ruff,git"
```

会话中也可以在审批提示时回复 **3**（Approve all），仅对当次会话自动审批后续所有操作。

> [!CAUTION]
> **危险模式（Dangerous mode）** 会完全解除工作区沙箱——智能体可以读写、删除**真实文件系统上任意位置**的文件（`sudo`/`rm -rf /` 等高危命令仍被拦截）。它隐含 `--auto-approve`（不再提示审批）。请仅在你完全信任该任务时使用。
>
> ```bash
> tyqa --dangerous                       # 单次会话
> tyqa config set dangerous_mode true    # 持久化
> ```

</details>

<details>
<summary>智能体提问</summary>

智能体可以在需要澄清时主动向你提问（例如数据集选择、实验方向等）。此功能默认开启。关闭方式：

```bash
# 持久化：写入配置
tyqa config set enable_ask_user false

# 重新开启
tyqa config set enable_ask_user true
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

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🍪 示例与实践

- **量子应用** — 见 [`quantum_app_example/`](./quantum_app_example)，包含上文 5 个端到端的 QAOA / VQE / QRC 展示示例。
- **其他示例与实践** — 官方示例、进阶用法和部署配方合集：👉 [浏览全部 →](docs/README.md)

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 🔌 MCP 集成

通过 [MCP](https://modelcontextprotocol.io/) 服务器一条命令即可添加外部工具：

```bash
# 用法
tyqa mcp add <name> <command> [-- args...]

# 示例
tyqa mcp add sequential-thinking npx -- -y @modelcontextprotocol/server-sequential-thinking
```

> [!TIP]
> 关于命令选项、配置字段、工具路由、通配符过滤和故障排查，请参阅 **[MCP 集成指南](https://github.com/zhw-li/QuantumAppAgent/tree/main/tyqa/mcp#model-context-protocol-integration)**。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 📱 渠道接入

连接消息平台，使其与 CLI 共享同一智能体会话：

```bash
# 用法
tyqa channel setup <channel>

# 示例
tyqa channel setup telegram
```

多个渠道可同时运行——在配置中用逗号分隔：

```yaml
channel_enabled: "telegram,slack,feishu,qq"
```

也可以在 CLI 会话中通过 `/channel` 交互式启动渠道。

> [!TIP]
> 关于各渠道设置指南、功能矩阵、架构详情和故障排查，请参阅 **[渠道集成指南](https://github.com/zhw-li/QuantumAppAgent/tree/main/tyqa/channels#channels)**。

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
- [ ] 🏷️ 完成 `tyqa` 迁移后的发布清理（兼容 alias、配置迁移、发布产物）
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

- [**EvoScientist**](https://arxiv.org/abs/2603.08127) — 启发并奠定本项目基础的原始自进化多智能体 AI Scientist 框架。
- [**cqlib**](https://github.com/cqlib-quantum/cqlib) — 驱动算法层的量子 SDK（电路、模拟器、QCIS）。
- [**LangChain**](https://github.com/langchain-ai/langchain) / [**DeepAgents**](https://github.com/langchain-ai/deepagents) / [**LangGraph**](https://github.com/langchain-ai/langgraph) — 智能体框架技术栈。

感谢以上项目作者对开源社区的宝贵贡献。

<p align="right"><a href="#top">🔝回到顶部</a></p>

## 📜 许可证

本项目基于 Apache License 2.0 开源——详情请见 [LICENSE](./LICENSE) 文件。

<p align="right"><a href="#top">🔝回到顶部</a></p>

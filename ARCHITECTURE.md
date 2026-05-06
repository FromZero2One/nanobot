# nanobot 项目架构文档

> 版本: v0.1.5.post3 | 最后更新: 2026-05-06

本文档提供 nanobot 项目的完整架构概览，帮助开发者快速理解代码结构和核心设计。

---

## 📋 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [目录结构](#目录结构)
- [核心架构](#核心架构)
- [关键模块详解](#关键模块详解)
- [数据流](#数据流)
- [配置系统](#配置系统)
- [扩展开发](#扩展开发)
- [部署架构](#部署架构)

---

## 项目概述

**nanobot** 是一个超轻量级 AI 智能体框架，保持核心智能体循环小而清晰，同时支持聊天渠道、记忆系统、MCP（Model Context Protocol）和实际部署路径。

### 设计理念

- **Ultra-lightweight**: 稳定的长期运行行为，核心代码小巧可读
- **Research-ready**: 代码库刻意简单，便于研究、修改和扩展
- **Practical**: 内置聊天渠道、API、记忆、MCP 和部署方案
- **Hackable**: 快速上手，深入探索

### 核心特性

| 特性 | 说明 |
|------|------|
| 多平台支持 | Telegram, Discord, Slack, WhatsApp, 微信, QQ, 飞书, 钉钉等 12+ 渠道 |
| LLM 提供商 | OpenAI, Anthropic, Azure, AWS Bedrock, GitHub Copilot, OpenRouter 等 |
| 记忆系统 | 三层记忆架构（短期/中期/长期），Dream 后台巩固 |
| 工具系统 | 文件系统、Shell、Web搜索、MCP、Cron定时任务等 |
| 安全机制 | SSRF防护、沙箱执行、工作区限制、API密钥保护 |
| API服务 | OpenAI兼容的REST API，SSE流式响应 |
| WebUI | React + TypeScript 实时聊天界面 |

---

## 技术栈

### 后端 (Python)

**核心框架**
- Python >= 3.11
- typer - CLI命令行框架
- pydantic / pydantic-settings - 数据验证和配置管理
- loguru - 日志记录

**LLM集成**
- openai SDK - OpenAI API
- anthropic SDK - Anthropic Claude API
- tiktoken - Token计数

**通信协议**
- websockets / websocket-client - WebSocket支持
- httpx - HTTP客户端
- aiohttp - 异步HTTP（可选）

**聊天平台SDK**
- python-telegram-bot - Telegram
- discord.py - Discord（可选）
- slack-sdk - Slack
- lark-oapi - 飞书/Lark
- dingtalk-stream - 钉钉
- qq-botpy - QQ
- wecom-aibot-sdk-python - 企业微信（可选）
- matrix-nio - Matrix（可选）

**其他依赖**
- croniter - Cron表达式解析
- mcp - Model Context Protocol
- jinja2 - 模板引擎
- ddgs - DuckDuckGo搜索
- readability-lxml - 网页内容提取
- rich / prompt-toolkit / questionary - 终端UI
- pypdf / python-docx / openpyxl / python-pptx - 文档处理
- boto3 - AWS SDK
- dulwich - Git操作

### 前端 (WebUI)

- React 18 + TypeScript
- Vite + Bun（构建工具）
- Radix UI + Tailwind CSS
- i18next（9种语言：en, zh-CN, zh-TW, ja, ko, es, fr, vi, id）
- react-markdown + remark-gfm + rehype-katex

### Bridge (WhatsApp)

- Node.js 20+
- @whiskeysockets/baileys (WhatsApp Web API)
- TypeScript

---

## 目录结构

```
nanobot/
├── nanobot/                    # 核心Python包
│   ├── __init__.py            # 包初始化，导出Nanobot和RunResult
│   ├── __main__.py            # 模块入口点 (python -m nanobot)
│   ├── nanobot.py             # 高级编程接口 (Nanobot facade)
│   │
│   ├── agent/                 # 智能体核心模块
│   │   ├── loop.py            # 核心智能体循环 (61.3 KB)
│   │   ├── runner.py          # 工具执行引擎 (48.9 KB)
│   │   ├── memory.py          # 记忆系统 (41 KB)
│   │   ├── context.py         # 上下文构建器
│   │   ├── subagent.py        # 子智能体管理器 (15.2 KB)
│   │   ├── skills.py          # 技能系统
│   │   ├── hook.py            # 生命周期钩子
│   │   ├── autocompact.py     # 自动压缩
│   │   └── tools/             # 工具系统
│   │       ├── base.py        # 工具基类
│   │       ├── filesystem.py  # 文件系统工具 (34.5 KB)
│   │       ├── web.py         # Web搜索和抓取 (22.6 KB)
│   │       ├── shell.py       # Shell执行
│   │       ├── mcp.py         # MCP集成 (25.4 KB)
│   │       ├── search.py      # 搜索工具 (grep/glob, 20.5 KB)
│   │       ├── self.py        # 自省工具 (19.9 KB)
│   │       ├── cron.py        # 定时任务
│   │       ├── ask_user.py    # 用户交互
│   │       ├── notebook.py    # Jupyter Notebook编辑
│   │       └── spawn.py       # 子智能体启动
│   │
│   ├── providers/             # LLM提供商抽象层
│   │   ├── base.py            # 基础提供商接口 (30.9 KB)
│   │   ├── factory.py         # 工厂模式创建提供商
│   │   ├── registry.py        # 提供商注册表
│   │   ├── anthropic_provider.py    # Anthropic Claude (25.0 KB)
│   │   ├── openai_compat_provider.py # OpenAI兼容API (51 KB)
│   │   ├── azure_openai_provider.py  # Azure OpenAI
│   │   ├── bedrock_provider.py       # AWS Bedrock (28.9 KB)
│   │   ├── github_copilot_provider.py # GitHub Copilot
│   │   └── transcription.py          # 语音转录
│   │
│   ├── channels/              # 聊天渠道集成
│   │   ├── base.py            # 渠道基类
│   │   ├── manager.py         # 渠道管理器
│   │   ├── telegram.py        # Telegram (52.6 KB)
│   │   ├── weixin.py          # 微信 (55.4 KB)
│   │   ├── feishu.py          # 飞书/Lark (73 KB - 最大)
│   │   ├── discord.py         # Discord
│   │   ├── slack.py           # Slack
│   │   ├── websocket.py       # WebSocket (53.2 KB)
│   │   ├── whatsapp.py        # WhatsApp
│   │   ├── qq.py              # QQ
│   │   ├── wecom.py           # 企业微信
│   │   ├── dingtalk.py        # 钉钉
│   │   ├── matrix.py          # Matrix
│   │   ├── email.py           # 电子邮件
│   │   └── msteams.py         # Microsoft Teams
│   │
│   ├── cli/                   # 命令行界面
│   │   ├── commands.py        # CLI命令 (62.9 KB)
│   │   ├── onboard.py         # 交互式设置向导 (39.7 KB)
│   │   └── stream.py          # 流式输出渲染
│   │
│   ├── config/                # 配置管理
│   │   ├── schema.py          # Pydantic配置模式 (16.8 KB)
│   │   ├── loader.py          # 配置加载器
│   │   └── paths.py           # 路径管理
│   │
│   ├── session/               # 会话管理
│   │   └── manager.py         # 会话持久化 (21.9 KB)
│   │
│   ├── api/                   # REST API服务器
│   │   └── server.py          # OpenAI兼容API (14.5 KB)
│   │
│   ├── cron/                  # 定时任务服务
│   │   ├── service.py         # Cron服务 (25.5 KB)
│   │   └── types.py           # Cron类型定义
│   │
│   ├── bus/                   # 消息总线
│   │   ├── events.py          # 事件定义
│   │   └── queue.py           # 消息队列
│   │
│   ├── command/               # 命令路由
│   │   ├── router.py          # 命令路由器
│   │   └── builtin.py         # 内置命令 (14.7 KB)
│   │
│   ├── heartbeat/             # 心跳服务
│   │   └── service.py         # 定期提醒
│   │
│   ├── security/              # 安全模块
│   │   └── network.py         # 网络安全防护
│   │
│   ├── utils/                 # 工具函数
│   │   ├── helpers.py         # 通用辅助函数
│   │   ├── document.py        # 文档解析
│   │   ├── gitstore.py        # Git存储
│   │   └── ...
│   │
│   └── skills/                # 内置技能
│       ├── skill-creator/     # 技能创建工具
│       ├── clawhub/           # ClawHub集成
│       ├── memory/            # 记忆相关技能
│       ├── github/            # GitHub技能
│       └── ...
│
├── webui/                     # Web用户界面
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── i18n/              # 国际化
│   │   └── lib/               # 客户端库
│   ├── package.json
│   └── vite.config.ts
│
├── bridge/                    # WhatsApp桥接服务
│   ├── src/
│   │   ├── index.ts
│   │   ├── server.ts
│   │   └── whatsapp.ts
│   └── package.json
│
├── tests/                     # 测试套件
│   ├── agent/                 # 智能体测试
│   ├── channels/              # 渠道测试
│   ├── providers/             # 提供商测试
│   └── ...
│
├── docs/                      # 文档
├── case/                      # 演示GIF
├── images/                    # 图片资源
│
├── pyproject.toml             # Python项目配置
├── Dockerfile                 # Docker镜像构建
├── docker-compose.yml         # Docker Compose配置
├── README.md                  # 项目说明
└── CONTRIBUTING.md            # 贡献指南
```

---

## 核心架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Chat Channels                            │
│  Telegram │ Discord │ Slack │ WeChat │ Feishu │ WebSocket   │
└──────────────┬──────────────────────────────────────────────┘
               │ InboundMessage
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Bus                               │
│              (Decouples channels & agent)                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Loop                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Context  │→ │ Provider │→ │ Runner   │→ │ Memory   │   │
│  │ Builder  │  │ (LLM)    │  │ (Tools)  │  │ System   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────┬──────────────────────────────────────────────┘
               │ OutboundMessage
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Response Delivery                          │
│              (Stream to channel/API)                         │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件关系

1. **Channel → MessageBus → AgentLoop**
   - 渠道接收用户消息，标准化为 InboundMessage
   - 通过消息总线传递给智能体循环
   - AgentLoop 处理后返回 OutboundMessage

2. **AgentLoop → Provider → LLM**
   - AgentLoop 构建上下文，调用 Provider
   - Provider 统一封装不同LLM API
   - 支持流式响应和思考模式

3. **AgentLoop → Runner → Tools**
   - LLM 决定需要调用的工具
   - Runner 并发执行工具，处理错误和重试
   - 工具结果返回给 LLM 继续推理

4. **AgentLoop ↔ Memory System**
   - 读取会话历史和 MEMORY.md
   - Dream 后台整理记忆
   - 写入 SOUL.md 和 USER.md

---

## 关键模块详解

### 1. 智能体循环 (AgentLoop)

**文件**: `nanobot/agent/loop.py` (61.3 KB)

**职责**: 核心智能体循环，协调整个对话流程

**关键方法**:
```python
class AgentLoop:
    async def process_message(self, message: InboundMessage) -> None
    async def _llm_call(self, context: list[dict]) -> LLMResponse
    async def _execute_tools(self, tool_calls: list) -> ToolResults
    async def _compact_context(self) -> None
    async def _dream_consolidate(self) -> None
```

**工作流程**:
1. 接收消息 → 2. 构建上下文 → 3. 调用LLM → 4. 执行工具 → 5. 更新记忆 → 6. 返回响应

**特性**:
- 流式输出支持
- 自动上下文压缩
- Dream 记忆巩固
- 子智能体管理
- 工具注册和执行
- 会话历史管理

### 2. 工具执行引擎 (AgentRunner)

**文件**: `nanobot/agent/runner.py` (48.9 KB)

**职责**: 共享的工具执行循环

**关键功能**:
- 并发工具执行
- 错误处理和重试
- Token预算管理
- 进度回调
- 虚拟工具调用（心跳保活）

**工具注册表**:
```python
tool_registry = {
    "read_file": FileSystemTool.read,
    "write_file": FileSystemTool.write,
    "exec": ShellTool.execute,
    "web_search": WebTool.search,
    "grep": SearchTool.grep,
    "glob": SearchTool.glob,
    "my_tool": SelfTool.invoke,
    "ask_user": AskUserTool.prompt,
}
```

### 3. 记忆系统 (Memory System)

**文件**: `nanobot/agent/memory.py` (41 KB)

**三层记忆架构**:

| 层级 | 文件 | 用途 | 更新频率 |
|------|------|------|----------|
| 短期 | `history.jsonl` | 当前会话对话历史 | 每次对话 |
| 中期 | `MEMORY.md` | 项目知识和经验 | 定期整理 |
| 长期 | `SOUL.md` / `USER.md` | 人格和用户偏好 | Dream巩固 |

**核心类**:
```python
class MemoryStore:
    """纯文件I/O层，管理记忆文件"""
    def load_memory_md(self) -> str
    def save_memory_md(self, content: str) -> None
    def append_history(self, entry: dict) -> None
    def load_soul(self) -> str
    def load_user_profile(self) -> str

class Consolidator:
    """轻量级记忆整合器"""
    async def consolidate(self, changes: list) -> None

class Dream:
    """两阶段记忆巩固处理器"""
    async def phase1_analyze_changes(self) -> ChangeReport
    async def phase2_refine_memory(self, report: ChangeReport) -> None
```

**Dream 巩固流程**:
1. Phase 1: 使用 `git blame` 分析代码变更
2. Phase 2: LLM 驱动的记忆提炼
3. 更新 MEMORY.md、SOUL.md、USER.md

### 4. LLM 提供商抽象 (Providers)

**文件**: `nanobot/providers/base.py` (30.9 KB)

**设计模式**: 策略模式 + 工厂模式

**基类接口**:
```python
class BaseProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
        thinking: dict | None = None,
    ) -> ChatCompletionResponse
    
    @abstractmethod
    def count_tokens(self, messages: list[dict]) -> int
```

**支持的提供商**:

| 提供商 | 文件 | 特点 |
|--------|------|------|
| OpenAI | `openai_compat_provider.py` | GPT-4, GPT-5, o-series |
| Anthropic | `anthropic_provider.py` | Claude Opus, Sonnet, Haiku |
| Azure OpenAI | `azure_openai_provider.py` | 企业级部署 |
| AWS Bedrock | `bedrock_provider.py` | Claude, Llama等 |
| GitHub Copilot | `github_copilot_provider.py` | OAuth认证 |
| OpenRouter | `openai_compat_provider.py` | 多模型聚合（推荐） |

**通用适配器** (`openai_compat_provider.py`, 51 KB):
- 支持所有OpenAI兼容API
- 自动检测模型能力
- 缓存优化
- 思考模式支持

### 5. 聊天渠道 (Channels)

**文件**: `nanobot/channels/`

**渠道基类** (`base.py`):
```python
class Channel(ABC):
    @abstractmethod
    async def start(self) -> None
    @abstractmethod
    async def stop(self) -> None
    @abstractmethod
    async def send_message(self, message: OutboundMessage) -> None
    @abstractmethod
    async def handle_incoming(self, data: dict) -> InboundMessage
```

**主要渠道实现**:

| 渠道 | 文件大小 | 特色功能 |
|------|----------|----------|
| Feishu | 73 KB | CardKit流式渲染，富文本 |
| WeChat | 55.4 KB | 个人号集成，多媒体 |
| WebSocket | 53.2 KB | 实时双向通信，WebUI后端 |
| Telegram | 52.6 KB | 完整多媒体支持，线程管理 |
| Discord | - | 线程感知会话 |
| Slack | - | mrkdwn格式化 |

**渠道管理器** (`manager.py`):
```python
class ChannelManager:
    async def start_all(self) -> None
    async def stop_all(self) -> None
    def get_channel(self, name: str) -> Channel
```

### 6. 配置系统 (Config)

**文件**: `nanobot/config/schema.py` (16.8 KB)

**Pydantic配置模式**:
```python
class NanobotConfig(BaseSettings):
    providers: dict[str, ProviderConfig]
    agents: AgentDefaults
    channels: ChannelsConfig
    tools: ToolsConfig
    dream: DreamConfig
    workspace: str
    timezone: str
```

**配置层次**:
1. 默认值（代码中硬编码）
2. 配置文件（`~/.nanobot/config.json`）
3. 环境变量（优先级最高）

**示例配置**:
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4-6",
      "workspace": "~/.nanobot/workspace",
      "maxTokens": 8192,
      "contextWindowTokens": 65536,
      "timezone": "Asia/Shanghai"
    }
  },
  "channels": {
    "websocket": {
      "enabled": true
    }
  },
  "tools": {
    "web": {
      "searchProvider": "duckduckgo"
    },
    "exec": {
      "sandbox": "bubblewrap"
    }
  }
}
```

### 7. 会话管理 (Session)

**文件**: `nanobot/session/manager.py` (21.9 KB)

**数据结构**:
```python
@dataclass
class Session:
    session_key: str
    messages: list[dict]  # JSONL格式
    created_at: datetime
    updated_at: datetime
    token_count: int
```

**特性**:
- 原子写入（防损坏）
- 自动修复（损坏数据恢复）
- Token预算控制
- 会话TTL和自动压缩
- 时间戳注解

### 8. 定时任务 (Cron)

**文件**: `nanobot/cron/service.py` (25.5 KB)

**功能**:
- 支持cron表达式和固定间隔
- 时区感知
- 自然语言调度
- 运行历史记录

**示例**:
```python
# 每天上午9点提醒
cron_service.schedule("0 9 * * *", "daily_standup")

# 每30分钟检查一次
cron_service.schedule("@every 30m", "health_check")
```

### 9. 命令行界面 (CLI)

**文件**: `nanobot/cli/commands.py` (62.9 KB)

**主要命令**:
```bash
nanobot onboard          # 交互式设置向导
nanobot agent            # 启动CLI聊天模式
nanobot gateway          # 启动网关服务
nanobot serve            # 启动OpenAI兼容API
nanobot status           # 显示状态
nanobot channels login   # 渠道登录
```

**设置向导** (`onboard.py`, 39.7 KB):
- 自动检测可用提供商
- 模型自动补全
- 交互式配置生成

### 10. API服务器

**文件**: `nanobot/api/server.py` (14.5 KB)

**功能**:
- OpenAI兼容的REST API
- SSE流式响应
- 文件上传支持
- 默认端口: 8900

**端点**:
```
POST /v1/chat/completions    # 聊天完成
POST /v1/files               # 文件上传
GET  /v1/models              # 列出模型
```

---

## 数据流

### 完整请求流程

```
用户消息
   ↓
┌─────────────────────┐
│  Channel接收         │ (Telegram/Discord/etc)
└──────────┬──────────┘
           │ InboundMessage
           ↓
┌─────────────────────┐
│  MessageBus         │ (解耦渠道和智能体)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  AgentLoop          │
│  ├─ 加载会话历史     │
│  ├─ 构建上下文       │
│  ├─ 调用LLM         │
└──────────┬──────────┘
           │ Prompt
           ↓
┌─────────────────────┐
│  Provider           │ (OpenAI/Anthropic/etc)
└──────────┬──────────┘
           │ LLM Response
           ↓
┌─────────────────────┐
│  AgentLoop          │
│  ├─ 解析工具调用     │
│  └─ 有工具？         │
└──────────┬──────────┘
     Yes   │   No
           ↓
┌─────────────────────┐
│  AgentRunner        │
│  ├─ 并发执行工具     │
│  ├─ 错误重试         │
│  └─ 返回结果         │
└──────────┬──────────┘
           │ Tool Results
           ↓
┌─────────────────────┐
│  AgentLoop          │
│  ├─ 更新记忆         │
│  ├─ 构建最终响应     │
└──────────┬──────────┘
           │ OutboundMessage
           ↓
┌─────────────────────┐
│  Channel发送         │ (流式/批量)
└─────────────────────┘
           ↓
        用户收到响应
```

### 记忆数据流

```
对话进行中
   ↓
┌─────────────────────┐
│  history.jsonl      │ (每次对话追加)
└──────────┬──────────┘
           │
           ↓ (定期触发)
┌─────────────────────┐
│  Dream Phase 1      │
│  git blame分析      │
└──────────┬──────────┘
           │ Change Report
           ↓
┌─────────────────────┐
│  Dream Phase 2      │
│  LLM提炼记忆         │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  MEMORY.md          │ (项目知识)
│  SOUL.md            │ (人格)
│  USER.md            │ (用户偏好)
└─────────────────────┘
```

---

## 配置系统

### 配置文件位置

- **全局配置**: `~/.nanobot/config.json`
- **工作区配置**: `~/.nanobot/workspace/`
- **会话数据**: `~/.nanobot/sessions/`

### 配置项详解

#### 1. 提供商配置 (providers)

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx",
      "baseUrl": "https://openrouter.ai/api/v1"
    },
    "anthropic": {
      "apiKey": "sk-ant-xxx"
    },
    "ollama": {
      "baseUrl": "http://localhost:11434"
    }
  }
}
```

#### 2. 智能体默认配置 (agents.defaults)

```json
{
  "agents": {
    "defaults": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4-6",
      "workspace": "~/.nanobot/workspace",
      "maxTokens": 8192,
      "contextWindowTokens": 65536,
      "temperature": 0.7,
      "timezone": "Asia/Shanghai",
      "thinking": {
        "enabled": true,
        "budget": 2000
      }
    }
  }
}
```

#### 3. 渠道配置 (channels)

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    },
    "websocket": {
      "enabled": true,
      "port": 18790
    },
    "discord": {
      "enabled": false,
      "botToken": "xxx",
      "allowedChannels": ["channel-id-1"]
    }
  }
}
```

#### 4. 工具配置 (tools)

```json
{
  "tools": {
    "web": {
      "searchProvider": "duckduckgo",
      "fetchTimeout": 30
    },
    "exec": {
      "sandbox": "bubblewrap",
      "allowedDirs": ["~/projects"],
      "blockedCommands": ["rm -rf /", "mkfs"]
    },
    "filesystem": {
      "workspaceOnly": true
    }
  }
}
```

#### 5. Dream配置 (dream)

```json
{
  "dream": {
    "enabled": true,
    "interval": "2h",
    "consolidateOnShutdown": true,
    "maxChangesPerRun": 50
  }
}
```

---

## 扩展开发

### 1. 添加新的LLM提供商

**步骤**:
1. 创建提供商类继承 `BaseProvider`
2. 实现 `chat_completion` 和 `count_tokens` 方法
3. 在 `registry.py` 中注册

**示例**:
```python
# nanobot/providers/my_provider.py
from .base import BaseProvider

class MyProvider(BaseProvider):
    def __init__(self, config: dict):
        self.api_key = config.get("apiKey")
        self.base_url = config.get("baseUrl", "https://api.example.com")
    
    async def chat_completion(self, messages, tools=None, stream=False):
        # 实现API调用逻辑
        pass
    
    def count_tokens(self, messages):
        # 实现Token计数
        pass

# nanobot/providers/registry.py
REGISTRY["my_provider"] = MyProvider
```

### 2. 添加新的聊天渠道

**步骤**:
1. 创建渠道类继承 `Channel`
2. 实现 `start`, `stop`, `send_message`, `handle_incoming` 方法
3. 在渠道管理器中注册

**示例**:
```python
# nanobot/channels/my_channel.py
from .base import Channel

class MyChannel(Channel):
    async def start(self):
        # 初始化连接
        pass
    
    async def stop(self):
        # 清理资源
        pass
    
    async def send_message(self, message):
        # 发送消息到平台
        pass
    
    async def handle_incoming(self, data):
        # 解析平台消息为标准格式
        return InboundMessage(...)
```

### 3. 添加工具

**步骤**:
1. 创建工具函数
2. 在 `AgentLoop` 中注册工具schema和执行函数

**示例**:
```python
# nanobot/agent/tools/my_tool.py
async def my_custom_tool(param1: str, param2: int) -> str:
    """工具描述（会被LLM看到）
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        返回值说明
    """
    # 实现逻辑
    return f"Result: {param1}, {param2}"

# 在 AgentLoop 中注册
self.tool_registry.register(
    name="my_tool",
    schema={
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "工具描述",
            "parameters": {...}
        }
    },
    handler=my_custom_tool
)
```

### 4. 添加技能 (Skills)

技能是可插拔的功能模块，位于 `nanobot/skills/` 目录。

**技能结构**:
```
skills/my-skill/
├── SKILL.md          # 技能描述和使用说明
├── assets/           # 资源文件
│   └── widget.html   # 可选的HTML Widget
└── scripts/          # 可选的脚本
    └── run.sh
```

**SKILL.md 示例**:
```markdown
# My Skill

## Description
简要描述技能功能

## Usage
使用说明

## Examples
示例用法
```

---

## 部署架构

### 1. 本地开发

```bash
# 安装
pip install -e .

# 设置
nanobot onboard

# 运行CLI
nanobot agent

# 运行网关
nanobot gateway

# 运行API
nanobot serve
```

### 2. Docker部署

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  nanobot-gateway:
    build: .
    ports:
      - "18790:18790"
    volumes:
      - ~/.nanobot:/home/nanobot/.nanobot
    environment:
      - NANOBOT_CONFIG_PATH=/home/nanobot/.nanobot/config.json
  
  nanobot-api:
    build: .
    ports:
      - "8900:8900"
    command: nanobot serve
    volumes:
      - ~/.nanobot:/home/nanobot/.nanobot
```

### 3. 生产环境

**架构建议**:
```
                    ┌──────────────┐
                    │  Load Balancer│
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
   │ Gateway 1   │  │ Gateway 2  │  │ Gateway 3  │
   │ (WS:18790)  │  │ (WS:18790) │  │ (WS:18790) │
   └──────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                  ┌────────▼────────┐
                  │  Shared Storage  │
                  │  (Sessions/Mem)  │
                  └─────────────────┘
```

**关键考虑**:
- 会话持久化：使用共享存储或数据库
- 水平扩展：多个Gateway实例
- 负载均衡：基于session_key的路由
- 监控：日志聚合、性能指标

---

## 安全机制

### 1. SSRF防护

**文件**: `nanobot/security/network.py`

- 阻止内网地址访问
- 验证URL协议
- DNS重绑定防护

### 2. 沙箱执行

**Shell工具配置**:
```json
{
  "tools": {
    "exec": {
      "sandbox": "bubblewrap",
      "allowedDirs": ["~/projects"],
      "blockedCommands": ["rm -rf /", "mkfs", "dd"]
    }
  }
}
```

### 3. 工作区限制

- 文件系统工具限制在工作区内
- 防止访问敏感文件
- 符号链接检查

### 4. API密钥保护

- 环境变量优先
- 配置文件加密（可选）
- 不在日志中打印密钥

---

## 测试

### 测试框架

- pytest + pytest-asyncio
- 覆盖率: pytest-cov
- 代码质量: ruff

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/agent/

# 带覆盖率报告
pytest --cov=nanobot --cov-report=html
```

### 测试目录结构

```
tests/
├── agent/
│   ├── test_loop.py
│   ├── test_runner.py
│   └── test_memory.py
├── channels/
│   ├── test_telegram.py
│   └── test_websocket.py
├── providers/
│   └── test_openai.py
└── conftest.py
```

---

## 常见问题

### Q1: 如何调试智能体循环？

启用详细日志：
```bash
export LOGURU_LEVEL=DEBUG
nanobot agent
```

### Q2: 如何添加自定义工具？

参考 [扩展开发 - 添加工具](#3-添加工具)

### Q3: 如何备份记忆数据？

备份 `~/.nanobot/` 目录：
```bash
tar -czf nanobot-backup.tar.gz ~/.nanobot/
```

### Q4: 如何切换模型？

修改配置文件中的 `agents.defaults.model`，或运行时指定：
```bash
nanobot agent --model gpt-4o
```

### Q5: 如何实现多实例部署？

参考 [docs/multiple-instances.md](./docs/multiple-instances.md)

---

## 相关文档

- [快速开始](./docs/quick-start.md)
- [配置详解](./docs/configuration.md)
- [聊天渠道](./docs/chat-apps.md)
- [记忆系统](./docs/memory.md)
- [部署指南](./docs/deployment.md)
- [OpenAI兼容API](./docs/openai-api.md)
- [Python SDK](./docs/python-sdk.md)
- [WebSocket通道](./docs/websocket.md)

---

## 贡献指南

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

**分支策略**:
- `main`: 稳定版本
- `nightly`: 实验性功能

**提交PR前**:
1. 运行测试: `pytest`
2. 代码检查: `ruff check .`
3. 更新文档（如需要）

---

## 联系方式

- 项目主页: https://github.com/HKUDS/nanobot
- 文档: https://nanobot.wiki
- 邮箱: xubinrencs@gmail.com
- Discord: https://discord.gg/MnCvHqpUGB

---

*本文档由 nanobot 团队维护，欢迎提交改进建议。*

# 技术设计文档: AutoWiki MVP (本地/自托管版)

## 🛠 我们将如何构建 (How We'll Build It)

### 推荐方案："透明盒" Vibe-Coding (Glass Box Vibe-Coding)

鉴于您要构建的是一个复杂的系统（涉及 AST 语法树解析 + Agent 智能体），但又希望采用 "Vibe-code"（AI 辅助编程）的方式，我们需要一套既能屏蔽底层样板代码，又能暴露核心逻辑的方案。

**🏆 首选推荐工具: 首选推荐工具: Gemini CLI (搭配 Gemini 3 Pro 模型)**
* **为什么它最适合 AutoWiki:** Gemini 3 Pro 拥有巨大的上下文窗口（1M+ token），能够一次性读取整个代码库的结构，非常适合处理 AutoWiki 的全局架构分析任务。
* **"架构师"工作流:** 您将在终端使用 Gemini CLI。例如：gemini "读取 backend 目录下的所有文件，编写一个 Tree-sitter 解析脚本"。您将审查 CLI 输出的代码块，然后将其重定向或复制到文件中。
* **成本:** $20/月 (Pro 版) + 您构建 Agent 所需的 API 费用。

## 🏗 系统架构 (Docker化)

由于这是一个本地应用，我们将使用 **Docker Compose** 一键启动整套服务。这确保了您的用户无需手动安装 Python、Node 或 向量数据库。

```mermaid
graph TD
    User[用户浏览器] --> |localhost:3000| FE[Next.js]
    FE -->|HTTP/REST| BE[FastAPI]
    
    subgraph "后端容器 (Python)"
        BE --> Agent[AgentScope 编排器]
        Agent --> Parser[Tree-sitter 解析器]
        Agent --> LLM[LLM API]
    end
    
    subgraph "数据持久化 (挂载卷)"
        BE --> SQLite[(SQLite - 元数据)]
        BE --> Vector[(FAISS/Chroma - 向量嵌入)]
        BE --> FS[本地文件系统]
    end
```

## 📋 项目启动清单 (Project Setup Checklist)

### 第 1 步：工具准备 (第 1 天)
- [ ] 安装 Gemini CLI 工具 (例如通过 ```pip install google-generativeai``` 或官方 CLI 工具)。
- [ ] 获取 Google AI Studio API Key 并配置环境变量 ```GOOGLE_API_KEY```
- [ ] 初始化: 在终端运行: ```gemini "为 Next.js 15 和 FastAPI 项目生成标准的目录结构命令"```，然后执行生成的命令。

### 第 2 步：仓库结构 (第 1 天)

让 VSCode 运行以下命令：

```bash
# 创建项目结构
mkdir autowiki && cd autowiki
mkdir -p frontend backend/app data
touch docker-compose.yml
```

### 第 3 步："骨架"初始化 (第 2 天)

我们将提示 VSCode 先构建容器，这样您就能立即拥有一个正在运行（虽是空白）的应用。

**给 VSCode 的提示词 (Prompt)**:

```
"我正在构建一个自托管应用程序，包含 Next.js 前端和 FastAPI 后端。请编写一个 docker-compose.yml 将它们连接起来。前端运行在 3000 端口，后端运行在 8000 端口。并为每个服务创建基础的 Dockerfile。"
```

## 🏗 构建核心功能

### 功能 1：数据摄入管道 (最难的部分)

**复杂度**: ⭐⭐⭐⭐⭐ (高)

**依据 PRD**: "使用 Tree-sitter 提取代码骨架... 使用 LLM 生成语义化解释。"

**实施策略**: 不要让 AI 一次性“构建整个解析器”，这通常会失败。请按以下步骤拆解：

1. 步骤 A (Tree-sitter 设置):
    * 提示词: "创建一个使用 tree_sitter 库的 Python 脚本 parser.py。它应接受一个文件路径，检测它是 Python 还是 TypeScript，并打印出 AST（抽象语法树）。"

2. 步骤 B (分块/Chunking):
    * 提示词: "更新 parser.py 以遍历 AST。提取所有的函数定义和类名。将它们作为包含 'code' (代码) 和 'metadata' (元数据) 字段的 JSON 对象返回。"

3. 步骤 C (向量存储):
    * 提示词: "创建 storage.py。使用 chromadb (最适合本地)。编写一个详细的函数 save_chunks，接收步骤 B 中的 JSON 并将其保存到本地持久化的 Chroma DB 中。"

### 功能 2："可操控"配置 (The "Steerable" Config)

**复杂度**: ⭐⭐ (低)

**依据 PRD**: 支持 ```.autowiki.json``` 配置文件。

**实施策略**:

* 提示词: "在 config.py 中创建一个 Pydantic 模型，以匹配此 JSON Schema：[粘贴 PRD 中的 Schema]。添加一个函数，在目标仓库根目录中查找 ```.autowiki.json``` 并进行解析。"

### 功能 3：前端仪表盘 (Frontend Dashboard)

**复杂度**: ⭐⭐⭐ (中) 

**依据 PRD**: 深色模式 (Dark Mode)，项目卡片，类似 "DeepWiki" 的风格。

**实施策略**:

* 提示词: "我需要一个使用 Tailwind CSS 的仪表盘页面。它应该使用深色主题 (slate-900)。创建一个'项目卡片'的网格布局。每个卡片显示标题、描述和'最后更新'徽章。目前先使用模拟数据 (Mock data)。"

## 🤖 AI 辅助与审计策略

### 如何审计代码 (您的"架构师"角色)

既然您希望理解系统，请在 Gemini CLI 生成代码之后，使用以下提示词进行“质询”：

1. "五岁小孩也能懂"的审计:
    * "解释一下 ```parser.py``` 是如何处理用户代码中的语法错误的。它是会让整个应用崩溃，还是仅仅跳过该文件？"
2. 安全审计:
    * "审查 ```routes.py```。既然这是本地运行的，我们是否暴露了任何可能允许恶意网站通过 CSRF 窃取用户代码的端点？请添加 CORS 保护。"
3. 逻辑检查:
    * "你使用了简单的字符分割来处理代码分块。PRD 要求基于 AST 的'智能分块'。请重构 ```chunker.py```，严格按照函数/类的边界进行分割。"

## 🚀 部署 (分发)

由于这是一个自托管应用，您的“部署”实际上就是分发 ```docker-compose.yml``` 文件。

1. 用户体验: 用户克隆您的仓库 -> 运行 ```docker-compose up``` -> 打开 ```localhost:3000```。
2. 更新: 用户执行 ```git pull``` -> ```docker-compose up --build```。

## 💰 成本分析 (本地/自托管)

| 资源 | 成本  | 备注 |
| :---- | :---- | :---- |
| **托管 (Hosting)** | $0 | 运行在用户自己的机器上 |
| **向量数据库** | $0 | 本地运行 (Chroma/FAISS) |
| **开发工具** | $20/月 | VSCode + Gemini插件 |
| **LLM API** | 可变 | 开发测试时付费。用户在应用设置中填入自己的 API Key，由用户付费 |

关键决策: 对于 MVP 版本，不要通过您的服务器代理 LLM 调用。请在“设置”页面要求用户输入他们自己的 OpenAI/Anthropic Key。这能将您的运营成本保持在 $0。

## ⚠️ 风险与局限性

* Docker 性能: 在用户的笔记本电脑（尤其是旧电脑）上同时运行 LLM 编排 + 向量数据库 + Next.js 可能会很重。
    * 缓解措施: 在设置中添加“低资源模式”，禁用后台自动重新索引。

* 上下文窗口限制: 解析巨大的 Monorepo (单体仓库) 可能会让用户的 API 成本激增。
    * 缓解措施: 严格实现 PRD 中提到的 "Ignore Patterns" (忽略模式/白名单机制)。

## ✅ 成功检查清单

- [ ] Docker 正常: docker-compose up 能在全新的机器上无报错启动。
- [ ] 摄入正常: 我可以将其指向一个本地 Git 仓库，它能提取代码结构。
- [ ] Wiki 生成: 它能生成实际描述代码逻辑的 Markdown 文件。
- [ ] UI 整洁: “深色模式”看起来很专业，没有明显的样式破损。
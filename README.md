# Shen

[![PyPI version](https://badge.fury.io/py/shen-cli.svg)](https://badge.fury.io/py/shen-cli)
[![Python Version](https://img.shields.io/pypi/pyversions/shen-cli.svg)](https://pypi.org/project/shen-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这个项目会是一个AI命令行工具，专注于处理编程以外的事情

因为我看到了Claude Code神一样的编程能力，他的交互和效果令我惊讶。

因此我在寻找一个类似的命令行工具，这个命令行工具不是专注于编程的，而是专注于处理其他工作。
让使用者能得到更大的效率提升。

这是一个探索性的项目，主要是为了探索CLI+MCP结合帮助使用者完成工作的常规任务。

选择使用python实现

## 特性

- 🚀 **AI 驱动**：专注于非编程任务的自动化处理
- 🔧 **MCP 集成**：支持 Model Context Protocol，可集成各种外部服务
- 🎯 **任务导向**：基于自然语言描述执行各种日常任务
- 📦 **插件系统**：可扩展的插件架构
- 🛠️ **CLI 界面**：强大的命令行界面，支持交互模式
- ⚡ **高性能**：异步处理，支持并发任务

## FAQ
### 为什么是做命令行工具？

1. 目前已经很多通用GUI的AI软件、AI IDE、AI plugin了，所以再做一个轮子的意义感觉不大
2. 如果你使用AI的强度比较高，你一定感受到了，无论是cursor还是augment之类的AI IDE或者是vscode插件，都受到其本身的制约，无法发挥出最强能力，这种情况无法避免，而Claude Code是CLI，因此他避开了这个问题。
3. 不一定所有的工作都在前台完成，也不一定所有的工作都在个人计算机完成。CLI会带来更多玩法和可能性，也许能派遣他到服务器上去（得足够安全），或者在后台运行，自动化通过TODOs读取任务并解决

### CLI的优势是什么？

1. CLI有更强的跨平台性（虽然普通用户可能会无法使用）
2. CLI受到的限制更少，能拥有的操作权限更大
3. 更多任务的并行可能
4. 更强的集成能力，他应该能被其他软件集成，就像ffmpeg那样


### 可能的工作？

他可能会聚合很多MCP服务，理解整个计算机中有哪些文档和软件，帮助用户完成文档整理、垃圾清理、提供必要信息、制作excel、world、安全检查、软件安装（软件安装我觉得对我一直很头疼，总是报错很烦）等一些常规工作

---

不过目前的确没有想好他和Claude Code的真正差异是什么，感觉Claude Code除了写代码，其他事情也干的不错。
我还得仔细思考一下。

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install shen-cli
```

### 从源码安装

```bash
git clone https://github.com/shenjingnan/shen.git
cd shen
pip install -e .
```

## 使用方法

### 基本命令

```bash
# 查看版本
shen --version

# 查看帮助
shen --help

# 获取 Shen 信息
shen info

# 列出可用插件
shen plugins

# 运行任务
shen run "帮我整理下载文件夹"

# 交互模式运行任务
shen run "检查系统安全" --interactive

# MCP 服务管理
shen mcp list                    # 列出所有 MCP 服务
shen mcp connect service-name    # 连接到指定服务
shen mcp disconnect service-name # 断开指定服务
shen mcp tools                   # 列出所有可用工具
shen mcp tools --service fs      # 列出特定服务的工具
```

### 调试模式

```bash
# 启用调试模式
shen --debug info
```

## 开发

### 环境设置

```bash
# 安装 Poetry
pip install poetry

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行测试并查看覆盖率
poetry run pytest --cov

# 运行特定测试
poetry run pytest tests/test_cli.py
```

### 代码质量

```bash
# 格式化代码
poetry run black src tests

# 代码检查
poetry run ruff check src tests

# 类型检查
poetry run mypy src

# 运行所有检查
poetry run black src tests && poetry run ruff check src tests && poetry run mypy src
```

## MCP 集成

Shen 支持 Model Context Protocol (MCP)，允许集成各种外部服务和工具。

### 配置 MCP 服务

MCP 服务配置文件位于 `~/.shen/mcp/` 目录下。每个服务一个 JSON 配置文件：

```json
{
  "name": "filesystem",
  "description": "文件系统操作服务",
  "transport": "stdio",
  "endpoint": "npx @modelcontextprotocol/server-filesystem",
  "args": ["npx", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
  "enabled": true,
  "timeout": 30
}
```

### 常用 MCP 服务

- **文件系统服务**：文件和目录操作
- **Git 服务**：版本控制操作
- **数据库服务**：数据库查询和操作
- **Web 服务**：网页抓取和 API 调用

### MCP 命令示例

```bash
# 查看所有 MCP 服务状态
shen mcp list

# 连接到文件系统服务
shen mcp connect filesystem

# 查看可用工具
shen mcp tools

# 使用文件系统工具整理文件
shen run "使用 filesystem 服务整理下载文件夹"
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

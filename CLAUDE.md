# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Shen 是一个探索性的 AI 命令行工具项目，旨在处理编程以外的日常工作任务。项目受 Claude Code 启发，但专注于非编程领域的自动化和效率提升。

### 核心特点
- **语言**: Python
- **类型**: CLI 工具
- **集成**: 计划整合 MCP (Model Context Protocol) 服务
- **目标**: 文档整理、垃圾清理、信息提供、Office 文档制作、安全检查、软件安装等日常任务

## 项目状态

**注意**: 项目刚刚初始化，目前还没有实际代码实现。

## 开发指南

### Python 项目初始化建议

当开始实现代码时，建议：

1. 使用 `pyproject.toml` 进行项目配置
2. 使用 `poetry` 或 `pip` + `venv` 管理依赖
3. 集成代码质量工具：
   - `black` 或 `ruff` 进行代码格式化
   - `mypy` 进行类型检查
   - `pytest` 进行单元测试
   - `pre-commit` 进行提交前检查

### CLI 架构建议

基于项目目标，建议采用以下架构：

1. **命令结构**: 使用 `click` 或 `typer` 构建 CLI 界面
2. **插件系统**: 为不同任务类型（文档处理、系统管理等）设计插件架构
3. **MCP 集成**: 创建统一的 MCP 服务接口层
4. **任务管理**: 实现任务队列和并行执行能力
5. **配置管理**: 支持用户配置和任务配置

### 目录结构建议

```
shen/
├── src/
│   ├── shen/
│   │   ├── __init__.py
│   │   ├── cli.py          # CLI 入口
│   │   ├── core/           # 核心功能
│   │   ├── plugins/        # 任务插件
│   │   ├── mcp/           # MCP 集成
│   │   └── utils/         # 工具函数
├── tests/                  # 测试文件
├── docs/                   # 文档
├── pyproject.toml         # 项目配置
└── README.md
```

## 与 Claude Code 的差异化定位

根据 README.md 的描述，Shen 与 Claude Code 的主要区别：

1. **Claude Code**: 专注于编程任务（代码编写、调试、重构等）
2. **Shen**: 专注于非编程任务（文档管理、系统维护、办公自动化等）

两者都是 CLI 工具，都强调跨平台性和强大的操作权限，但应用领域不同。

## 注意事项

- 项目仍在探索阶段，架构和功能定位可能会调整
- 优先考虑安全性，特别是涉及系统操作和文件管理时
- 保持良好的错误处理和用户反馈机制
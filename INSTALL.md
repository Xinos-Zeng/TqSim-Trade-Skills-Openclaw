# 安装指南

## 前置要求

- OpenClaw 已安装 ([https://openclaw.ai](https://openclaw.ai))
- Git 和 bash

## 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/xinos-zeng/TqSim-Trade-Skills-Openclaw/main/install-from-github.sh | bash
```

## 手动安装

```bash
git clone https://github.com/xinos-zeng/TqSim-Trade-Skills-Openclaw.git
cd TqSim-Trade-Skills-Openclaw
bash install.sh
```

## 升级

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/xinos-zeng/TqSim-Trade-Skills-Openclaw/main/update.sh)
```

## 验证

安装后技能文件位于 `~/.openclaw/skills/` 目录：

```
~/.openclaw/skills/
├── run-backtest/SKILL.md
├── get-backtest-result/SKILL.md
└── list-presets/SKILL.md
```

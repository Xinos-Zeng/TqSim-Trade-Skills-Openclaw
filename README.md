# TqSim Trade Skills for OpenClaw 📊

基于天勤量化(TqSim)的期货回测与策略分析 OpenClaw 技能包。

让你的 AI Agent 能够运行期货策略回测、分析交易表现、获取策略列表。

## 更完整的功能体验

本技能包基于 **无需登录的公共 API**，适合 OpenClaw 等外部 Agent 快速调用。若你需要 **流式回测、登录后的账户与数据隔离、收藏与排行榜、与量化 Agent 的深度协作** 等完整产品体验，请使用开源前端 **OpenTrader**：

**[https://github.com/Xinos-Zeng/OpenTrader.github.io](https://github.com/Xinos-Zeng/OpenTrader.github.io)**

---

## 🎯 技能清单

| 技能 | 功能 | 触发词 |
|------|------|--------|
| `run-backtest` | 运行期货策略回测 | "回测"、"测试策略"、"backtest" |
| `get-backtest-result` | 解读回测结果 | "回测结果"、"策略表现"、"分析" |
| `list-presets` | 查询可用策略 | "有哪些策略"、"策略列表" |

## 🚀 快速开始

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/xinos-zeng/TqSim-Trade-Skills-Openclaw/main/install-from-github.sh | bash
```

### 手动安装

```bash
git clone https://github.com/xinos-zeng/TqSim-Trade-Skills-Openclaw.git
cd TqSim-Trade-Skills-Openclaw
bash install.sh
```

## 💡 使用示例

### 示例 1：回测均线策略

```
你：帮我回测一下螺纹钢的均线策略，看看2024年下半年的表现
```

Agent 将调用 `run-backtest`：
```json
{
  "symbol": "SHFE.rb2510",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "preset_id": "ma_cross"
}
```

### 示例 2：查看可用策略

```
你：有哪些策略可以回测？
```

Agent 调用 `list-presets` 并列出所有预置策略。

## 🔧 API 端点

所有端点无需认证，可直接调用：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/public/backtest` | 发起回测 |
| GET | `/api/public/presets` | 获取策略列表 |
| GET | `/api/public/health` | 健康检查 |

## 🧪 测试 & 调用示例

`tests/` 目录提供了两种测试脚本，同时也是 **Agent 调用 API 的参考示例**：

### Python 测试（推荐）

覆盖 10 项测试场景：健康检查、策略列表、预置策略回测、自定义代码回测、6 种校验失败场景。

```bash
# 测试本地服务
python tests/test_skills.py

# 测试远程服务
python tests/test_skills.py --base-url https://your-server.com

# 只测回测接口
python tests/test_skills.py --only backtest custom
```

### Shell 测试（curl 示例）

适合快速验证或作为 curl 调用参考：

```bash
# 默认测试 localhost:8000
bash tests/test_skills.sh

# 指定服务地址
bash tests/test_skills.sh https://your-server.com
```

### 测试覆盖的场景

| # | 场景 | 期望结果 |
|---|------|----------|
| 1 | 健康检查 | 200, status=ok |
| 2 | 获取预置策略列表 | 200, 返回策略数组 |
| 3 | 预置策略 (ma_cross) 回测 | 200, 含 stats + trades |
| 4 | 自定义策略代码回测 | 200, 含 stats |
| 5 | 代码未继承 BaseStrategy | 400, 校验失败 |
| 6 | 缺少 on_bar 方法 | 400, 校验失败 |
| 7 | 包含 import os (危险操作) | 400, 校验失败 |
| 8 | 日期格式错误 | 400, 提示格式 |
| 9 | 开始日期晚于结束日期 | 400, 提示范围 |
| 10 | 不存在的预置策略 ID | 400, 提示不存在 |

## 🔄 升级

当技能调用失败时，可能是版本不兼容。运行以下命令升级：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/xinos-zeng/TqSim-Trade-Skills-Openclaw/main/update.sh)
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

Made with ❤️ by AgentTrader

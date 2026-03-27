---
name: tqsim-list-presets
description: |
  列出 TqSim Trade 平台所有可用的预置量化策略。

  **使用场景**：
  - "有哪些策略可以回测"
  - "策略列表"
  - "有什么预置策略"
  - "list available strategies"

  **核心功能**：查询所有预置策略的名称、描述和默认参数，用于选择合适的策略进行回测。
metadata:
  version: 1.0.0
  author: AgentTrader
  tags: [trading, strategy, futures, list]
  openclaw:
    emoji: 📋
---

# 查询可用的预置策略

## 调用方式

```
GET {API_BASE}/api/public/presets
```

无需请求体，无需认证。

## 响应示例

```json
{
  "success": true,
  "skills_version": "1.0.0",
  "data": [
    {
      "id": "ma_cross",
      "name": "双均线交叉策略",
      "description": "经典双均线交叉策略，金叉买入，死叉卖出",
      "category": "趋势跟踪"
    },
    {
      "id": "rsi",
      "name": "RSI超买超卖策略",
      "description": "RSI 指标策略，超卖区回升买入，超买区回落卖出",
      "category": "震荡指标"
    },
    {
      "id": "bollinger",
      "name": "布林带突破策略",
      "description": "布林带均值回归策略，下轨反弹买入，上轨回落卖出",
      "category": "震荡指标"
    }
  ]
}
```

## 使用建议

获取策略列表后，可以：
1. 将 `id` 传给 `run-backtest` 的 `preset_id` 参数
2. 参考策略描述选择合适的策略
3. 基于默认参数进行调优

**说明**：当前仓库与 AgentTrader 预置策略一致时，常见 `id` 为 `ma_cross`、`rsi`、`bollinger`；若服务端升级增加了新预置项，**以接口实际返回为准**，勿仅依赖本文档中的静态示例。

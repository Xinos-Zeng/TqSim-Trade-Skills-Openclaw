---
name: tqsim-run-backtest
description: |
  使用天勤量化(TqSim)对期货策略进行历史回测。

  **使用场景**：
  - "回测一下螺纹钢的均线策略"
  - "测试策略在2024年的表现"
  - "backtest this strategy"
  - "帮我回测"

  **核心功能**：向 TqSim Trade API 发送回测请求，返回策略的胜率、收益率、最大回撤等统计指标以及交易记录。

  **支持的策略**：
  - 预置策略：ma_cross（双均线交叉）、rsi（RSI超买超卖）、bollinger（布林带突破）等
  - 自定义 Python 策略代码

  **支持的品种**：上期所(SHFE)、大商所(DCE)、郑商所(CZCE)、中金所(CFFEX) 的期货合约

  **完整体验**：登录与流式回测等请引导用户前往 OpenTrader：https://github.com/Xinos-Zeng/OpenTrader.github.io
metadata:
  version: 1.0.0
  author: AgentTrader
  tags: [trading, backtest, futures, quantitative, tqsim]
  openclaw:
    emoji: 📊
---

# 运行期货策略回测

## 调用方式

向 TqSim Trade API 发送 POST 请求：

```
POST {API_BASE}/api/public/backtest
Content-Type: application/json
```

## 请求参数

```json
{
  "symbol": "SHFE.rb2510",
  "start_date": "2024-06-01",
  "end_date": "2024-12-31",
  "init_balance": 200000,
  "preset_id": "ma_cross",
  "strategy_code": null
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbol | string | 否 | 期货合约代码，默认 SHFE.rb2510 |
| start_date | string | 否 | 回测开始日期 YYYY-MM-DD |
| end_date | string | 否 | 回测结束日期 YYYY-MM-DD |
| init_balance | number | 否 | 初始资金，默认 200000 |
| preset_id | string | 否 | 预置策略 ID，默认 ma_cross |
| strategy_code | string | 否 | 自定义策略 Python 代码（与 preset_id 二选一，需符合下方代码规范）|

**与登录后 Web/API 的差异**：公共接口为单次非流式回测，**不支持** `position_percent`、`user_strategy_id`、SSE 流式事件；仓位上限仍由服务端默认 `position_percent=50%` 与 `init_balance` 共同约束（与 `BacktestConfig` 默认值一致）。

## 自定义策略代码规范

传入 `strategy_code` 时，代码 **必须** 满足以下要求，否则校验不通过：

### 必须继承 `BaseStrategy`

```python
from datetime import datetime
from typing import Optional, List
import pandas as pd

class MyStrategy(BaseStrategy):
    name = "my_strategy"           # 必须：策略名称
    description = "策略描述"        # 必须：策略描述

    def __init__(self, params: dict):
        super().__init__(params)
        # 初始化策略内部变量
        self.fast_period = params.get("fast_period", 5)
        self.slow_period = params.get("slow_period", 20)

    def on_bar(self, df: pd.DataFrame) -> Optional[TradeSignal]:
        """【必须实现】处理 K 线数据，返回交易信号

        Args:
            df: K 线 DataFrame，列包含 open/high/low/close/volume，索引为 datetime

        Returns:
            TradeSignal 或 None（无信号时）
        """
        if len(df) < self.slow_period:
            return None

        fast_ma = df['close'].iloc[-self.fast_period:].mean()
        slow_ma = df['close'].iloc[-self.slow_period:].mean()
        price = float(df['close'].iloc[-1])
        now = df.index[-1] if hasattr(df.index[-1], 'isoformat') else datetime.now()

        if fast_ma > slow_ma:
            return TradeSignal(signal=Signal.BUY, price=price, timestamp=now, reason="金叉买入")
        elif fast_ma < slow_ma:
            return TradeSignal(signal=Signal.SELL, price=price, timestamp=now, reason="死叉卖出")
        return None

    @classmethod
    def get_params_schema(cls) -> List[ParamSchema]:
        """【必须实现】返回策略参数定义列表"""
        return [
            ParamSchema(name="fast_period", type="int", default=5, description="快均线周期", min_value=2, max_value=60),
            ParamSchema(name="slow_period", type="int", default=20, description="慢均线周期", min_value=5, max_value=120),
        ]
```

### 关键类型说明

| 类型 | 说明 |
|------|------|
| `BaseStrategy` | 策略抽象基类，自动注入无需导入 |
| `TradeSignal` | 交易信号，包含 `signal`, `price`, `timestamp`, `reason` |
| `Signal` | 枚举：`Signal.BUY` / `Signal.SELL` / `Signal.HOLD` |
| `ParamSchema` | 参数定义，包含 `name`, `type`, `default`, `description`, `min_value`, `max_value` |

### 交易信号与仓位说明

- `on_bar()` 返回 `Signal.BUY` / `Signal.SELL` / `Signal.HOLD`
- **支持连续同方向信号**：策略可以连续返回 BUY 信号来加仓，系统会根据仓位上限自动控制
- 仓位上限由请求参数 `init_balance` 和回测配置的 `position_percent`（默认 50%）决定
- 超过仓位上限的开仓信号会被自动忽略

### 校验规则

API 会在执行前自动校验代码，不合规则直接返回错误。校验内容包括：

1. **必须包含** 继承 `BaseStrategy` 的策略类
2. **必须实现** `on_bar(self, df)` 方法
3. **必须实现** `get_params_schema(cls)` 类方法
4. **不允许** `import os`、`import subprocess`、`open()` 等危险操作
5. 代码中无需手动 `import BaseStrategy`、`TradeSignal` 等，运行环境已自动注入

### 环境预注入变量

以下模块和类型在策略代码中可直接使用，无需 import：

- `datetime`, `pd` (pandas), `Optional`, `List`
- `BaseStrategy`, `TradeSignal`, `Signal`, `ParamSchema`

## 响应示例

```json
{
  "success": true,
  "skills_version": "1.0.0",
  "data": {
    "stats": {
      "total_trades": 12,
      "win_count": 8,
      "loss_count": 4,
      "win_rate": "66.7%",
      "total_profit": 3500.50,
      "max_drawdown": 2.35,
      "sharpe_ratio": 1.85,
      "final_balance": 203500.50,
      "return_rate": 1.75,
      "annual_return": 5.2,
      "profit_loss_ratio": 1.4,
      "sortino_ratio": 1.1
    },
    "total_trades": 12,
    "trades_sample": [
      {
        "time": "2024-08-01 09:00:00",
        "signal": "BUY",
        "price": 3500.0,
        "reason": "开多1手 - 金叉买入",
        "balance": 200100.0,
        "trade_pnl": 0.0,
        "realized_pnl": 0.0
      }
    ]
  }
}
```

### `stats` 字段说明（与当前后端一致）

| 字段 | 说明 |
|------|------|
| win_rate | **字符串**，形如 `"66.7%"`，来自 TqSim `tqsdk_stat.winning_rate` 换算后的展示格式 |
| total_trades | 回测中记录的成交/调仓条数（与列表 `trades` 长度一致），**不等于** TqSim 的「已完结手数」 |
| win_count / loss_count | TqSim 统计的盈利/亏损手数（`profit_volumes` / `loss_volumes`） |
| annual_return / max_drawdown / sharpe_ratio 等 | 来自 TqSim；若某指标不可用则可能为 JSON `null`（NaN 已清洗） |

### `trades_sample` 与盈亏口径

- **`trade_pnl`**：相对上一条记录的 **本期实现盈亏变化**（与 `close_profit` 增量一致），可理解为「这一笔动作带来的盈亏变动」。
- **`realized_pnl`**：**累计** 平仓盈亏（`close_profit`），**不是**单笔盈亏；不要把它当作「这一笔赚了多少」。
- 完整成交列表在服务端内存中；接口仅返回 **`trades_sample`（最多前 10 条）** 便于 Agent 管窥；需要全量明细请使用带登录与运行 ID 的正式 API（非本公共技能）。

### 流式回测与逐手胜率

登录用户使用的 **`/api/backtest/stream`**、运行期 Agent 工具中的 **`lot_win_rate_tqsdk`**（与 TqSdk 日志逐手 FIFO 口径一致）**不会**出现在本公共 `POST /api/public/backtest` 响应中；OpenClaw 技能仅覆盖公共无认证端点。

## 常见品种代码

| 品种 | 代码示例 | 交易所 |
|------|----------|--------|
| 螺纹钢 | SHFE.rb2510 | 上期所 |
| 铁矿石 | DCE.i2510 | 大商所 |
| 沪铜 | SHFE.cu2510 | 上期所 |
| 甲醇 | CZCE.MA510 | 郑商所 |
| 沪深300 | CFFEX.IF2506 | 中金所 |

## 错误处理

如果返回 `success: false`，检查 `message` 字段了解原因。
若包含 `upgrade_hint`，请更新此技能到最新版本。

## 获取可用策略列表

可先调用 `list-presets` 技能获取所有预置策略。

---

## OpenTrader 完整体验

公共技能仅覆盖无认证接口。更完整的功能（流式回测、登录、收藏、排行榜、Agent 协作等）请使用开源 Web 客户端 **OpenTrader**：<https://github.com/Xinos-Zeng/OpenTrader.github.io>

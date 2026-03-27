#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  TqSim Trade Skills — curl 快速测试 / Agent 调用示例
#
#  用法:
#    ./tests/test_skills.sh                         # 默认 localhost:8000
#    ./tests/test_skills.sh https://your-server.com # 指定地址
# ─────────────────────────────────────────────────────────

BASE="${1:-http://localhost:8000}"
PASS=0; FAIL=0

green() { printf "\033[32m%s\033[0m" "$1"; }
red()   { printf "\033[31m%s\033[0m" "$1"; }

check() {
  local label="$1" expect_code="$2" actual_code="$3" body="$4"
  if [ "$actual_code" = "$expect_code" ]; then
    printf "  %s  %s\n" "$(green PASS)" "$label"
    PASS=$((PASS+1))
  else
    printf "  %s  %s (期望 %s, 实际 %s)\n" "$(red FAIL)" "$label" "$expect_code" "$actual_code"
    echo "        $body" | head -c 200
    echo
    FAIL=$((FAIL+1))
  fi
}

echo "╔══════════════════════════════════════════════╗"
echo "║  TqSim Trade Skills — curl 快速测试          ║"
echo "║  服务地址: $BASE"
echo "╚══════════════════════════════════════════════╝"

# ────── 1. 健康检查 ──────
echo ""
echo "[1] GET /api/public/health"
RESP=$(curl -s -w "\n%{http_code}" "$BASE/api/public/health")
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "健康检查" 200 "$CODE" "$BODY"

# ────── 2. 获取预置策略列表 ──────
echo ""
echo "[2] GET /api/public/presets"
RESP=$(curl -s -w "\n%{http_code}" "$BASE/api/public/presets")
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "获取预置策略列表" 200 "$CODE" "$BODY"
echo "        响应片段: $(echo "$BODY" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(", ".join(p["id"] for p in d.get("data",[])))' 2>/dev/null || echo "$BODY" | head -c 120)"

# ────── 3. 预置策略回测 ──────
echo ""
echo "[3] POST /api/public/backtest — 预置策略"
RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "SHFE.rb2510",
    "start_date": "2024-06-01",
    "end_date": "2024-12-31",
    "init_balance": 200000,
    "preset_id": "ma_cross"
  }')
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "预置策略回测" 200 "$CODE" "$BODY"
echo "        统计: $(echo "$BODY" | python3 -c '
import sys, json
d = json.load(sys.stdin).get("data",{}).get("stats",{})
print(f"交易={d.get(\"total_trades\")}, 胜率={d.get(\"win_rate\")}, 收益率={d.get(\"return_rate\")}, 夏普={d.get(\"sharpe_ratio\")}")
' 2>/dev/null || echo '(解析失败)')"

# ────── 4. 自定义策略代码回测 ──────
echo ""
echo "[4] POST /api/public/backtest — 自定义策略代码"

read -r -d '' STRATEGY_CODE << 'PYEOF'
class SimpleMA(BaseStrategy):
    name = "simple_ma_test"
    description = "测试用均线策略"

    def __init__(self, params: dict):
        super().__init__(params)
        self.period = params.get("period", 10)

    def on_bar(self, df) -> Optional[TradeSignal]:
        if len(df) < self.period:
            return None
        ma = df["close"].iloc[-self.period:].mean()
        price = float(df["close"].iloc[-1])
        now = df.index[-1] if hasattr(df.index[-1], "isoformat") else datetime.now()
        if price > ma:
            return TradeSignal(signal=Signal.BUY, price=price, timestamp=now, reason="上穿均线")
        elif price < ma:
            return TradeSignal(signal=Signal.SELL, price=price, timestamp=now, reason="下穿均线")
        return None

    @classmethod
    def get_params_schema(cls) -> List[ParamSchema]:
        return [
            ParamSchema(name="period", type="int", default=10, description="均线周期", min_value=2, max_value=120),
        ]
PYEOF

# 构造 JSON（strategy_code 字段需要正确转义）
JSON_BODY=$(python3 -c "
import json
code = '''$STRATEGY_CODE'''
print(json.dumps({
    'symbol': 'SHFE.rb2510',
    'start_date': '2024-09-01',
    'end_date': '2024-12-31',
    'init_balance': 200000,
    'strategy_code': code
}))
")

RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY")
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "自定义策略代码回测" 200 "$CODE" "$BODY"

# ────── 5. 校验 — 无 BaseStrategy 继承 ──────
echo ""
echo "[5] 校验 — 未继承 BaseStrategy"
RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "class Foo:\n    pass\n"}')
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "拒绝无效策略代码" 400 "$CODE" "$BODY"

# ────── 6. 校验 — 危险 import ──────
echo ""
echo "[6] 校验 — 包含 import os"
RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "import os\nclass E(BaseStrategy):\n    name=\"e\"\n    description=\"e\"\n    def on_bar(self,df): return None\n    @classmethod\n    def get_params_schema(cls): return []\n"}')
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "拒绝危险代码" 400 "$CODE" "$BODY"

# ────── 7. 校验 — 日期格式错误 ──────
echo ""
echo "[7] 校验 — 日期格式错误"
RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "bad-date"}')
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "拒绝错误日期" 400 "$CODE" "$BODY"

# ────── 8. 校验 — 不存在的策略 ID ──────
echo ""
echo "[8] 校验 — 不存在的预置策略 ID"
RESP=$(curl -s -w "\n%{http_code}" \
  -X POST "$BASE/api/public/backtest" \
  -H "Content-Type: application/json" \
  -d '{"preset_id": "no_such_strategy"}')
CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
check "拒绝不存在的策略" 400 "$CODE" "$BODY"

# ────── 汇总 ──────
echo ""
echo "================================================"
printf "总计: %d 项, $(green "$PASS 通过")" $((PASS+FAIL))
if [ "$FAIL" -gt 0 ]; then
  printf ", $(red "$FAIL 失败")"
fi
echo ""
echo "================================================"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1

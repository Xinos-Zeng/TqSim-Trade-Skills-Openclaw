#!/usr/bin/env python3
"""TqSim Trade Skills 接口测试脚本

覆盖全部公共 API 端点，同时作为 Agent 调用示例。

使用方法：
    # 测试本地服务（默认 http://localhost:8000）
    python tests/test_skills.py

    # 测试远程服务
    python tests/test_skills.py --base-url https://your-server.example.com

    # 只跑某一组
    python tests/test_skills.py --only backtest
"""
import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEFAULT_BASE = "http://localhost:8000"

# ────────────────────── 工具函数 ──────────────────────

def api(method: str, path: str, body: dict | None = None, *, base: str) -> tuple[int, dict]:
    """发送请求并返回 (status_code, json_body)"""
    url = f"{base}{path}"
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urlopen(req, timeout=120)
        return resp.status, json.loads(resp.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())


def ok(label: str):
    print(f"  \033[32mPASS\033[0m  {label}")


def fail(label: str, detail: str = ""):
    print(f"  \033[31mFAIL\033[0m  {label}")
    if detail:
        print(f"        {detail}")


def assert_eq(label: str, actual, expected):
    if actual == expected:
        ok(label)
        return True
    fail(label, f"expected {expected!r}, got {actual!r}")
    return False


def assert_true(label: str, cond: bool, detail: str = ""):
    if cond:
        ok(label)
        return True
    fail(label, detail)
    return False


# ────────────────────── 测试用例 ──────────────────────

def test_health(base: str) -> list[bool]:
    """测试健康检查端点"""
    print("\n[1] GET /api/public/health")
    code, data = api("GET", "/api/public/health", base=base)
    return [
        assert_eq("状态码 200", code, 200),
        assert_eq("status=ok", data.get("status"), "ok"),
        assert_true("含 skills_version", "skills_version" in data),
    ]


def test_list_presets(base: str) -> list[bool]:
    """测试预置策略列表"""
    print("\n[2] GET /api/public/presets")
    code, data = api("GET", "/api/public/presets", base=base)
    presets = data.get("data", [])
    results = [
        assert_eq("状态码 200", code, 200),
        assert_eq("success=true", data.get("success"), True),
        assert_true("至少有 1 个预置策略", len(presets) >= 1, f"got {len(presets)}"),
    ]
    if presets:
        first = presets[0]
        results.append(assert_true("策略含 id 字段", "id" in first))
        results.append(assert_true("策略含 name 字段", "name" in first))
        print(f"        可用策略: {', '.join(p['id'] for p in presets)}")
    return results


def test_backtest_preset(base: str) -> list[bool]:
    """测试预置策略回测"""
    print("\n[3] POST /api/public/backtest — 预置策略 (ma_cross)")
    body = {
        "symbol": "SHFE.rb2510",
        "start_date": "2024-06-01",
        "end_date": "2024-12-31",
        "init_balance": 200000,
        "preset_id": "ma_cross",
    }
    t0 = time.time()
    code, data = api("POST", "/api/public/backtest", body, base=base)
    elapsed = time.time() - t0
    print(f"        耗时: {elapsed:.1f}s")

    results = [
        assert_eq("状态码 200", code, 200),
        assert_eq("success=true", data.get("success"), True),
    ]
    d = data.get("data", {})
    stats = d.get("stats", {})
    results.append(assert_true("含 stats 对象", bool(stats), f"data={d}"))
    results.append(assert_true("含 total_trades", "total_trades" in d))
    results.append(assert_true("含 trades_sample 数组", isinstance(d.get("trades_sample"), list)))

    if stats:
        print(f"        回测统计: 交易={stats.get('total_trades')}, 胜率={stats.get('win_rate')}, "
              f"收益率={stats.get('return_rate')}, 夏普={stats.get('sharpe_ratio')}")
    return results


CUSTOM_STRATEGY_VALID = '''\
class SimpleMA(BaseStrategy):
    """简单均线策略 - 用于接口测试"""
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
            return TradeSignal(signal=Signal.BUY, price=price, timestamp=now, reason="价格上穿均线")
        elif price < ma:
            return TradeSignal(signal=Signal.SELL, price=price, timestamp=now, reason="价格下穿均线")
        return None

    @classmethod
    def get_params_schema(cls) -> List[ParamSchema]:
        return [
            ParamSchema(name="period", type="int", default=10, description="均线周期", min_value=2, max_value=120),
        ]
'''


def test_backtest_custom_code(base: str) -> list[bool]:
    """测试自定义策略代码回测"""
    print("\n[4] POST /api/public/backtest — 自定义策略代码")
    body = {
        "symbol": "SHFE.rb2510",
        "start_date": "2024-09-01",
        "end_date": "2024-12-31",
        "init_balance": 200000,
        "strategy_code": CUSTOM_STRATEGY_VALID,
    }
    t0 = time.time()
    code, data = api("POST", "/api/public/backtest", body, base=base)
    elapsed = time.time() - t0
    print(f"        耗时: {elapsed:.1f}s")

    results = [
        assert_eq("状态码 200", code, 200),
        assert_eq("success=true", data.get("success"), True),
    ]
    d = data.get("data", {})
    stats = d.get("stats", {})
    results.append(assert_true("含 stats 对象", bool(stats), f"data={d}"))

    if stats:
        print(f"        回测统计: 交易={stats.get('total_trades')}, 胜率={stats.get('win_rate')}, "
              f"收益率={stats.get('return_rate')}")
    return results


# ────────────── 校验失败场景 ──────────────

def test_validate_no_base_class(base: str) -> list[bool]:
    """校验：代码未继承 BaseStrategy"""
    print("\n[5] 校验 — 未继承 BaseStrategy")
    body = {
        "strategy_code": "class Foo:\n    pass\n",
    }
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_eq("success=false", data.get("success"), False),
        assert_true("错误消息含校验提示", "校验失败" in data.get("message", ""), data.get("message", "")),
        assert_true("含 upgrade_hint", "upgrade_hint" in data),
    ]


def test_validate_missing_on_bar(base: str) -> list[bool]:
    """校验：缺少 on_bar 方法"""
    print("\n[6] 校验 — 缺少 on_bar 方法")
    body = {
        "strategy_code": (
            'class Bad(BaseStrategy):\n'
            '    name = "bad"\n'
            '    description = "no on_bar"\n'
            '    @classmethod\n'
            '    def get_params_schema(cls):\n'
            '        return []\n'
        ),
    }
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_eq("success=false", data.get("success"), False),
        assert_true("错误消息提到 on_bar 或校验", "on_bar" in data.get("message", "") or "校验" in data.get("message", ""),
                    data.get("message", "")),
    ]


def test_validate_dangerous_import(base: str) -> list[bool]:
    """校验：包含危险 import"""
    print("\n[7] 校验 — 包含 import os（危险操作）")
    body = {
        "strategy_code": (
            'import os\n'
            'class Evil(BaseStrategy):\n'
            '    name = "evil"\n'
            '    description = "danger"\n'
            '    def on_bar(self, df):\n'
            '        os.system("echo hacked")\n'
            '        return None\n'
            '    @classmethod\n'
            '    def get_params_schema(cls):\n'
            '        return []\n'
        ),
    }
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_eq("success=false", data.get("success"), False),
        assert_true("错误消息含安全提示", "校验失败" in data.get("message", "") or "安全" in data.get("message", ""),
                    data.get("message", "")),
    ]


def test_validate_bad_dates(base: str) -> list[bool]:
    """校验：日期格式错误"""
    print("\n[8] 校验 — 日期格式错误")
    body = {"start_date": "not-a-date", "end_date": "2024-12-31"}
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_true("提示日期格式", "日期" in data.get("message", ""), data.get("message", "")),
    ]


def test_validate_date_range(base: str) -> list[bool]:
    """校验：开始日期晚于结束日期"""
    print("\n[9] 校验 — 开始日期晚于结束日期")
    body = {"start_date": "2025-01-01", "end_date": "2024-01-01"}
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_true("提示日期范围", "早于" in data.get("message", ""), data.get("message", "")),
    ]


def test_validate_bad_preset(base: str) -> list[bool]:
    """校验：不存在的预置策略"""
    print("\n[10] 校验 — 不存在的预置策略 ID")
    body = {"preset_id": "nonexistent_strategy_xyz"}
    code, data = api("POST", "/api/public/backtest", body, base=base)
    return [
        assert_eq("状态码 400", code, 400),
        assert_true("提示策略不存在", "不存在" in data.get("message", ""), data.get("message", "")),
    ]


# ────────────────────── 主入口 ──────────────────────

ALL_TESTS = {
    "health":       test_health,
    "presets":      test_list_presets,
    "backtest":     test_backtest_preset,
    "custom":       test_backtest_custom_code,
    "no_base":      test_validate_no_base_class,
    "no_on_bar":    test_validate_missing_on_bar,
    "dangerous":    test_validate_dangerous_import,
    "bad_dates":    test_validate_bad_dates,
    "date_range":   test_validate_date_range,
    "bad_preset":   test_validate_bad_preset,
}


def main():
    parser = argparse.ArgumentParser(description="TqSim Trade Skills 接口测试")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help=f"API 服务地址 (默认 {DEFAULT_BASE})")
    parser.add_argument("--only", choices=list(ALL_TESTS.keys()), nargs="+",
                        help="只运行指定的测试（可多选）")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    tests = {k: ALL_TESTS[k] for k in args.only} if args.only else ALL_TESTS

    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  TqSim Trade Skills 接口测试                ║")
    print(f"║  服务地址: {base:<34s}║")
    print(f"║  测试用例: {len(tests):<34d}║")
    print(f"╚══════════════════════════════════════════════╝")

    # 连通性检查
    print("\n[0] 连通性检查 ...")
    try:
        api("GET", "/api/public/health", base=base)
        ok("服务可达")
    except (URLError, OSError) as e:
        fail("服务不可达", str(e))
        print(f"\n请确认服务已启动并监听在 {base}")
        sys.exit(1)

    total = 0
    passed = 0
    failed_names = []

    for name, fn in tests.items():
        try:
            results = fn(base)
            total += len(results)
            pass_count = sum(results)
            passed += pass_count
            if pass_count < len(results):
                failed_names.append(name)
        except Exception as e:
            print(f"  \033[31mERROR\033[0m  {name}: {e}")
            total += 1
            failed_names.append(name)

    # 汇总
    print(f"\n{'='*48}")
    print(f"总计: {total} 项断言, \033[32m{passed} 通过\033[0m", end="")
    if total - passed > 0:
        print(f", \033[31m{total - passed} 失败\033[0m ({', '.join(failed_names)})")
    else:
        print()
    print(f"{'='*48}")

    sys.exit(0 if not failed_names else 1)


if __name__ == "__main__":
    main()

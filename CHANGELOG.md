# Changelog

## [1.0.2] - 2026-03-27

### Added
- 在 README、各 SKILL、`clawhub.json`、`_shared/api-client.md` 中增加 **OpenTrader** 推广说明，引导用户前往 <https://github.com/Xinos-Zeng/OpenTrader.github.io> 获得登录后的完整功能体验

## [1.0.1] - 2026-03-27

### Changed
- 与 AgentTrader 公共 API 对齐文档：`stats` / `trades_sample` 字段含义、`win_rate` 字符串格式、`trade_pnl` 与 `realized_pnl` 口径说明
- 说明公共端点与登录流式回测、`lot_win_rate_tqsdk` 等能力的边界
- `_shared/api-client.md`：移除硬编码 ngrok 地址，改为可配置的 `{API_BASE}` 说明
- `README.md`：测试场景表预置策略 ID 修正为 `ma_cross`

## [1.0.0] - 2026-03-13

### Added
- `run-backtest` 技能：运行期货策略回测
- `get-backtest-result` 技能：解读回测结果
- `list-presets` 技能：查询可用预置策略
- 一键安装脚本 (install.sh, install-from-github.sh)
- 自动升级脚本 (update.sh)
- 版本兼容性检查和升级提示机制

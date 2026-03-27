# TqSim Trade API 调用指南

## 服务地址

地址: `https://6ed3-43-136-74-85.ngrok-free.app`

所有公共 API 在 `/api/public/` 路径下，无需认证。

## 通用约定

- 请求格式: JSON
- 响应格式: JSON，包含 `success` 布尔值和 `data` 对象
- 每个响应包含 `skills_version` 用于版本兼容性检查
- 若返回 `upgrade_hint`，说明应更新技能到最新版本

## 错误处理

若 API 返回非 200 状态码或 `success: false`，检查 `upgrade_hint` 字段。
如有升级提示，请运行：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/xinos-zeng/TqSim-Trade-Skills-Openclaw/main/update.sh)
```

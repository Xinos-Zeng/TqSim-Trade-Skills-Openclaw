#!/bin/bash
# TqSim Trade Skills 安装脚本
set -e

SKILLS_DIR="${HOME}/.openclaw/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 安装 TqSim Trade Skills..."

for skill_dir in run-backtest get-backtest-result list-presets; do
  target="${SKILLS_DIR}/${skill_dir}"
  mkdir -p "${target}"
  cp "${SCRIPT_DIR}/${skill_dir}/SKILL.md" "${target}/SKILL.md"
  echo "  ✅ ${skill_dir}"
done

# 安装共享文件
mkdir -p "${SKILLS_DIR}/_tqsim-shared"
cp "${SCRIPT_DIR}/_shared/api-client.md" "${SKILLS_DIR}/_tqsim-shared/api-client.md"

echo ""
echo "✨ 安装完成！已安装 3 个技能到 ${SKILLS_DIR}"
echo ""
echo "技能列表："
echo "  📊 run-backtest     - 运行期货策略回测"
echo "  📈 get-backtest-result - 解读回测结果"
echo "  📋 list-presets     - 查询可用策略"

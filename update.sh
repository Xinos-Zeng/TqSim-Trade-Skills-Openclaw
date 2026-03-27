#!/bin/bash
# TqSim Trade Skills 升级脚本
set -e

REPO="xinos-zeng/TqSim-Trade-Skills-Openclaw"
BRANCH="main"
TMP_DIR=$(mktemp -d)

echo "🔄 更新 TqSim Trade Skills..."

git clone --depth 1 "https://github.com/${REPO}.git" -b "${BRANCH}" "${TMP_DIR}"

cd "${TMP_DIR}"
bash install.sh

rm -rf "${TMP_DIR}"

echo ""
echo "✅ 更新完成！技能已是最新版本。"

#!/bin/bash
# 从 GitHub 一键安装 TqSim Trade Skills
set -e

REPO="xinos-zeng/TqSim-Trade-Skills-Openclaw"
BRANCH="main"
TMP_DIR=$(mktemp -d)
SKILLS_DIR="${HOME}/.openclaw/skills"

echo "🚀 从 GitHub 安装 TqSim Trade Skills..."

git clone --depth 1 "https://github.com/${REPO}.git" -b "${BRANCH}" "${TMP_DIR}"

cd "${TMP_DIR}"
bash install.sh

rm -rf "${TMP_DIR}"

echo ""
echo "🎉 安装完成！"

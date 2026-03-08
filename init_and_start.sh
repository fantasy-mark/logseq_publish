#!/bin/bash
# Logseq Publish - 初始化和启动脚本

set -e

PROJECT_DIR="/home/admin/project/logseq_publish_app"
LOGSEQ_DIR="/home/admin/project/logseq_publish"

echo "🚀 初始化并启动 Logseq Publish 服务..."
echo ""

# 检查 Git 仓库
if [ ! -d "$LOGSEQ_DIR/.git" ]; then
    echo "❌ Logseq 仓库不存在，请先克隆："
    echo "   git clone https://github.com/fantasy-mark/logseq_publish $LOGSEQ_DIR"
    exit 1
fi

# 检查 Git 配置
echo "📦 检查 Git 配置..."
cd "$LOGSEQ_DIR"
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  配置 Git 用户信息..."
    git config user.name "Logseq Publish"
    git config user.email "logseq@local"
fi

# 检查后端依赖
echo ""
echo "📦 检查后端依赖..."
pip3 install -q flask flask-cors markdown 2>/dev/null || {
    echo "⚠️  请手动安装：pip3 install flask flask-cors markdown"
}

# 检查前端依赖
echo ""
echo "📦 检查前端依赖..."
if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "▶️  安装前端依赖..."
    cd "$PROJECT_DIR/frontend"
    npm install
fi

# 启动服务
echo ""
cd "$PROJECT_DIR"
./start-services.sh

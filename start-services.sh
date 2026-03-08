#!/bin/bash
# Logseq Publish - 服务启动脚本

set -e

PROJECT_DIR="/home/admin/project/logseq_publish_app"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 启动 Logseq Publish 服务..."
echo ""

# 检查后端服务
echo "📦 检查后端服务..."
if netstat -tlnp | grep 11669 > /dev/null 2>&1; then
    echo "⚠️  后端服务已在运行 (端口 11669)"
else
    echo "▶️  启动后端服务 (端口 11669)..."
    cd "$BACKEND_DIR"
    nohup python3 app.py --port 11669 > /tmp/logseq_backend.log 2>&1 &
    sleep 2
    if netstat -tlnp | grep 11669 > /dev/null 2>&1; then
        echo "✅ 后端服务已启动"
    else
        echo "❌ 后端服务启动失败，请检查日志：/tmp/logseq_backend.log"
        exit 1
    fi
fi

# 检查前端服务
echo ""
echo "📦 检查前端服务..."
if netstat -tlnp | grep 11668 > /dev/null 2>&1; then
    echo "⚠️  前端服务已在运行 (端口 11668)"
else
    echo "▶️  启动前端服务 (端口 11668)..."
    cd "$FRONTEND_DIR"
    nohup npm run preview -- --host 0.0.0.0 --port 11668 > /tmp/logseq_frontend.log 2>&1 &
    sleep 3
    if netstat -tlnp | grep 11668 > /dev/null 2>&1; then
        echo "✅ 前端服务已启动"
    else
        echo "❌ 前端服务启动失败，请检查日志：/tmp/logseq_frontend.log"
        exit 1
    fi
fi

echo ""
echo "========================================="
echo "✅ 所有服务启动完成！"
echo "========================================="
echo ""
echo "🌐 访问地址:"
echo "   本地：http://localhost:11668"
echo "   外网：http://47.102.152.55:11668"
echo ""
echo "📋 服务状态:"
echo "   后端：http://localhost:11669 (Flask)"
echo "   前端：http://localhost:11668 (Vite)"
echo ""
echo "📂 Pages 目录：/home/admin/project/logseq_publish/pages"
echo "📦 Git 仓库：/home/admin/project/logseq_publish"
echo ""
echo "🛑 停止服务：./stop-services.sh"
echo "========================================="

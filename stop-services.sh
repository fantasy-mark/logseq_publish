#!/bin/bash
# Logseq Publish - 服务停止脚本

echo "🛑 停止 Logseq Publish 服务..."

# 停止前端
echo "⏹️  停止前端服务..."
pkill -f "vite preview.*11668" 2>/dev/null || true

# 停止后端
echo "⏹️  停止后端服务..."
pkill -f "python3 app.py.*11669" 2>/dev/null || true

sleep 1

# 检查是否已停止
if ! lsof -i:11668 > /dev/null 2>&1 && ! lsof -i:11669 > /dev/null 2>&1; then
    echo "✅ 所有服务已停止"
else
    echo "⚠️  部分服务仍在运行，请手动检查"
    lsof -i:11668 2>/dev/null || true
    lsof -i:11669 2>/dev/null || true
fi

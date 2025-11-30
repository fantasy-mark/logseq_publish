#!/bin/bash
set -e                 # 任何一步出错就退出

git add .
git commit -m "add2push" || true
git push

# —— 提示信息 ——
echo
echo "✅ 推送完成！GitHub Pages 正在后台构建 …"
echo "   构建进度 →  https://github.com/fantasy-mark/logseq_publish/actions"
echo "   在线预览 →  https://fantasy-mark.github.io/logseq_publish/"
echo
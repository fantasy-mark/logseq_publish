#!/usr/bin/env python3
"""
Logseq Publish Web Application
通过浏览器编辑 pages 目录中的 Markdown 文件，并提交到 GitHub

运行方式:
    python3 app.py
    
访问：http://localhost:11668
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, make_response
from flask_cors import CORS
import markdown

app = Flask(__name__)
CORS(app, origins=['*'], supports_credentials=True)

# 配置
LOGSEQ_PUBLISH_DIR = "/home/admin/project/logseq_publish"
PAGES_DIR = os.path.join(LOGSEQ_PUBLISH_DIR, "pages")
PORT = 11669
HOST = "0.0.0.0"

# 完整的 HTML 模板（用于调试页面）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Logseq Publish</title>
    <style>
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --accent: #e94560;
            --accent-hover: #ff6b6b;
            --success: #4ecca3;
            --warning: #ffc107;
            --border: #2a2a4a;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        header {
            background: var(--bg-secondary);
            padding: 20px 0;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 30px;
        }
        
        header h1 { color: var(--accent); font-size: 1.8rem; }
        .path-info { color: var(--text-secondary); font-size: 0.9rem; margin-top: 5px; }
        
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .file-card {
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid var(--border);
            text-decoration: none;
            color: inherit;
            display: block;
        }
        
        .file-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent);
            box-shadow: 0 5px 20px rgba(233, 69, 96, 0.2);
        }
        
        .file-card .filename {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--success);
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        .file-card .meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .markdown-content {
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 40px;
            line-height: 1.8;
        }
        
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
            color: var(--accent);
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }
        
        .markdown-content h1 { border-bottom: 2px solid var(--accent); padding-bottom: 10px; }
        .markdown-content h2 { border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        .markdown-content p { margin-bottom: 1em; }
        .markdown-content code {
            background: var(--bg-primary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', Consolas, monospace;
            font-size: 0.9em;
        }
        .markdown-content pre {
            background: var(--bg-primary);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1em 0;
            border: 1px solid var(--border);
        }
        .markdown-content pre code { background: none; padding: 0; }
        .markdown-content a { color: var(--success); }
        
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--accent);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .back-btn:hover { background: var(--accent-hover); }
        
        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📚 {{ title }}</h1>
            <div class="path-info">{{ path_info }}</div>
        </div>
    </header>
    
    <main class="container">
        {% if view == 'list' %}
        <div class="file-list">
            {% for file in files %}
            <a href="/view/{{ file.name }}" class="file-card">
                <div class="filename">📄 {{ file.name }}</div>
                <div class="meta">
                    <span>📅 {{ file.mtime }}</span>
                    <span class="size">📦 {{ file.size }}</span>
                </div>
            </a>
            {% endfor %}
        </div>
        
        {% if not files %}
        <div class="empty-state">
            <h2>📂 目录为空</h2>
            <p>将 Markdown 文件放置到 {{ pages_dir }}</p>
        </div>
        {% endif %}
        
        {% elif view == 'file' %}
        <a href="/" class="back-btn">← 返回列表</a>
        <div class="markdown-content">{{ html_content|safe }}</div>
        {% endif %}
    </main>
</body>
</html>
"""


def format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def format_mtime(mtime: float) -> str:
    """格式化修改时间"""
    dt = datetime.fromtimestamp(mtime)
    return dt.strftime("%Y-%m-%d %H:%M")


def get_markdown_files(pages_dir: str = None) -> list:
    """获取所有 Markdown 文件"""
    if pages_dir is None:
        pages_dir = PAGES_DIR
    
    pages_path = Path(pages_dir)
    if not pages_path.exists():
        pages_path.mkdir(parents=True, exist_ok=True)
        return []
    
    files = []
    for f in pages_path.glob("*.md"):
        if f.is_file():
            stat = f.stat()
            files.append({
                'name': f.name,
                'path': str(f),
                'size': format_file_size(stat.st_size),
                'mtime': format_mtime(stat.st_mtime),
                'mtime_ts': stat.st_mtime
            })
    
    files.sort(key=lambda x: x['name'].lower())
    return files


def render_markdown(content: str) -> str:
    """渲染 Markdown 为 HTML"""
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'tables', 'fenced_code', 'nl2br'])
    return md.convert(content)


def run_git_command(cmd: list, cwd: str = None) -> tuple:
    """运行 Git 命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or LOGSEQ_PUBLISH_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)


def get_git_status() -> dict:
    """获取 Git 仓库状态"""
    success, stdout, stderr = run_git_command(['git', 'status', '--porcelain'])
    if not success:
        return {'status': 'error', 'message': stderr}
    
    changes = []
    for line in stdout.split('\n'):
        if line.strip():
            changes.append(line.strip())
    
    return {
        'status': 'clean' if not changes else 'modified',
        'changes': changes
    }


def commit_and_push(message: str, files: list = None) -> dict:
    """提交并推送到 GitHub"""
    # 添加文件
    if files:
        for f in files:
            success, stdout, stderr = run_git_command(['git', 'add', f])
            if not success:
                return {'success': False, 'message': f'Failed to add {f}: {stderr}'}
    else:
        success, stdout, stderr = run_git_command(['git', 'add', '.'])
        if not success:
            return {'success': False, 'message': f'Failed to add files: {stderr}'}
    
    # 提交
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"[Publish] {message} ({timestamp})"
    success, stdout, stderr = run_git_command(['git', 'commit', '-m', commit_msg])
    if not success:
        if "nothing to commit" in stderr or "nothing to commit" in stdout:
            # 没有变更，但仍然尝试推送（可能之前有未推送的提交）
            pass
        else:
            return {'success': False, 'message': f'Failed to commit: {stderr}'}
    
    # 获取当前分支
    success, current_branch, _ = run_git_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    branch = current_branch if current_branch else 'main'
    
    # 推送到当前分支
    success, stdout, stderr = run_git_command(['git', 'push', 'origin', branch])
    if not success:
        return {'success': False, 'message': f'Failed to push: {stderr}'}
    
    return {'success': True, 'message': 'Successfully committed and pushed!'}


@app.route('/')
def index():
    """首页 - 显示文件列表（调试用）"""
    files = get_markdown_files()
    
    html = render_template_string(
        HTML_TEMPLATE,
        title="Logseq Publish - 文件列表",
        path_info=f"📂 {PAGES_DIR}",
        view='list',
        files=files,
        pages_dir=PAGES_DIR
    )
    
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


@app.route('/view/<filename>')
def view_file(filename: str):
    """查看单个 Markdown 文件（调试用）"""
    file_path = Path(PAGES_DIR) / filename
    
    if not file_path.exists():
        html = render_template_string(
            HTML_TEMPLATE,
            title="文件不存在",
            path_info=f"❌ {filename}",
            view='file',
            filename=filename,
            html_content='<h2>❌ 文件不存在</h2>'
        )
        response = make_response(html, 404)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    try:
        content = file_path.read_text(encoding='utf-8')
        html_content = render_markdown(content)
        
        html = render_template_string(
            HTML_TEMPLATE,
            title=filename.replace('.md', ''),
            path_info=f"📄 {filename}",
            view='file',
            filename=filename,
            html_content=html_content
        )
        
        response = make_response(html)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    except Exception as e:
        html = render_template_string(
            HTML_TEMPLATE,
            title="读取失败",
            path_info=f"❌ {filename}",
            view='file',
            filename=filename,
            html_content=f'<h2>❌ 读取失败</h2><p>{str(e)}</p>'
        )
        response = make_response(html, 500)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response


# ============== API Routes ==============

@app.route('/api/files', methods=['GET'])
def api_files():
    """API - 获取文件列表"""
    try:
        files = get_markdown_files()
        return jsonify({'success': True, 'data': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/file/<filename>', methods=['GET'])
def api_get_file(filename: str):
    """API - 获取文件内容"""
    file_path = Path(PAGES_DIR) / filename
    
    if not file_path.exists():
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        content = file_path.read_text(encoding='utf-8')
        return jsonify({
            'success': True,
            'data': {
                'name': filename,
                'content': content,
                'html': render_markdown(content)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/file/<filename>', methods=['PUT'])
def api_update_file(filename: str):
    """API - 更新文件内容"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'success': False, 'error': 'Missing content'}), 400
    
    file_path = Path(PAGES_DIR) / filename
    
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        file_path.write_text(data['content'], encoding='utf-8')
        
        return jsonify({
            'success': True,
            'message': f'File {filename} updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/file/<filename>', methods=['POST'])
def api_create_file(filename: str):
    """API - 创建新文件"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'success': False, 'error': 'Missing content'}), 400
    
    file_path = Path(PAGES_DIR) / filename
    
    if file_path.exists():
        return jsonify({'success': False, 'error': 'File already exists'}), 409
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data['content'], encoding='utf-8')
        
        return jsonify({
            'success': True,
            'message': f'File {filename} created successfully'
        }, 201)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/file/<filename>', methods=['DELETE'])
def api_delete_file(filename: str):
    """API - 删除文件"""
    file_path = Path(PAGES_DIR) / filename
    
    if not file_path.exists():
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        file_path.unlink()
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/git/status', methods=['GET'])
def api_git_status():
    """API - 获取 Git 状态"""
    status = get_git_status()
    return jsonify(status)


@app.route('/api/git/publish', methods=['POST'])
def api_publish():
    """API - 提交并推送到 GitHub"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Missing commit message'}), 400
    
    files = data.get('files')  # 可选，指定要提交的文件
    message = data['message']
    
    result = commit_and_push(message, files)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/api/git/diff', methods=['GET'])
def api_git_diff():
    """API - 获取 Git diff"""
    success, stdout, stderr = run_git_command(['git', 'diff'])
    
    if not success:
        return jsonify({'success': False, 'error': stderr}), 500
    
    return jsonify({
        'success': True,
        'data': stdout
    })


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Logseq Publish Web Server')
    parser.add_argument('--port', '-p', type=int, default=PORT, help=f'端口号 (默认：{PORT})')
    parser.add_argument('--host', '-H', type=str, default=HOST, help=f'监听地址 (默认：{HOST})')
    parser.add_argument('--dir', '-d', type=str, default=PAGES_DIR, help='Pages 目录')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    Path(args.dir).mkdir(parents=True, exist_ok=True)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              📚 Logseq Publish Web Server                    ║
╠══════════════════════════════════════════════════════════════╣
║  后端地址：http://localhost:{args.port}                        ║
║  外网访问：http://47.102.152.55:{args.port}                    ║
║  Pages 目录：{args.dir}                                        ║
║  仓库目录：{LOGSEQ_PUBLISH_DIR}                                ║
║                                                              ║
║  按 Ctrl+C 停止服务                                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == '__main__':
    main()

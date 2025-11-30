public:: true

- # Windows 上部署 Nginx 指南
  
  本指南介绍如何在 Windows 系统上安装和配置 Nginx，用于 SSO 演示系统的反向代理。
- ## 目录
- [下载和安装 Nginx](#下载和安装-nginx)
- [配置 Nginx](#配置-nginx)
- [启动和管理 Nginx](#启动和管理-nginx)
- [验证配置](#验证配置)
- [常见问题](#常见问题)
- [开机自启动（可选）](#开机自启动可选)
  
  ---
- ## 下载和安装 Nginx
- ### 方法 1: 官方下载（推荐）
  
  1. **访问 Nginx 官网下载页面**
   
   打开浏览器访问：http://nginx.org/en/download.html
  
  2. **下载 Windows 版本**
   
   选择 Stable version（稳定版），下载 Windows 版本的 zip 文件
   
   例如：`nginx-1.24.0.zip`（版本号可能不同）
  
  3. **解压到指定目录**
   
   推荐解压到：`C:\nginx`
   
   ```cmd
   # 使用命令行解压（如果有 7-Zip）
   "C:\Program Files\7-Zip\7z.exe" x nginx-1.24.0.zip -oC:\
   
   # 或者右键 -> 解压到当前文件夹，然后移动到 C:\nginx
   ```
- ### 方法 2: 使用 Chocolatey（如果已安装）
  
  ```powershell
  # 以管理员身份运行 PowerShell
  choco install nginx
  ```
  
  ---
- ## 配置 Nginx
- ### 1. 创建适用于 Windows 的配置文件
  
  由于 Windows 和 Linux 的路径和配置有所不同，我们需要修改配置文件。
  
  **创建 `nginx/nginx-windows.conf` 文件：**
  
  ```nginx
  # Windows 版本的 Nginx 配置
  
  # 工作进程数（建议设置为 CPU 核心数）
  worker_processes 1;
  
  # 错误日志路径（Windows 路径）
  error_log logs/error.log;
  error_log logs/error.log notice;
  error_log logs/error.log info;
  
  # PID 文件路径
  pid logs/nginx.pid;
  
  events {
    worker_connections 1024;
  }
  
  http {
    # MIME 类型
    include mime.types;
    default_type application/octet-stream;
  
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  
    access_log logs/access.log main;
  
    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
  
    server {
        listen 80;
        server_name localhost;
  
        # 字符集
        charset utf-8;
  
        # SSO服务 - 代理到端口5000
        location /sso/ {
            proxy_pass http://127.0.0.1:5000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # Cookie传递
            proxy_cookie_path / /;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
  
        # 站点A - 代理到端口5001
        location /site-a/ {
            proxy_pass http://127.0.0.1:5001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # Cookie传递
            proxy_cookie_path / /;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
  
        # 站点B - 代理到端口5002
        location /site-b/ {
            proxy_pass http://127.0.0.1:5002/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # Cookie传递
            proxy_cookie_path / /;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
  
        # 根路径重定向到站点A
        location = / {
            return 301 /site-a/;
        }
  
        # 健康检查端点
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
  }
  ```
- ### 2. 复制配置文件到 Nginx 目录
  
  ```cmd
  # 复制我们的配置文件到 Nginx 安装目录
  copy nginx\nginx-windows.conf C:\nginx\conf\nginx.conf
  
  # 或者使用项目目录中的配置（需要修改路径）
  ```
  
  ---
- ## 启动和管理 Nginx
- ### 启动 Nginx
  
  **方法 1: 使用命令行**
  
  ```cmd
  # 进入 Nginx 目录
  cd C:\nginx
  
  # 启动 Nginx
  start nginx
  
  # 或者直接运行
  nginx.exe
  ```
  
  **方法 2: 使用 PowerShell**
  
  ```powershell
  # 进入 Nginx 目录
  cd C:\nginx
  
  # 启动 Nginx（后台运行）
  Start-Process nginx.exe
  ```
- ### 检查 Nginx 是否运行
  
  ```cmd
  # 查看 Nginx 进程
  tasklist /fi "imagename eq nginx.exe"
  
  # 应该看到类似输出：
  # nginx.exe                    12345 Console                    1     10,234 K
  # nginx.exe                    12346 Console                    1      9,876 K
  ```
- ### 停止 Nginx
  
  ```cmd
  # 进入 Nginx 目录
  cd C:\nginx
  
  # 快速停止（立即停止）
  nginx.exe -s stop
  
  # 优雅停止（等待请求处理完成）
  nginx.exe -s quit
  ```
- ### 重新加载配置（不停止服务）
  
  ```cmd
  cd C:\nginx
  nginx.exe -s reload
  ```
- ### 测试配置文件
  
  ```cmd
  cd C:\nginx
  
  # 测试配置文件语法
  nginx.exe -t
  
  # 应该看到：
  # nginx: the configuration file C:\nginx/conf/nginx.conf syntax is ok
  # nginx: configuration file C:\nginx/conf/nginx.conf test is successful
  ```
  
  ---
- ## 验证配置
- ### 1. 启动所有服务
  
  ```cmd
  # 1. 启动 PostgreSQL（如果还没启动）
  # 参考 POSTGRESQL_SETUP.md
  
  # 2. 启动 SSO 系统的所有服务
  start_services.bat
  
  # 3. 启动 Nginx
  cd C:\nginx
  start nginx
  ```
- ### 2. 测试访问
  
  打开浏览器，访问以下地址：
- **健康检查**: http://localhost/health
	- 应该显示：`healthy`
- **SSO 登录页**: http://localhost/sso/login
	- 应该显示登录页面
- **站点 A**: http://localhost/site-a/
	- 应该重定向到 SSO 登录页
- **站点 B**: http://localhost/site-b/
	- 应该重定向到 SSO 登录页
- ### 3. 检查日志
  
  ```cmd
  # 查看访问日志
  type C:\nginx\logs\access.log
  
  # 查看错误日志
  type C:\nginx\logs\error.log
  ```
  
  ---
- ## 常见问题
- ### 问题 1: 端口 80 被占用
  
  **错误信息**：
  ```
  bind() to 0.0.0.0:80 failed (10013: An attempt was made to access a socket in a way forbidden by its access permissions)
  ```
  
  **解决方法**：
  
  1. **检查哪个程序占用了端口 80**
  
  ```cmd
  netstat -ano | findstr :80
  ```
  
  2. **停止占用端口的程序**
  
  常见占用端口 80 的程序：
- IIS (Internet Information Services)
- Skype
- VMware
- 其他 Web 服务器
  
  停止 IIS：
  ```cmd
  # 以管理员身份运行
  net stop was /y
  ```
  
  3. **或者修改 Nginx 监听端口**
  
  编辑 `C:\nginx\conf\nginx.conf`，将 `listen 80;` 改为其他端口：
  
  ```nginx
  server {
    listen 8080;  # 改为 8080 或其他未占用的端口
    server_name localhost;
    # ...
  }
  ```
  
  然后访问 http://localhost:8080/
- ### 问题 2: 无法访问后端服务
  
  **症状**：访问 http://localhost/sso/ 显示 502 Bad Gateway
  
  **解决方法**：
  
  1. **确认后端服务正在运行**
  
  ```cmd
  netstat -ano | findstr :5000
  netstat -ano | findstr :5001
  netstat -ano | findstr :5002
  ```
  
  2. **检查防火墙设置**
  
  确保 Windows 防火墙允许本地连接
  
  3. **查看 Nginx 错误日志**
  
  ```cmd
  type C:\nginx\logs\error.log
  ```
- ### 问题 3: 配置文件路径问题
  
  **症状**：Nginx 启动失败，提示找不到配置文件
  
  **解决方法**：
  
  确保配置文件在正确的位置：`C:\nginx\conf\nginx.conf`
  
  或者使用 `-c` 参数指定配置文件：
  
  ```cmd
  nginx.exe -c "C:\path\to\your\nginx.conf"
  ```
- ### 问题 4: 权限问题
  
  **症状**：无法启动 Nginx 或无法写入日志
  
  **解决方法**：
  
  以管理员身份运行命令提示符或 PowerShell
- ### 问题 5: 中文路径或文件名问题
  
  **症状**：配置文件中的中文注释导致错误
  
  **解决方法**：
  
  确保配置文件使用 UTF-8 编码保存（不带 BOM）
  
  ---
- ## 开机自启动（可选）
- ### 方法 1: 使用 Windows 任务计划程序
  
  1. **打开任务计划程序**
	- 按 `Win + R`，输入 `taskschd.msc`，回车
	  
	  2. **创建基本任务**
	- 点击右侧"创建基本任务"
	- 名称：`Nginx 自动启动`
	- 触发器：`当计算机启动时`
	- 操作：`启动程序`
	- 程序：`C:\nginx\nginx.exe`
	- 起始于：`C:\nginx`
	  
	  3. **设置高级选项**
	- 右键任务 -> 属性
	- 勾选"使用最高权限运行"
	- 勾选"不管用户是否登录都要运行"
- ### 方法 2: 使用 NSSM（推荐）
  
  NSSM (Non-Sucking Service Manager) 可以将 Nginx 注册为 Windows 服务。
  
  1. **下载 NSSM**
   
   访问：https://nssm.cc/download
   
   下载并解压到 `C:\nssm`
  
  2. **安装 Nginx 服务**
  
  ```cmd
  # 以管理员身份运行
  cd C:\nssm\win64
  
  # 安装服务
  nssm install nginx C:\nginx\nginx.exe
  
  # 设置服务参数
  nssm set nginx AppDirectory C:\nginx
  nssm set nginx DisplayName "Nginx Web Server"
  nssm set nginx Description "Nginx reverse proxy for SSO demo"
  nssm set nginx Start SERVICE_AUTO_START
  
  # 启动服务
  nssm start nginx
  ```
  
  3. **管理服务**
  
  ```cmd
  # 查看服务状态
  nssm status nginx
  
  # 停止服务
  nssm stop nginx
  
  # 重启服务
  nssm restart nginx
  
  # 卸载服务
  nssm remove nginx confirm
  ```
- ### 方法 3: 使用启动文件夹
  
  1. **创建启动脚本 `start_nginx.bat`**
  
  ```batch
  @echo off
  cd C:\nginx
  start nginx.exe
  ```
  
  2. **将脚本快捷方式放到启动文件夹**
  
  按 `Win + R`，输入 `shell:startup`，将脚本快捷方式复制到打开的文件夹
  
  ---
- ## 创建便捷管理脚本
  
  为了方便管理，可以创建以下批处理脚本：
- ### `nginx_start.bat`
  
  ```batch
  @echo off
  echo 正在启动 Nginx...
  cd C:\nginx
  start nginx.exe
  timeout /t 2 /nobreak >nul
  tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" >nul
  if %errorlevel% == 0 (
    echo Nginx 启动成功！
  ) else (
    echo Nginx 启动失败，请检查日志
  )
  pause
  ```
- ### `nginx_stop.bat`
  
  ```batch
  @echo off
  echo 正在停止 Nginx...
  cd C:\nginx
  nginx.exe -s quit
  timeout /t 2 /nobreak >nul
  echo Nginx 已停止
  pause
  ```
- ### `nginx_reload.bat`
  
  ```batch
  @echo off
  echo 正在重新加载 Nginx 配置...
  cd C:\nginx
  nginx.exe -t
  if %errorlevel% == 0 (
    nginx.exe -s reload
    echo 配置重新加载成功！
  ) else (
    echo 配置文件有错误，请检查
  )
  pause
  ```
- ### `nginx_status.bat`
  
  ```batch
  @echo off
  echo 检查 Nginx 运行状态...
  tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" >nul
  if %errorlevel% == 0 (
    echo Nginx 正在运行
    tasklist /fi "imagename eq nginx.exe"
  ) else (
    echo Nginx 未运行
  )
  echo.
  echo 端口占用情况:
  netstat -ano | findstr :80
  pause
  ```
  
  ---
- ## 完整启动流程
  
  创建一个完整的启动脚本 `start_all_services.bat`：
  
  ```batch
  @echo off
  chcp 65001 >nul
  set PYTHONIOENCODING=utf-8
  set PGCLIENTENCODING=UTF8
  
  echo ========================================
  echo SSO 系统完整启动脚本
  echo ========================================
  echo.
  
  REM 1. 检查 PostgreSQL
  echo [1/4] 检查 PostgreSQL 数据库...
  pg_isready -h localhost -p 5432 >nul 2>&1
  if errorlevel 1 (
    echo [警告] PostgreSQL 未运行，请先启动数据库
    pause
    exit /b 1
  )
  echo PostgreSQL 运行正常
  
  REM 2. 启动 Flask 应用
  echo.
  echo [2/4] 启动 Flask 应用...
  start "SSO服务" cmd /k "cd sso_service && python app.py"
  timeout /t 2 /nobreak >nul
  start "站点A" cmd /k "cd site_a && python app.py"
  timeout /t 2 /nobreak >nul
  start "站点B" cmd /k "cd site_b && python app.py"
  timeout /t 2 /nobreak >nul
  
  REM 3. 启动 Nginx
  echo.
  echo [3/4] 启动 Nginx...
  cd C:\nginx
  start nginx.exe
  timeout /t 2 /nobreak >nul
  
  REM 4. 验证服务
  echo.
  echo [4/4] 验证服务状态...
  netstat -ano | findstr :5000 >nul && echo   ✓ SSO服务 (5000) 运行中
  netstat -ano | findstr :5001 >nul && echo   ✓ 站点A (5001) 运行中
  netstat -ano | findstr :5002 >nul && echo   ✓ 站点B (5002) 运行中
  tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" >nul && echo   ✓ Nginx (80) 运行中
  
  echo.
  echo ========================================
  echo 所有服务已启动！
  echo ========================================
  echo.
  echo 访问地址:
  echo   - 通过 Nginx: http://localhost/site-a/
  echo   - 健康检查: http://localhost/health
  echo.
  pause
  ```
  
  ---
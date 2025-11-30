public:: true

- # PostgreSQL安装和配置指南
  
  本指南详细说明如何在不同操作系统上安装和配置PostgreSQL。
- ## 📋 目录
- [Windows安装](#windows安装)
- [Linux安装](#linux安装)
- [Mac安装](#mac安装)
- [数据库配置](#数据库配置)
- [常见问题](#常见问题)
- ## Windows安装
- ### 方法1：使用官方安装程序（推荐）
- #### 1. 下载安装程序
  
  访问 https://www.postgresql.org/download/windows/
  
  选择"Download the installer"，下载PostgreSQL 14或更高版本。
- #### 2. 运行安装程序
  
  1. 双击下载的安装程序
  2. 点击"Next"开始安装
  3. 选择安装目录（默认：`C:\Program Files\PostgreSQL\14`）
  4. 选择要安装的组件：
	- ✅ PostgreSQL Server
	- ✅ pgAdmin 4（图形化管理工具）
	- ✅ Stack Builder（可选）
	- ✅ Command Line Tools
	  5. 选择数据目录（默认：`C:\Program Files\PostgreSQL\14\data`）
	  6. **设置postgres用户密码**（重要！请记住这个密码）
	- 建议使用强密码，例如：`Postgres@2024`
	  7. 选择端口（默认：5432）
	  8. 选择区域设置（默认：Default locale）
	  9. 点击"Next"开始安装
	  10. 等待安装完成
- #### 3. 验证安装
  
  打开命令提示符（CMD）：
  
  ```cmd
  # 检查PostgreSQL版本
  psql --version
  
  # 检查服务状态
  sc query postgresql-x64-14
  ```
  
  如果看到版本信息和服务状态为"RUNNING"，说明安装成功。
- ### 方法2：使用Chocolatey
  
  如果你安装了Chocolatey包管理器：
  
  ```cmd
  choco install postgresql
  ```
- ## Linux安装
- ### Ubuntu/Debian
  
  ```bash
  # 更新包列表
  sudo apt update
  
  # 安装PostgreSQL
  sudo apt install postgresql postgresql-contrib
  
  # 启动服务
  sudo systemctl start postgresql
  
  # 设置开机自启
  sudo systemctl enable postgresql
  
  # 检查状态
  sudo systemctl status postgresql
  ```
- ### CentOS/RHEL
  
  ```bash
  # 安装PostgreSQL
  sudo yum install postgresql-server postgresql-contrib
  
  # 初始化数据库
  sudo postgresql-setup initdb
  
  # 启动服务
  sudo systemctl start postgresql
  
  # 设置开机自启
  sudo systemctl enable postgresql
  
  # 检查状态
  sudo systemctl status postgresql
  ```
- ### Fedora
  
  ```bash
  # 安装PostgreSQL
  sudo dnf install postgresql-server postgresql-contrib
  
  # 初始化数据库
  sudo postgresql-setup --initdb
  
  # 启动服务
  sudo systemctl start postgresql
  
  # 设置开机自启
  sudo systemctl enable postgresql
  ```
- ## Mac安装
- ### 方法1：使用Homebrew（推荐）
  
  ```bash
  # 安装Homebrew（如果还没有）
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  
  # 安装PostgreSQL
  brew install postgresql
  
  # 启动服务
  brew services start postgresql
  
  # 检查状态
  brew services list | grep postgresql
  ```
- ### 方法2：使用Postgres.app
  
  1. 访问 https://postgresapp.com/
  2. 下载并安装Postgres.app
  3. 打开应用，点击"Initialize"初始化数据库
  4. 添加到PATH（可选）：
   ```bash
   echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
- ## 数据库配置
- ### 1. 连接到PostgreSQL
- #### Windows
  
  打开"SQL Shell (psql)"（从开始菜单）：
  
  ```
  Server [localhost]:        # 按Enter使用默认值
  Database [postgres]:       # 按Enter使用默认值
  Port [5432]:              # 按Enter使用默认值
  Username [postgres]:      # 按Enter使用默认值
  Password:                 # 输入安装时设置的密码
  ```
  
  或使用命令行：
  
  ```cmd
  psql -U postgres
  ```
- #### Linux
  
  ```bash
  # 切换到postgres用户
  sudo -u postgres psql
  
  # 或直接连接
  sudo -u postgres psql -d postgres
  ```
- #### Mac
  
  ```bash
  psql postgres
  ```
- ### 2. 创建SSO数据库和用户
  
  在psql命令行中执行：
  
  ```sql
  -- 创建数据库用户
  CREATE USER sso_user WITH PASSWORD 'your_secure_password';
  
  -- 创建数据库
  CREATE DATABASE sso_demo OWNER sso_user;
  
  -- 授予权限
  GRANT ALL PRIVILEGES ON DATABASE sso_demo TO sso_user;
  
  -- 验证创建
  \l                        -- 列出所有数据库
  \du                       -- 列出所有用户
  
  -- 退出psql
  \q
  ```
- ### 3. 配置远程访问（可选）
  
  如果需要从其他机器访问PostgreSQL：
- #### 编辑 postgresql.conf
  
  **Windows**: `C:\Program Files\PostgreSQL\14\data\postgresql.conf`  
  **Linux**: `/etc/postgresql/14/main/postgresql.conf`  
  **Mac**: `/usr/local/var/postgres/postgresql.conf`
  
  找到并修改：
  
  ```conf
  listen_addresses = '*'    # 监听所有IP地址
  ```
- #### 编辑 pg_hba.conf
  
  **Windows**: `C:\Program Files\PostgreSQL\14\data\pg_hba.conf`  
  **Linux**: `/etc/postgresql/14/main/pg_hba.conf`  
  **Mac**: `/usr/local/var/postgres/pg_hba.conf`
  
  添加以下行（允许密码认证）：
  
  ```conf
  # TYPE  DATABASE        USER            ADDRESS                 METHOD
  host    all             all             0.0.0.0/0               md5
  ```
- #### 重启PostgreSQL
  
  **Windows**:
  ```cmd
  net stop postgresql-x64-14
  net start postgresql-x64-14
  ```
  
  **Linux**:
  ```bash
  sudo systemctl restart postgresql
  ```
  
  **Mac**:
  ```bash
  brew services restart postgresql
  ```
- ### 4. 初始化SSO数据库表
  
  ```bash
  # 设置密码环境变量（避免每次输入）
  # Windows
  set PGPASSWORD=your_secure_password
  
  # Linux/Mac
  export PGPASSWORD=your_secure_password
  
  # 初始化表结构
  # Windows
  psql -h localhost -U sso_user -d sso_demo -f database\init.sql
  
  # Linux/Mac
  psql -h localhost -U sso_user -d sso_demo -f database/init.sql
  ```
  
  如果看到以下输出，说明初始化成功：
  
  ```
  CREATE TABLE
  CREATE INDEX
  CREATE INDEX
  ALTER TABLE
  ```
- ### 5. 验证数据库
  
  ```bash
  # 连接到数据库
  psql -h localhost -U sso_user -d sso_demo
  
  # 在psql中执行
  \dt                       -- 列出所有表
  \d users                  -- 查看users表结构
  \d sessions               -- 查看sessions表结构
  
  SELECT * FROM users;      -- 查询用户（应该为空）
  SELECT * FROM sessions;   -- 查询会话（应该为空）
  
  \q                        -- 退出
  ```
- ## 常见问题
- ### 问题1：psql命令不识别
  
  **Windows解决方案**:
  
  1. 添加PostgreSQL到系统PATH：
	- 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
	- 在系统变量中找到Path，点击编辑
	- 添加：`C:\Program Files\PostgreSQL\14\bin`
	- 点击确定，重新打开命令提示符
	  
	  2. 或使用完整路径：
	  ```cmd
	  "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres
	  ```
	  
	  **Linux/Mac解决方案**:
	  
	  ```bash
	  # 查找psql位置
	  which psql
	  
	  # 如果找不到，添加到PATH
	  echo 'export PATH="/usr/lib/postgresql/14/bin:$PATH"' >> ~/.bashrc
	  source ~/.bashrc
	  ```
- ### 问题2：密码认证失败
  
  **错误**: `FATAL: password authentication failed for user "postgres"`
  
  **解决方案**:
  
  1. 重置postgres用户密码：
  
  **Windows**:
  ```cmd
  # 以postgres用户身份运行psql
  psql -U postgres
  
  # 在psql中执行
  ALTER USER postgres WITH PASSWORD 'new_password';
  \q
  ```
  
  **Linux**:
  ```bash
  sudo -u postgres psql
  ALTER USER postgres WITH PASSWORD 'new_password';
  \q
  ```
  
  2. 检查pg_hba.conf配置是否正确
- ### 问题3：无法连接到服务器
  
  **错误**: `could not connect to server: Connection refused`
  
  **解决方案**:
  
  1. 检查PostgreSQL服务是否运行：
  
  **Windows**:
  ```cmd
  sc query postgresql-x64-14
  # 如果未运行
  net start postgresql-x64-14
  ```
  
  **Linux**:
  ```bash
  sudo systemctl status postgresql
  # 如果未运行
  sudo systemctl start postgresql
  ```
  
  **Mac**:
  ```bash
  brew services list | grep postgresql
  # 如果未运行
  brew services start postgresql
  ```
  
  2. 检查防火墙是否阻止了5432端口
  
  3. 检查postgresql.conf中的listen_addresses配置
- ### 问题4：权限不足
  
  **错误**: `ERROR: permission denied for database sso_demo`
  
  **解决方案**:
  
  ```sql
  -- 以postgres用户连接
  psql -U postgres
  
  -- 授予所有权限
  GRANT ALL PRIVILEGES ON DATABASE sso_demo TO sso_user;
  
  -- 如果还有问题，授予超级用户权限
  ALTER USER sso_user WITH SUPERUSER;
  
  \q
  ```
- ### 问题5：端口被占用
  
  **错误**: `could not bind IPv4 address "0.0.0.0": Address already in use`
  
  **解决方案**:
  
  1. 查找占用5432端口的进程：
  
  **Windows**:
  ```cmd
  netstat -ano | findstr :5432
  taskkill /PID <进程ID> /F
  ```
  
  **Linux/Mac**:
  ```bash
  lsof -i :5432
  kill -9 <进程ID>
  ```
  
  2. 或修改PostgreSQL端口：
  
  编辑postgresql.conf，修改：
  ```conf
  port = 5433    # 改为其他端口
  ```
  
  然后在.env文件中也修改：
  ```
  DB_PORT=5433
  ```
- ### 问题6：数据库不存在
  
  **错误**: `FATAL: database "sso_demo" does not exist`
  
  **解决方案**:
  
  ```bash
  # 创建数据库
  psql -U postgres
  CREATE DATABASE sso_demo OWNER sso_user;
  \q
  ```
- ## 图形化管理工具
- ### pgAdmin 4（推荐）
  
  PostgreSQL官方图形化管理工具，安装PostgreSQL时会自动安装。
  
  **启动pgAdmin**:
- Windows: 开始菜单 → pgAdmin 4
- Linux: `pgadmin4`
- Mac: 应用程序 → pgAdmin 4
  
  **连接数据库**:
  1. 右键"Servers" → Create → Server
  2. 填写连接信息：
	- Name: SSO Demo
	- Host: localhost
	- Port: 5432
	- Username: sso_user
	- Password: your_secure_password
- ### DBeaver
  
  通用数据库管理工具，支持多种数据库。
  
  下载: https://dbeaver.io/download/
- ### DataGrip
  
  JetBrains出品的专业数据库IDE。
  
  下载: https://www.jetbrains.com/datagrip/
- ## 性能优化（可选）
- ### 调整内存设置
  
  编辑postgresql.conf：
  
  ```conf
  # 根据系统内存调整
  shared_buffers = 256MB          # 系统内存的25%
  effective_cache_size = 1GB      # 系统内存的50-75%
  maintenance_work_mem = 64MB
  work_mem = 4MB
  ```
- ### 启用查询日志
  
  ```conf
  logging_collector = on
  log_directory = 'pg_log'
  log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
  log_statement = 'all'           # 记录所有SQL语句
  ```
- ## 备份和恢复
- ### 备份数据库
  
  ```bash
  # 备份整个数据库
  pg_dump -h localhost -U sso_user -d sso_demo -F c -f sso_demo_backup.dump
  
  # 备份为SQL文件
  pg_dump -h localhost -U sso_user -d sso_demo -f sso_demo_backup.sql
  ```
- ### 恢复数据库
  
  ```bash
  # 从dump文件恢复
  pg_restore -h localhost -U sso_user -d sso_demo sso_demo_backup.dump
  
  # 从SQL文件恢复
  psql -h localhost -U sso_user -d sso_demo -f sso_demo_backup.sql
  ```
- ## 卸载PostgreSQL
- ### Windows
  
  1. 控制面板 → 程序和功能
  2. 找到PostgreSQL，点击卸载
  3. 删除数据目录（如果需要）：`C:\Program Files\PostgreSQL\14\data`
- ### Linux
  
  ```bash
  # Ubuntu/Debian
  sudo apt remove postgresql postgresql-contrib
  sudo apt purge postgresql postgresql-contrib
  sudo rm -rf /var/lib/postgresql/
  
  # CentOS/RHEL
  sudo yum remove postgresql-server postgresql-contrib
  sudo rm -rf /var/lib/pgsql/
  ```
- ### Mac
  
  ```bash
  # 使用Homebrew
  brew uninstall postgresql
  brew cleanup
  rm -rf /usr/local/var/postgres
  ```
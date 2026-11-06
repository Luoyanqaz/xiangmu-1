# xiangmu2 本地开发

本目录是独立的 xiangmu2 开发实例。原项目 `E:\Code\xiangmu-main` 的代码和配置保持原样。
用编辑器打开 `xiangmu2.code-workspace`，工作区显示为 xiangmu2；浏览器标签页也带有 xiangmu2。

## 已配置的隔离项

| 资源 | xiangmu2 |
| --- | --- |
| 前端 | http://127.0.0.1:5174/login |
| Django | http://127.0.0.1:8001 |
| MySQL 数据库 | xiangmu2 |
| MySQL 用户 | xiangmu2_local，仅授权 xiangmu2 和 xiangmu2_test |
| Redis | WSL Ubuntu-24.04 内独立进程，127.0.0.1:6380，独立密码 |
| Redis 数据库 | 缓存 0、Celery broker 1、任务结果 2 |
| Celery | 队列/交换机 xiangmu2，worker 名 xiangmu2@机器名 |
| Python | 当前后端目录 `.venv`，Python 3.11 |
| 上传及报告文件 | 当前后端 `media`，本地文件系统 |
| Redis 持久化及服务日志 | 当前项目 `.local` |
| 邮件 | 仅输出到控制台 |
| 大模型 | 默认关闭网络调用，不使用其他项目的 API 密钥 |

MySQL 服务本身共用现有 MySQL80，但数据及账号权限分开。停止 MySQL80 或整个 WSL 仍会影响依赖这些公共服务的项目。
业务操作从前端登录地址进入。后端根地址自动跳转到 Django 管理入口 `http://127.0.0.1:8001/django-admin/`（需要 Django 管理权限）；API 文档位于 `http://127.0.0.1:8001/swagger/`。后端 `/admin/` 不是有效页面。
启动/停止脚本只管理本项目记录的进程，不停止 MySQL80、Redis 6379 或整个 WSL。

## 启动、停止与检查

在本项目根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\local.ps1 start
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\local.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\local.ps1 check
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\local.ps1 stop
```

`start` 会依次启动专用 Redis、Django、Celery 和 Vite，后台运行，不弹出额外窗口。
前端支持局域网访问（监听 `0.0.0.0:5174`），后端及 Redis 仍只监听本机。首次共享前，在管理员 PowerShell 中执行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\lan-firewall.ps1 enable`，仅向本地子网放行前端端口；完整操作见 [本地运行指南.md](本地运行指南.md) 第 7 节。
`check` 检查数据库权限、缓存、后台任务、验证码、管理员登录、API 及文件代理；会产生一条正常的本地登录日志。
修改后端代码后，用 `stop`、`start` 重启；此启动入口使用 `--noreload`，便于准确管理进程。
前端代码修改仍支持 Vite 热更新。端口占用时脚本会报错，不接管不属于本项目的服务。

初始管理员账号及随机密码见 `.local/login.txt`。本项目使用全新数据库，已初始化问卷和系统配置，没有导入原项目的学校、用户或评估记录。
如果修改了管理员密码，同步更新 `.local/credentials.json` 才能继续使用自动登录检查。

## F5 调试

先运行 `local.ps1 stop`，避免与后台运行模式争用端口，再打开 `xiangmu2.code-workspace`。
选择 `xiangmu2: full stack` 并按 F5；也可以单独选择 Django、Celery 或前端。
Django 调试入口会自动启动专用 Redis；单独调试 Celery 时先执行 `local.ps1 redis`。
使用编辑器的停止按钮结束调试进程，再执行 `local.ps1 stop` 关闭专用 Redis。
不要同时使用后台启动模式和 F5 启动同一服务。

## 环境与依赖

后端配置只加载当前后端 `.env`，优先于继承的环境变量，避免从另一个终端带入旧项目连接。
原后端 `.env` 已备份到 `.local/original-backend.env`，仅用于回看，不应重新加载运行。

```powershell
py -3.11 -m venv .\mature-evaluation-system-backend\.venv
.\mature-evaluation-system-backend\.venv\Scripts\python.exe -m pip install -r .\mature-evaluation-system-backend\requirements-local.txt
cd .\mature-evaluation-system-frontend
npm.cmd ci
```

Kombu 固定为 5.3.7，以兼容本项目 Celery 5.3.4 和 redis-py 5.0.1。兼容范围参考 [Kombu 官方变更记录](https://docs.celeryq.dev/projects/kombu/en/v5.3.7/changelog.html)。

`.env.example` 只提供配置模板。`.env`、`.venv`、`.local`、日志和依赖目录已排除出版本控制。
`scripts/bootstrap.py` 仅供创建新的空 xiangmu2 数据库，已存在时拒绝重建，日常启动不要重复执行。

## 将文件夹也改名为 xiangmu2

当前文件夹被编辑器占用，配置过程未强制关闭编辑器，所以实际目录暂为 `E:\Code\xinmin\xiangmu`。
工作区和服务标识已经全部使用 xiangmu2，不影响同时运行。

关闭本项目的编辑器、调试进程和所有位于此目录的终端后，在父目录的独立 PowerShell 中执行：

```powershell
cd E:\Code\xinmin
powershell -NoProfile -ExecutionPolicy Bypass -File .\rename-xiangmu2.ps1
```

脚本会停止本项目后台服务，将目录改为 `E:\Code\xinmin\xiangmu2`，并重建其中的 Python 虚拟环境，修复虚拟环境内的绝对路径。
不会覆盖已存在的目标文件夹，也不会修改原项目。随后打开新目录内的 `xiangmu2.code-workspace` 并重新启动。

## 启用真实外部服务

需要 AI 时，在本项目 `.env` 配置自己的密钥并设置 `LLM_ALLOW_NETWORK=True`，同时检查本项目数据库的系统配置，因为模型服务优先读取数据库配置。
OSS 默认关闭；如需启用，应使用本项目独立桶并设置 `USE_OSS=True`。邮件默认输出到本项目后台日志。

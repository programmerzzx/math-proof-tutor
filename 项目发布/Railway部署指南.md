# 数学证明导师会员付费系统 - Railway 部署指南

> 本指南将帮助您将数学证明导师会员付费系统部署到 Railway 平台。

## 目录

- [快速开始](#快速开始)
- [准备工作](#准备工作)
- [部署步骤](#部署步骤)
- [配置环境变量](#配置环境变量)
- [数据库设置](#数据库设置)
- [一键部署](#一键部署)
- [验证部署](#验证部署)
- [自定义域名](#自定义域名)
- [常见问题](#常见问题)

---

## 快速开始

### 一键部署（推荐）

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/math-tutor-membership)

> ⚠️ **注意**: 请将 `YOUR_USERNAME` 替换为您的 GitHub 用户名，并将仓库地址替换为实际地址。

### 部署要求

- Python 3.11
- PostgreSQL 数据库（Railway 提供）
- GitHub 账户

---

## 准备工作

### 1. 准备代码仓库

确保您的项目代码已推送到 GitHub 仓库：

```bash
cd 会员付费系统
git init
git add .
git commit -m "Initial commit for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/math-tutor-membership.git
git push -u origin main
```

### 2. 创建 Railway 账户

1. 访问 [Railway 官网](https://railway.app)
2. 点击 **Sign Up** 注册账户
3. 推荐使用 **GitHub 登录**（更方便）
4. 完成邮箱验证

---

## 部署步骤

### 方法一：通过 Railway 控制台部署

#### 第一步：创建新项目

1. 登录 [Railway 控制台](https://railway.app/dashboard)
2. 点击 **New Project** 按钮
3. 选择 **Deploy from GitHub repo**

#### 第二步：连接 GitHub 仓库

1. 在弹出窗口中授权 Railway 访问您的 GitHub
2. 选择包含会员系统的仓库
3. Railway 会自动检测为 **Python** 项目

#### 第三步：配置环境变量

1. 在项目页面点击 **Variables** 标签
2. 添加以下必需的环境变量：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 会话密钥 | `your-secure-random-key-here` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxxxxxxxxxxxxxx` |
| `CORS_ORIGINS` | CORS 允许的域名 | `*` 或具体域名 |

#### 第四步：添加 PostgreSQL 数据库

1. 点击 **Add a Database**
2. 选择 **PostgreSQL**
3. Railway 会自动创建数据库并设置 `DATABASE_URL` 环境变量

#### 第五步：部署

1. Railway 会自动检测并安装依赖
2. 点击 **Deploy** 开始部署
3. 等待构建完成（约 2-5 分钟）

### 方法二：通过 Railway CLI 部署

#### 1. 安装 Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. 登录 Railway

```bash
railway login
```

#### 3. 初始化项目

```bash
cd 会员付费系统
railway init
```

#### 4. 添加数据库

```bash
railway add postgresql
```

#### 5. 设置环境变量

```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set DEEPSEEK_API_KEY=your-api-key
```

#### 6. 部署

```bash
railway up
```

#### 7. 查看部署状态

```bash
railway status
```

---

## 配置环境变量

### 必需的环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `SECRET_KEY` | ✅ | Flask 会话加密密钥（使用随机字符串） |
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API 密钥 |
| `DATABASE_URL` | 自动 | Railway PostgreSQL 自动提供 |
| `PORT` | 自动 | Railway 自动分配 |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CORS_ORIGINS` | 跨域白名单 | `*` |
| `FLASK_ENV` | 运行环境 | `production` |
| `ALIPAY_APP_ID` | 支付宝应用ID | - |
| `WECHAT_MCH_ID` | 微信商户号 | - |

### 生成安全的 SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

---

## 数据库设置

### Railway PostgreSQL

Railway 会自动：
1. 创建 PostgreSQL 数据库
2. 设置 `DATABASE_URL` 环境变量
3. 配置数据库连接池

### 手动初始化数据库表

如果需要手动初始化数据库：

```bash
# 连接到 Railway 数据库
railway connect postgresql

# 或者使用 psql
psql $DATABASE_URL -f database/membership_schema.sql
```

### 本地开发数据库

本地开发时，可以使用 SQLite：

```python
# .env 文件
DATABASE_URL=sqlite:///membership.db
```

---

## 一键部署

### 获取部署按钮代码

将以下代码添加到您的 README.md：

```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/math-tutor-membership)
```

### 替换仓库地址

将 `YOUR_USERNAME/math-tutor-membership` 替换为您的实际仓库地址。

### 部署链接格式

```
https://railway.app/new/template?template=<GITHUB_REPO_URL>
```

示例：
```
https://railway.app/new/template?template=https://github.com/username/math-tutor-membership
```

---

## 验证部署

### 检查健康状态

部署完成后，访问以下端点验证：

```
https://your-app.railway.app/health
```

预期响应：
```json
{
  "status": "healthy",
  "service": "math-tutor-membership",
  "version": "1.0.0"
}
```

### 获取部署 URL

1. 在 Railway 控制台的项目页面
2. 点击 **Settings** 标签
3. 找到 **Networking** 部分
4. 复制 **Public Domain** URL

格式：`https://your-app-name.up.railway.app`

---

## 自定义域名

### 添加自定义域名

1. 在 Railway 控制台打开项目
2. 进入 **Settings** → **Networking**
3. 点击 **Generate Domain** 或 **Add Custom Domain**
4. 按照提示配置 DNS

### DNS 配置

添加以下 DNS 记录：

| 类型 | 名称 | 值 |
|------|------|-----|
| CNAME | www | your-app.railway.app |
| CNAME | @ | your-app.railway.app |

---

## 常见问题

### 1. 部署失败

**问题**: 构建失败或报错

**解决方案**:
- 检查 `requirements.txt` 是否包含所有依赖
- 确保 Python 版本与 `runtime.txt` 一致
- 查看构建日志定位具体错误

### 2. 数据库连接错误

**问题**: `psycopg2.OperationalError`

**解决方案**:
- 确认已添加 PostgreSQL 数据库
- 检查 `DATABASE_URL` 是否正确设置
- 重启应用使环境变量生效

### 3. 端口错误

**问题**: 应用无法启动

**解决方案**:
- Railway 使用 `$PORT` 环境变量
- 确保 `app.py` 使用 `os.environ.get('PORT', 5000)`
- Gunicorn 配置 `--bind 0.0.0.0:$PORT`

### 4. CORS 跨域问题

**问题**: 前端无法调用 API

**解决方案**:
- 设置 `CORS_ORIGINS=*`（开发环境）
- 生产环境设置具体域名：`CORS_ORIGINS=https://yourdomain.com`

### 5. 静态文件加载失败

**问题**: CSS/JS/图片无法加载

**解决方案**:
- 确保 `static/` 目录存在
- 检查 Flask 应用的静态文件路径配置

### 6. 内存不足

**问题**: 应用被 OOM Kill

**解决方案**:
- 降低 Gunicorn workers 数量（当前为 2）
- 修改为 `workers = 1`

### 7. 环境变量未生效

**问题**: 修改环境变量后无效

**解决方案**:
- 重启应用：Railway 控制台 → **Deployments** → **Redeploy**
- 或使用 `railway up --prod`

---

## 维护与监控

### 查看日志

```bash
railway logs
```

### 实时日志

```bash
railway logs -f
```

### 重新部署

```bash
railway up --prod
```

### 降级回滚

在 Railway 控制台的 **Deployments** 页面，选择之前的版本点击 **Redeploy**。

---

## 项目文件结构

部署时确保包含以下文件：

```
会员付费系统/
├── app.py                 # Flask 应用入口
├── requirements.txt       # Python 依赖
├── Procfile              # Railway 启动命令
├── runtime.txt           # Python 版本
├── .env.example          # 环境变量模板
├── railway.json          # Railway 配置
├── railway.toml          # Railway 配置（备选）
├── static/               # 静态文件
├── templates/            # HTML 模板
├── backend/              # 后端逻辑
│   ├── routes/          # 路由
│   ├── membership/       # 会员模块
│   └── models/           # 数据模型
└── database/             # 数据库相关
    ├── membership_schema.sql
    └── init_db.py        # 数据库初始化
```

---

## 联系支持

如有问题：

- 📧 查看 [Railway 文档](https://docs.railway.app)
- 💬 加入 [Railway Discord](https://discord.gg/railway)
- 🐛 提交 [GitHub Issue](https://github.com/YOUR_USERNAME/math-tutor-membership/issues)

---

*文档版本: 1.0.0 | 更新日期: 2025*

# Simple Blog

一个简洁优雅的博客系统，支持文章发布和付费阅读功能。

## 功能特点

- 用户系统（注册、登录、个人中心）
- 文章管理（发布、编辑、删除）
- 付费阅读功能
- 响应式设计，支持移动端访问

## 安装说明

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置环境变量：
   创建 `.env` 文件并配置以下内容：
   ```
   SECRET_KEY=your_secret_key
   ALIPAY_APP_ID=your_alipay_app_id
   ALIPAY_PRIVATE_KEY=your_private_key
   ALIPAY_PUBLIC_KEY=your_public_key
   ```
4. 初始化数据库：
   ```bash
   flask db upgrade
   ```
5. 运行项目：
   ```bash
   flask run
   ```

## 技术栈

- 后端：Python + Flask + SQLAlchemy
- 前端：HTML + CSS + JavaScript
- 数据库：SQLite
- 支付集成：支付宝

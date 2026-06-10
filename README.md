# 校园二手物品交易平台

一个适合课堂展示的中型 Web 项目，覆盖：

- 前端页面与交互
- 后端接口设计
- SQLite 数据库建模
- 三类用户与登录鉴权
- 商品发布、收藏、留言
- 轻量 AI 功能：自动生成商品描述

## 快速启动

先进入后端目录并安装依赖：

```bash
cd campus-market/backend
python3 -m pip install -r requirements.txt
```

然后启动项目：

```bash
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000
```

账户中心：

```text
http://127.0.0.1:8000/account
```

默认演示账号：

- 普通用户：`demo / 123456`
- 管理员：`admin / 123456`

## 项目结构

```text
campus-market/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.js
│   ├── account.js
│   ├── account.html
│   ├── index.html
│   └── styles.css
└── README.md
```

## 用户角色

- `游客`
  可以浏览首页和商品详情，但不能发布、收藏、留言。
- `普通用户`
  可以发布商品、编辑自己的商品、下架/删除、收藏、留言，并进入账户中心查看自己的数据。普通用户还有 `active / disabled` 两种状态，被禁用后不能登录和操作系统。
- `管理员`
  可以进入账户中心查看和管理全站商品，也可以管理普通用户，适合课堂展示“信息系统中的角色权限”。

## 核心功能

- 用户注册、登录、退出
- 商品列表、搜索、分类筛选
- 商品详情查看
- 商品发布、状态更新
- 收藏商品
- 给卖家留言
- 独立账户中心页面
- 管理员全站商品管理
- 管理员普通用户管理
- 用户启用 / 禁用状态控制
- AI 自动生成商品描述

## 页面结构

- 首页 `/`
  顶部保留项目介绍和展示卡片；第二行左侧是快速发布，右侧是商品广场。
- 账户中心 `/account`
  用户点击头像进入，查看自己的发布、收藏、留言；管理员则可以查看和管理全站商品，并对普通用户进行启用、禁用、删除和查看其发布商品。

## 数据表设计

- `users`
- `categories`
- `items`
- `favorites`
- `messages`

## 运行方式

如果你想从头完整启动，可以按下面顺序执行：

```bash
cd campus-market/backend
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动成功后访问：

```text
http://127.0.0.1:8000
```

如果需要进入账户中心：

```text
http://127.0.0.1:8000/account
```

## 亮点展示

- 前后端和数据库是完整连通的
- 首页和账户中心分离，结构更接近真实系统
- 同时覆盖游客、普通用户、管理员三类角色
- AI 功能不依赖外部大模型，也能现场稳定展示
- 后续可以平滑升级为 `Vue + FastAPI + MySQL`

# 创建GitHub仓库步骤

## 方法1：通过GitHub网页创建

1. 打开浏览器访问：https://github.com/new
2. 登录你的GitHub账号（用户名：coolgnchina）
3. 填写仓库信息：
   - Repository name: `geopark-tuban-manager`
   - Description: `地质公园疑似违法图斑管理系统 - 基于Flask的Web应用`
   - 选择 Public（公开仓库）
   - 不要勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

## 方法2：通过GitHub CLI（如果已安装）

```bash
gh repo create geopark-tuban-manager --public --description "地质公园疑似违法图斑管理系统 - 基于Flask的Web应用"
```

## 推送代码

创建仓库后，在你的项目目录中运行：

```bash
cd "C:\Users\coolgn\OneDrive\桌面\vibe coding\geopark tuban manager\tuban_system"
git remote add origin https://github.com/coolgnchina/geopark-tuban-manager.git
git branch -M main
git push -u origin main
```

## 项目简介

本系统是一个基于Python + Flask的地质公园疑似违法图斑管理系统，主要功能包括：

- 图斑信息管理（增删改查）
- Excel数据导入导出
- 整改跟踪记录
- 统计分析图表
- 系统字典管理
- 用户登录认证

技术栈：
- Python 3.8+ + Flask 2.3.0
- SQLite数据库
- Bootstrap 5前端框架
- Chart.js图表库
- pandas/openpyxl数据处理
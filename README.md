# 地质公园疑似违法图斑管理系统

## 系统简介

本系统是一个基于Python + Flask + SQLite + Bootstrap的Web应用，用于管理地质公园内的疑似违法图斑信息，包括图斑录入、整改跟踪、统计分析等功能。

## 技术栈

- **后端**: Python 3.8+, Flask 2.3.0, Flask-SQLAlchemy 3.0.0
- **数据库**: SQLite
- **前端**: Bootstrap 5, jQuery, Chart.js
- **数据处理**: pandas, openpyxl

## 功能特性

### 核心功能
1. **图斑管理**
   - 图斑信息录入与编辑
   - 多条件筛选与搜索
   - 详情查看
   - Excel导入/导出

2. **整改跟踪**
   - 整改进度记录
   - 整改期限预警
   - 时间线展示

3. **统计分析**
   - 仪表盘概览
   - 问题类型分布
   - 月度趋势分析
   - 地质公园排名

4. **系统管理**
   - 字典管理（下拉选项）
   - 用户登录（简化版）

### 数据字段
系统包含38个字段，分为7大类：
- 基础信息（8项）
- 建设主体信息（4项）
- 发现与核查信息（5项）
- 问题与违法信息（6项）
- 整改信息（6项）
- 处罚信息（4项）
- 管理信息（5项）

## 安装与运行

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. **克隆或下载项目**
```bash
git clone [项目地址]
cd tuban_system
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python init_db.py
```

5. **启动应用**
```bash
python app.py
```

6. **访问系统**
打开浏览器访问：http://localhost:5000

默认登录账号：admin
默认密码：admin123

## 使用说明

### 登录系统
1. 访问 http://localhost:5000
2. 使用默认账号密码登录
3. 建议首次登录后修改密码

### 主要功能

#### 1. 图斑管理
- **新增图斑**: 点击"新增图斑"按钮，填写完整信息后保存
- **编辑图斑**: 在列表页点击"编辑"按钮或通过详情页编辑
- **搜索筛选**: 支持按图斑编号、地质公园、问题类型等条件筛选
- **导出Excel**: 点击"导出Excel"按钮导出当前筛选结果
- **导入Excel**: 点击"Excel导入"按钮，选择符合模板格式的文件

#### 2. 整改跟踪
- 在图斑详情页查看整改进展
- 点击"添加跟踪记录"更新整改状态
- 系统会自动标识超期图斑

#### 3. 统计分析
- 首页仪表盘显示关键指标
- 统计分析页面提供多维度图表
- 支持问题类型、功能区、整改进展等分析

#### 4. 系统设置
- 字典管理：维护下拉选项数据
- 可添加、编辑、删除字典项

### Excel导入模板
系统提供标准Excel模板，包含所有38个字段。导入前请：
1. 下载模板文件
2. 按格式填写数据
3. 确保必填字段完整
4. 日期格式为YYYY-MM-DD
5. 坐标使用十进制度格式

## 项目结构

```
tuban_system/
├── app.py                 # Flask应用主文件
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── init_db.py            # 数据库初始化脚本
├── database/
│   └── tubans.db         # SQLite数据库文件
├── models/               # 数据模型
│   ├── __init__.py
│   ├── tuban.py          # 图斑模型
│   ├── dictionary.py     # 字典模型
│   └── rectify_record.py # 整改记录模型
├── routes/               # 路由处理
│   ├── __init__.py
│   ├── tuban.py          # 图斑管理路由
│   ├── stats.py          # 统计分析路由
│   └── system.py         # 系统管理路由
├── templates/            # HTML模板
│   ├── base.html         # 基础模板
│   ├── login.html        # 登录页
│   ├── index.html        # 首页仪表盘
│   ├── tuban_list.html   # 图斑列表
│   ├── tuban_detail.html # 图斑详情
│   ├── tuban_form.html   # 图斑表单
│   ├── stats.html        # 统计分析
│   └── dictionaries.html # 字典管理
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 自定义样式
│   └── js/               # JavaScript文件
└── utils/                # 工具函数
    ├── __init__.py
    ├── helpers.py        # 辅助函数
    └── excel_handler.py  # Excel处理
```

## 开发说明

### 数据库模型
- 使用SQLAlchemy ORM
- 支持软删除（is_deleted字段）
- 自动记录创建和更新时间

### 前端特性
- 响应式设计，适配移动端
- Bootstrap 5组件
- Chart.js图表库
- 侧边栏导航

### 安全考虑
- 基础登录验证
- 表单输入验证
- XSS防护（模板自动转义）
- 文件上传限制

## 注意事项

1. **开发环境**: 当前为开发环境，请勿直接用于生产
2. **数据备份**: 建议定期备份数据库文件
3. **字符编码**: 确保系统使用UTF-8编码
4. **浏览器兼容**: 推荐使用Chrome、Firefox、Edge等现代浏览器

## 扩展功能建议

1. **地图集成**: 接入高德/百度地图API显示图斑位置
2. **用户管理**: 完善用户角色权限系统
3. **通知提醒**: 整改期限前自动提醒
4. **移动端**: 开发微信小程序或移动APP
5. **数据同步**: 与上级部门系统对接

## 技术支持

如有问题或建议，请联系开发团队。

---

**版本**: 1.0.0
**更新日期**: 2025-12-12
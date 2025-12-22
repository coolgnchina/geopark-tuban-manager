[根目录](../../CLAUDE.md) > **tuban_system**

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 模块职责

tuban_system 是地质公园疑似违法图斑管理系统的核心模块，负责整个Web应用的运行。该模块实现了图斑信息的全生命周期管理，包括录入、查询、整改跟踪、统计分析等功能。

## 入口与启动

### 应用入口文件
- **开发环境**: `app.py` - 启用调试模式，适合开发阶段
- **生产环境**: `app_prod.py` - 优化性能配置，适合生产部署

### 启动方式
```bash
# 开发模式
python app.py

# 生产模式
python app_prod.py

# 使用批处理脚本（Windows）
start_optimized.bat    # 生产环境启动
restart_full.bat       # 完整重启（包含清理）
restart_en.bat         # 快速重启
```

### 工厂模式实现
应用使用工厂模式创建Flask实例：
```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # 初始化扩展、注册蓝图、配置模板等
    return app
```

## 对外接口

### Blueprint组织结构
系统采用Blueprint模块化组织，每个Blueprint负责特定功能域：

1. **tuban_bp** (`/tuban`)
   - 图斑列表查看: `/tuban/list`
   - 图斑详情: `/tuban/detail/<id>`
   - 新增图斑: `/tuban/add`
   - 编辑图斑: `/tuban/edit/<id>`
   - Excel导入: `/tuban/import_excel`
   - Excel导出: `/tuban/export_excel`

2. **stats_bp** (`/stats`)
   - 统计仪表盘: `/stats/dashboard`
   - 问题类型分析: `/stats/problem_analysis`
   - 月度趋势: `/stats/monthly_trend`

3. **system_bp** (`/system`)
   - 字典管理: `/system/dictionaries`
   - 字典增删改: `/system/dictionary/<action>`

4. **map_bp** (`/map`)
   - 地图视图: `/map/view`
   - 图斑分布: `/map/distribution`

### 认证与授权
- 基于Session的简单认证机制
- 默认账号: admin/admin123
- 通过before_request钩子进行登录验证
- 公开端点白名单：login、static、export_excel、import_excel

## 关键依赖与配置

### 核心依赖
```
Flask==2.3.0              # Web框架
Flask-SQLAlchemy==3.0.0   # ORM
pandas==2.0.0            # 数据处理
openpyxl==3.1.0          # Excel处理
python-dateutil==2.8.2   # 日期处理
```

### 配置管理 (config.py)
- **数据库**: SQLite (`database/tubans.db`)
- **上传限制**: 16MB
- **分页设置**: 每页20条记录
- **Excel格式**: 支持.xlsx和.xls
- **日期格式**: YYYY-MM-DD

### 数据库模型关系
```
Tuban (图斑主表)
├── 关联 RectifyRecord (一对多)
└── 引用 Dictionary (多对一，通过dict_type)
```

## 数据模型

### Tuban模型（38个字段）
1. **基础信息** (8项)
   - tuban_code: 图斑编号（唯一）
   - park_name: 地质公园名称
   - func_zone: 功能区（核心区/缓冲区/实验区）
   - facility_name: 活动/设施名称
   - longitude/latitude: 经纬度坐标
   - area: 占地面积
   - image_date: 影像时相

2. **建设主体信息** (4项)
   - build_unit: 建设单位
   - build_time: 建设时间
   - has_approval: 是否有审批手续
   - approval_no: 审批文号

3. **发现与核查信息** (5项)
   - discover_time/discover_method: 发现时间和方式
   - check_time/check_person: 核查时间和人员
   - check_result: 核查结论

4. **问题与违法信息** (6项)
   - problem_type/problem_desc: 问题类型和描述
   - geo_heritage_type: 涉及地质遗迹类型
   - impact_level: 影响程度（严重/一般/轻微）
   - is_illegal/violated_law: 是否违法及违反条款

5. **整改信息** (6项)
   - rectify_measure: 整改措施
   - rectify_deadline: 整改时限
   - rectify_status: 整改进展（未整改/整改中/已整改）
   - rectify_verify_time: 验收时间
   - verify_person: 验收人员
   - is_closed: 是否销号

6. **处罚信息** (4项)
   - is_punished: 是否处罚
   - punish_type: 处罚形式
   - fine_amount: 罚款金额
   - punish_doc_no: 处罚文书编号

7. **管理信息** (5项)
   - data_source: 数据来源
   - is_patrol_point: 是否巡查点
   - responsible_dept: 责任部门
   - attachments: 附件路径
   - remark: 备注

### 软删除设计
所有模型使用 `is_deleted` 字段实现软删除：
- 0: 未删除
- 1: 已删除（逻辑删除）

## 测试与质量

### 测试框架
- 使用pytest进行单元测试
- 测试文件位置: `tests/`
- 主要测试类: `test_tuban.py`

### 代码质量工具
- 建议使用flake8进行代码风格检查
- 使用black进行代码格式化

### 性能优化
1. **数据库优化**
   - 为常用查询字段添加索引
   - 使用分页减少大数据集查询

2. **前端优化**
   - 静态资源本地化（避免CDN依赖）
   - 压缩CSS/JS文件
   - 使用Bootstrap Icons的Unicode回退

3. **生产环境配置**
   - 关闭调试模式
   - 启用线程支持
   - 禁用自动重载

## 常见问题 (FAQ)

### Q: Excel导入失败怎么办？
A: 检查以下几点：
1. 确保使用系统提供的模板
2. 检查必填字段是否完整
3. 日期格式必须为YYYY-MM-DD
4. 坐标使用十进制度格式
5. 文件大小不超过16MB

### Q: 如何备份数据？
A: 直接复制 `database/tubans.db` 文件即可

### Q: 忘记管理员密码怎么办？
A: 在登录页使用默认账号 admin/admin123，建议首次登录后修改

### Q: 如何修改端口？
A: 编辑 `app.py` 或 `app_prod.py`，修改 `app.run()` 的 `port` 参数

## 相关文件清单

### 核心文件
- `app.py` - 应用主文件
- `app_prod.py` - 生产环境启动文件
- `config.py` - 配置文件
- `requirements.txt` - 依赖列表
- `init_db.py` - 数据库初始化

### 模型文件 (models/)
- `__init__.py` - SQLAlchemy实例初始化
- `tuban.py` - 图斑主模型
- `dictionary.py` - 字典模型
- `rectify_record.py` - 整改记录模型

### 路由文件 (routes/)
- `__init__.py` - 路由包初始化
- `tuban.py` - 图斑管理路由
- `stats.py` - 统计分析路由
- `system.py` - 系统管理路由
- `map.py` - 地图功能路由

### 工具文件 (utils/)
- `__init__.py` - 工具包初始化
- `helpers.py` - 通用辅助函数
- `excel_handler.py` - Excel处理逻辑

### 模板文件 (templates/)
- `base.html` - 基础模板
- `index.html` - 首页仪表盘
- `login.html` - 登录页
- `tuban_*.html` - 图斑相关页面
- `stats.html` - 统计页面
- `dictionaries.html` - 字典管理页

### 静态资源 (static/)
- `css/style.css` - 自定义样式
- `js/` - JavaScript文件

### 批处理脚本
- `start_optimized.bat` - 生产环境启动
- `restart_full.bat` - 完整重启脚本
- `restart_en.bat` - 快速重启脚本

## 变更记录 (Changelog)

### 2025-12-22
- 更新模块级文档结构
- 添加详细的字段说明
- 完善常见问题解答
- 添加文件清单索引
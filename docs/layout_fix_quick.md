# 页面布局宽度限制问题 - 通用修复方案

## 问题

页面内容区域被CSS限制宽度，导致无法使用全宽。

典型表现：
- 右侧 `col-lg-4` 区域看起来很空
- 页面内容没有占满整个可用宽度
- 与其他页面布局不一致

## 诊断方法

```bash
# 检查页面是否有宽度限制样式
curl -s "http://127.0.0.1:5000/页面路径" | grep -A5 "page-content-wrapper"

# 对比正常页面的样式
curl -s "http://127.0.0.1:5000/正常页面" | grep -A5 "page-content-wrapper"
```

## 通用修复方案

### 步骤1：在页面模板中添加样式覆盖

在 `{% block content %}` 开头添加：

```html
<style>
/* 覆盖全局宽度限制 */
#page-content-wrapper {
    max-width: 100% !important;
    width: calc(100vw - 260px) !important;
    margin-left: 260px !important;
}
</style>
```

### 步骤2：移除全局CSS限制

编辑 `static/css/style.css`，搜索并移除所有：

```css
max-width: calc(100vw - var(--sidebar-width));
max-width: calc(100vw - var(--sidebar-collapsed-width));
```

替换为：

```css
max-width: 100%;
```

### 步骤3：清理页面内联样式

如页面中有类似：

```html
<div class="content-wrapper">
```

可添加内联覆盖：

```html
<div class="content-wrapper" style="max-width: 100% !important;">
```

## 参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `260px` | `var(--sidebar-width)` | 侧边栏宽度 |
| `100vw` | 视口宽度 | CSS单位 |

## 快速定位

```bash
# 搜索所有宽度限制
grep -rn "calc(100vw" static/css/

# 搜索所有max-width限制
grep -rn "max-width" static/css/ | grep -v "100%"
```

## 验证

刷新页面，检查：
1. 页面是否占满宽度
2. 右侧区域是否正常显示
3. 侧边栏是否正常

## 相关文件

- `static/css/style.css` - 全局样式
- `templates/*.html` - 页面模板

## 日期

2026-01-16

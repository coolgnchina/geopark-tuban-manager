from flask import Blueprint, render_template

# 创建测试蓝图
test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/icons')
def test_icons():
    """图标测试页面"""
    return render_template('test_icons.html')

@test_bp.route('/favicon.ico')
def favicon():
    """返回favicon.ico - 避免404错误"""
    return "", 204  # No Content

@test_bp.route('/unicode')
def test_unicode():
    """Unicode图标测试页面"""
    return render_template('test_unicode_icons.html')
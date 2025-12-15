#!/usr/bin/env python
"""
更新模板文件中的CDN链接为本地链接
"""

import os
import re
from pathlib import Path

# CDN到本地资源的映射
cdn_to_local = {
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css': '/static/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js': '/static/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css': '/static/css/bootstrap-icons.css',
    'https://code.jquery.com/jquery-3.6.0.min.js': '/static/js/jquery.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js': '/static/js/chart.js'
}

def update_file(file_path):
    """更新单个文件中的CDN链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 替换CDN链接
        for cdn_url, local_url in cdn_to_local.items():
            # 替换完整的CDN链接
            content = content.replace(cdn_url, local_url)

            # 替换使用url_for的CDN链接
            content = content.replace(f"'{cdn_url}'", f"'{local_url}'")
            content = content.replace(f'"{cdn_url}"', f'"{local_url}"')

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[UPDATED] {file_path}")
            return True
        else:
            print(f"[SKIP] {file_path} - No changes needed")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to update {file_path}: {str(e)}")
        return False

def main():
    print("Updating CDN links in templates...")
    print("-" * 50)

    templates_dir = Path('templates')
    updated_count = 0
    total_files = 0

    # 遍历所有模板文件
    for template_file in templates_dir.rglob('*.html'):
        total_files += 1
        if update_file(template_file):
            updated_count += 1

    print("-" * 50)
    print(f"Update completed: {updated_count}/{total_files} files modified")

    if updated_count > 0:
        print("\n[SUCCESS] CDN links have been updated to local paths!")
        print("\nNext step: Restart the server")
    else:
        print("\n[INFO] No files needed updating")

if __name__ == '__main__':
    main()
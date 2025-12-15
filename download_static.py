#!/usr/bin/env python
"""
下载所有CDN资源到本地，解决网络访问问题
"""

import os
import requests
from pathlib import Path

# CDN资源列表
cdn_resources = [
    # Bootstrap CSS
    {
        'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
        'local_path': 'static/css/bootstrap.min.css'
    },
    # Bootstrap JS
    {
        'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
        'local_path': 'static/js/bootstrap.bundle.min.js'
    },
    # Bootstrap Icons CSS
    {
        'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css',
        'local_path': 'static/css/bootstrap-icons.css'
    },
    # Bootstrap Icons fonts
    {
        'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2',
        'local_path': 'static/css/fonts/bootstrap-icons.woff2'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff',
        'local_path': 'static/css/fonts/bootstrap-icons.woff'
    },
    # jQuery
    {
        'url': 'https://code.jquery.com/jquery-3.6.0.min.js',
        'local_path': 'static/js/jquery.min.js'
    },
    # Chart.js
    {
        'url': 'https://cdn.jsdelivr.net/npm/chart.js',
        'local_path': 'static/js/chart.js'
    }
]

def download_resource(url, local_path):
    """下载单个资源"""
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 确保目录存在
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"[OK] Saved to: {local_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed: {url} - {str(e)}")
        return False

def main():
    print("Starting to download CDN resources to local...")
    print("-" * 50)

    success_count = 0
    total_count = len(cdn_resources)

    for resource in cdn_resources:
        if download_resource(resource['url'], resource['local_path']):
            success_count += 1

    print("-" * 50)
    print(f"Download completed: {success_count}/{total_count} resources")

    if success_count == total_count:
        print("\n[SUCCESS] All resources downloaded successfully!")
        print("\nNext steps:")
        print("1. Run update_templates.py to update CDN links in templates")
        print("2. Restart the server")
    else:
        print(f"\n[WARNING] {total_count - success_count} resources failed to download")

if __name__ == '__main__':
    main()
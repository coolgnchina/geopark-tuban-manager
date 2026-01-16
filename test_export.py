import requests
import os
import re
import urllib.parse
from datetime import datetime


# 测试Excel导出功能
def test_export():
    # 登录获取cookie
    login_url = "http://127.0.0.1:5000/login"
    export_url = "http://127.0.0.1:5000/tuban/export_excel"

    # 登录数据
    login_data = {
        "username": "admin",
        "password": "admin123",
    }

    # 创建session
    session = requests.Session()

    # 获取CSRF Token
    login_page = session.get(login_url)
    token_match = re.search(r'name="_csrf_token"\s+value="([^"]+)"', login_page.text)
    if not token_match:
        print("未能获取CSRF Token")
        return
    login_data["_csrf_token"] = token_match.group(1)

    # 登录
    login_response = session.post(login_url, data=login_data)

    print(f"登录状态码: {login_response.status_code}")
    print(f"登录响应头: {dict(login_response.headers)}")
    if login_response.status_code != 200 and login_response.status_code != 302:
        print("登录失败")
        print(f"登录响应: {login_response.text}")
        return

    # 导出Excel
    export_response = session.get(export_url)

    # 检查响应
    print(f"状态码: {export_response.status_code}")
    print(f"响应头: {dict(export_response.headers)}")

    # 如果是文件下载
    if (
        export_response.status_code == 200
        and "content-disposition" in export_response.headers
    ):
        # 获取文件名
        content_disposition = export_response.headers.get("content-disposition", "")
        filename = None

        filename_star_match = re.search(r"filename\*=([^;]+)", content_disposition)
        if filename_star_match:
            filename = urllib.parse.unquote(filename_star_match.group(1))
            if filename.lower().startswith("utf-8''"):
                filename = filename[7:]

        if not filename:
            filename_match = re.search(r'filename="?([^";]+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1)

        if not filename:
            filename = f"图斑数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # 保存文件
        with open(filename, "wb") as f:
            f.write(export_response.content)

        print(f"文件已下载: {filename}")
        print(f"文件大小: {len(export_response.content)} 字节")
    else:
        print("下载失败，响应内容:")
        print(export_response.text[:500])


if __name__ == "__main__":
    test_export()

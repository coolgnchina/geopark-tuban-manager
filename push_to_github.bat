@echo off
echo 正在推送到GitHub...
echo.

REM 添加远程仓库
git remote add origin https://github.com/coolgnchina/geopark-tuban-manager.git

REM 重命名分支
git branch -M main

REM 推送到GitHub
git push -u origin main

echo.
echo 推送完成！
echo.
echo 如果推送失败，请确认：
echo 1. 已在GitHub上创建仓库 https://github.com/coolgnchina/geopark-tuban-manager
echo 2. 已登录GitHub账号
echo 3. 网络连接正常
pause
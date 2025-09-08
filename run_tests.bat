@echo off
echo 清理旧报告...
rmdir /s /q reports\allure-results
mkdir reports\allure-results

echo 正在运行测试...
pytest --alluredir=./reports/allure-results

echo 测试完成，生成报告中...
allure serve ./reports/allure-results

pause
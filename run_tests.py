import os
import subprocess
import shutil

# 获取当前脚本所在目录（确保路径正确）
base_dir = os.path.dirname(os.path.abspath(__file__))
reports_dir = os.path.join(base_dir, "reports", "allure-results")

print("=== 清理旧报告 ===")
if os.path.exists(reports_dir):
    shutil.rmtree(reports_dir)  # 删除旧的报告目录
os.makedirs(reports_dir, exist_ok=True)  # 创建新的报告目录

print("=== 正在运行测试（生成 Allure 结果）===")
pytest_cmd = ["pytest", "--alluredir=./reports/allure-results"]
subprocess.run(pytest_cmd, cwd=base_dir)  # 在项目根目录运行 pytest

print("=== 测试完成，生成 Allure 报告 ===")
allure_cmd = ["allure", "serve", "./reports/allure-results"]
subprocess.run(allure_cmd, cwd=base_dir)  # 启动 Allure 服务

input("=== 按回车键退出 ===")  # 相当于 bat 中的 pause
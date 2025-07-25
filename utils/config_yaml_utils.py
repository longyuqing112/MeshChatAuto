# SecureNetAutoWin/utils/yaml_config_utils.py
import pytest
import yaml

class YamlConfigUtils:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_yaml_test_data(self):
        """加载YAML测试数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            pytest.fail(f"测试数据文件 {self.file_path} 未找到")
        except yaml.YAMLError as e:
            pytest.fail(f"YAML文件解析失败: {str(e)}")

    # def  load_test_data(file_path):
    #     """加载指定路径的 YAML 测试数据"""
    #     yaml_utils = YamlConfigUtils(file_path)
    #     return yaml_utils.load_yaml_test_data()

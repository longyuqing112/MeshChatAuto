# SecureNetAutoWin/utils/config_utils.py
import  json
import os
from pathlib import Path

import yaml
from jinja2 import Template


class ConfigUtils:
    _template_context = {
        "USERNAME": os.getenv("APP_USERNAME", "19911111111"),
        "PASSWORD": os.getenv("APP_PASSWORD", "111111a"),
        "ID": os.getenv("APP_ID", "OWQt9z32"),
    }
    def __init__(self, config_file):
        self.config_file = Path(config_file)

    def _render_template(self,content):
        if "{{" in content and "}}" in content:
            return Template(content).render(**self._template_context)
        return content

    def read_config(self,render_vars=False):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"数据文件{self.config_file}不存在/没找到")
        with open(self.config_file, "r", encoding="utf-8") as f:
            content = f.read()

            if render_vars:
                content = self._render_template(content)
                # 自动识别JSON/YAML格式
            if self.config_file.suffix == '.json':
                return json.loads(content)
            return yaml.safe_load(content)
            # return json.loads(f.read())

    def write_config(self, data):
        """写入配置文件（自动识别格式）"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            if self.config_file.suffix == '.json':
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                yaml.safe_dump(data, f, allow_unicode=True)

    def clear_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)


# if __name__ == "__main__":
#     app_utils =  ("config/app_settings.json")
#     app_config = app_utils.read_config()  # 不渲染

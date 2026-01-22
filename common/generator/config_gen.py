from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typeguard import typechecked

from common import ver_check
from common.decorator import log_run_time
from common.utils.time_util import get_time_iso_string

"""
     - 配置文件生成器
     基于 Pydantic 的 BaseModel 实例自动生成带注释、格式化的 YAML 配置字符串
     用于将结构化的配置模型转换为人类可读的 YAML 配置文件
"""
class ConfigFileGenerator:

    # 初始化 YAML 字符串缓冲区和缩进量（默认 2 个空格）
    def __init__(self, indent: int = 2):
        self._yaml_str = ""
        self._indent = indent

    # 据嵌套深度生成对应数量的空格缩进
    def _get_indent(self, depth: int):
        return " " * self._indent * depth

    # 解析 FieldInfo 中的描述信息，生成 YAML 注释行
    def _add_comments(self, field_info: FieldInfo, depth: int):
        if field_info.description:
            for description_line in field_info.description.split("\n"):
                self._yaml_str += self._get_indent(depth) + f"# {description_line}\n"

    # 遍历 BaseModel 的字段，递归处理嵌套的 BaseModel，并根据字段类型（枚举、字符串、数字等）格式化 YAML 行：
    def _gen(self, model: BaseModel, depth: int = 0):
        fields = model.model_fields

        for field_name, field_info in fields.items():
            field_val = model.__getattribute__(field_name)
            if isinstance(field_val, BaseModel):
                self._add_comments(field_info, depth)
                self._yaml_str += self._get_indent(depth) + f"{field_name}:\n"
                self._gen(field_val, depth + 1)
            else:
                self._add_comments(field_info, depth)
                if isinstance(type(field_val), type(Enum)):
                    self._yaml_str += self._get_indent(depth) + f"{field_name}: '{field_val.value}'\n"
                elif isinstance(field_val, str):
                    self._yaml_str += self._get_indent(depth) + f"{field_name}: '{field_val}'\n"
                else:
                    self._yaml_str += self._get_indent(depth) + f"{field_name}: {field_val}\n"

    # 生成包含生成时间的注释头
    def _get_header(self):
        generated_info = f"# This file was generated at {get_time_iso_string()} #"
        header = "#" * len(generated_info) + "\n" \
                 + generated_info + "\n" \
                 + "#" * len(generated_info) + "\n"

        return header

    # 入口方法，校验 Pydantic 版本，调用递归生成逻辑，拼接头部和主体返回最终 YAML 字符串
    @log_run_time()
    @typechecked
    def generate_yaml(self, model: BaseModel):
        """
        Generate yaml from BaseModel instance.
        :param model: An instance of BaseModel.
        :return: Yaml string.
        """
        ver_check.check_pydantic_ver()
        self._gen(model, depth=0)
        return self._get_header() + "\n" + self._yaml_str

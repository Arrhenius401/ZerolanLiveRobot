from enum import Enum
from typing import Type, Any, List

from typeguard import typechecked

# 提取枚举所有成员的 value，转为列表
def enum_members_to_list(enum: Type[Enum]) -> List[Any]:
    return [member.value for member in enum]

# 提取枚举所有成员的 value，转为字符串列表
@typechecked
def enum_members_to_str_list(enum: Type[Enum]) -> List[str]:
    return [str(elm.value) for elm in list(enum)]

# 内部函数：枚举 value 转「value1, value2」格式文本
@typechecked
def _enum_members_to_plain_text_with_comma(enum: Type[Enum]) -> str:
    str_list = enum_members_to_str_list(enum)
    text = ""
    for string in str_list:
        text += "`" + string + "`" + ", "
    return text[:-2]

# 枚举转为英文 markdown 说明文本
@typechecked
def enum_to_markdown(enum: Type[Enum]) -> str:
    num_of_enum = len(enum)
    if num_of_enum == 1:
        return f"`{list(enum)[0].value}` is supported only."
    else:
        candidates = _enum_members_to_plain_text_with_comma(enum)
        return f"{candidates} are supported."

# 枚举转为中文 markdown 说明文本
@typechecked
def enum_to_markdown_zh(enum: Type[Enum]) -> str:
    num_of_enum = len(enum)
    if num_of_enum == 1:
        return f"仅支持 `{list(enum)[0].value}`。"
    else:
        candidates = _enum_members_to_plain_text_with_comma(enum)
        return f"支持 {candidates}。"


def try_get_pynput_key_enum_str():
    try:
        from pynput.keyboard import Key

        return '`' + '`, `'.join(list(Key.__members__.keys())[:40]) + '`'
    except ImportError:
        from loguru import logger
        logger.warning(f'Pynput not installed, please try "pip install pynput" to solve this problem.')
        return '`Error: Please install `pynput` and try again`'

"""
Author: Github@AkagawaTsurunaki
Notes:
    GLM-4 输出的 JSON 结果可能会带有 Markdown 代码块标记，以及出现的多余的右大括号。
    提示词调整后依旧无效，为了防止还有其他模型具有相同错误，特使用此模块从一个错误的 JSON 字符串中尝试恢复。
"""

import json
from json import JSONDecodeError

# 从混杂的文本中提取 JSON 片段（仅提取第一个 JSON 对象 / 数组的首尾）
def _extract_json_from_text(text: str):
    """
    从如下的文档中获取JSON字符串：
    ...
    ```json
    {
        ...
    }
    ```
    ...
    文档中必须只有一个 JSON 对象。
    Args:
        text:

    Returns:
    """
    start, end = 0, len(text)
    for i in range(len(text)):
        if text[i] == "{" or text[i] == "[":
            start = i
            break
    for i in range(len(text)):
        j = len(text) - i - 1
        if text[j] == "}" or text[j] == "]":
            end = j
            break
    return text[start:end + 1]

# 移除 JSON 字符串末尾多余的右大括号，尝试解析直到成功
def _remove_end_extra_braces(text: str):
    """
    {...}
    Args:
        text:

    Returns:

    """
    errs = []
    n = text.count("}")
    for i in range(n):
        j = len(text) - i
        new_text = text[:j]
        try:
            return json.loads(new_text)
        except JSONDecodeError as e:
            errs.append(e)
    raise errs[-1]

# 对外接口
def smart_load_json_like(content: str):
    json_val = _extract_json_from_text(content)
    json_val = _remove_end_extra_braces(json_val)
    return json_val

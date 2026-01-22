from typing import List

from common.enumerator import Language

# 校验字符串是否为 “空
def is_blank(s: str) -> bool:
    """Check if a string is None, empty, or contains only whitespace."""
    return s is None or not s.strip() or s == ""

# 按指定语言的标点符号分割文本
def split_by_punc(text: str, lang: Language) -> List[str]:
    if lang == Language.ZH:
        cut_punc = "，。！？"
    elif lang == Language.JA:
        cut_punc = "、。！？"
    else:
        cut_punc = ",.!?"

    def punc_cut(text: str, punc: str):
        texts = []
        last = -1
        for i in range(len(text)):
            if text[i] in punc:
                try:
                    texts.append(text[last + 1: i])
                except IndexError:
                    continue
                last = i
        return texts

    return punc_cut(text, cut_punc)

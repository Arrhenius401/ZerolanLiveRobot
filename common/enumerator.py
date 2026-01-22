from enum import Enum

# 枚举基类
class BaseEnum(str, Enum):
    pass

# 语言枚举类
class Language(str, Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"

    # 返回语言的全名
    def full_name(self):
        if self == self.ZH:
            return "Chinese"
        elif self == self.EN:
            return "English"
        elif self == self.JA:
            return "Japanese"
        else:
            raise ValueError("Unknown language")

    # 返回语言的简写
    def name(self):
        if self == self.ZH:
            return "zh"
        elif self == self.EN:
            return "en"
        elif self == self.JA:
            return "ja"
        else:
            raise ValueError("Unknown language")

    # 返回语言的中文名称
    def to_zh_name(self):
        if self == self.ZH:
            return "中文"
        elif self == self.EN:
            return "英文"
        elif self == self.JA:
            return "日语"
        else:
            raise ValueError("Unknown language")

    # 获取语言枚举
    @staticmethod
    def value_of(s: str):
        s = s.lower()
        if s in ["en", "english", "英文", "英语"]:
            return Language.EN
        elif s in ["zh", "cn", "chinese", "中文"]:
            return Language.ZH
        elif s in ["ja", "japanese", "日语", "日本語", "にほんご"]:
            return Language.JA
        else:
            raise ValueError("Unknown language")

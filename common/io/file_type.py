from enum import Enum

""" 音频文件类型枚举类 """
class AudioFileType(str, Enum):
    FLV = 'flv'
    WAV = 'wav'
    OGG = 'ogg'
    MP3 = 'mp3'
    RAW = 'raw'

""" 图片文件类型枚举类 """
class ImageFileType(str, Enum):
    PNG = 'png'
    JPEG = 'jpeg'
    JPG = 'jpg'

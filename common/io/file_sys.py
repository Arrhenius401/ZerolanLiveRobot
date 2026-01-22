import os
import uuid
import zipfile
from pathlib import Path
from typing import Literal

from typeguard import typechecked

from common.utils.time_util import get_time_string

ResType = Literal["image", "video", "audio", "model"]

"""
    - 文件系统操作类
    提供项目目录、临时目录的路径获取和临时文件创建功能
"""
class FileSystem:
    def __init__(self):
        self._proj_dir: Path | None = None
        self._temp_dir: Path | None = None
        self._create_temp_dir()

    # 初始化临时目录，并创建 image/audio/video/model 子目录
    def _create_temp_dir(self):
        self.temp_dir.mkdir(exist_ok=True)
        for dir_name in ["image", "audio", "video", "model"]:
            self.temp_dir.joinpath(dir_name).mkdir(exist_ok=True)

    # 自动识别项目根目录（若当前工作目录是 tests，则取父目录），返回绝对路径
    @property
    def project_dir(self) -> Path:
        """
        Get project directory path.
        :return: Project directory path.
        """
        if self._proj_dir is None:
            cur_work_dir = os.getcwd()
            if Path(cur_work_dir).name == "tests":
                dir_path = Path(cur_work_dir).parent
                self._proj_dir = Path(dir_path)
            else:
                self._proj_dir = Path(cur_work_dir)
        return self._proj_dir.absolute()

    # 默认指向项目根目录下的 .temp/，自动创建
    @property
    def temp_dir(self) -> Path:
        """
        Get temp directory path.
        :return: Temp directory path.
        """
        if self._temp_dir is None:
            self._temp_dir = self.project_dir.joinpath('.temp/')
        return self._temp_dir.absolute()

    # 生成带前缀、后缀、时间戳的临时文件路径（按资源类型放入对应子目录），自动处理后缀的 . 前缀（如 .wav → wav）
    @typechecked
    def create_temp_file_descriptor(self, prefix: str, suffix: str, type: ResType) -> Path:
        """
        Create temp file descriptor.
        :param prefix: Prefix that at the beginning of the file name.
        :param suffix: Suffix that at the end of the file name. Usually file type. For example .wav
        :param type: Temp resource type. See ResType.
        :return:
        """
        self.temp_dir.mkdir(exist_ok=True)
        if suffix[0] == '.':
            suffix = suffix[1:]
        filename = f"{prefix}-{get_time_string()}-{uuid.uuid4()}.{suffix}"
        typed_dir = self.temp_dir.joinpath(type)
        typed_dir.mkdir(exist_ok=True)
        return typed_dir.joinpath(filename).absolute()

    # 递归遍历指定目录，查找包含目标名称的子目录，返回绝对路径（未找到返回 None）
    @typechecked
    def find_dir(self, dir_path: str, tgt_dir_name: str) -> Path | None:
        """
        Walk in tgt_dir_name, and find if dir_path exists
        :param dir_path: Directory path to walk.
        :param tgt_dir_name: Target directory name to find.
        :return: Path if found, else None
        """
        assert os.path.exists(dir_path), f"{dir_path} doesn't exist."
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for dirname in dirnames:
                if tgt_dir_name in dirname:
                    path = os.path.join(dirpath, dirname)
                    return Path(path).absolute()
        return None

    # 将指定目录下的所有文件压缩为 ZIP 包（追加模式，保留相对路径）
    @typechecked
    def compress(self, src_dir: str | Path, tgt_dir: str | Path):
        src_dir = Path(src_dir).absolute()

        with zipfile.ZipFile(tgt_dir, 'a', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=src_dir)
                    zipf.write(file_path, arcname=arcname)


fs = FileSystem()

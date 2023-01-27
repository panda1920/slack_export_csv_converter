from pathlib import Path
from typing import List

from slack_export_csv_converter.exceptions import ConverterException

# abstracts away the directory structure of slack exports
class ExportDir:
  USERS_FILE_NAME = 'users.json'

  def __init__(self, export_dir: Path):
    self._check_exists(export_dir)
    self._export_dir = export_dir

  def get_users_file(self) -> Path:
    """
    Get path to a file containing user information of slack
    """
    users_file = self._export_dir / self.USERS_FILE_NAME
    self._check_exists(users_file)

    return users_file

  def get_channel_dirs(self) -> List[Path]:
    """
    Get path to all the channels
    """
    return [
      dir for dir in self._export_dir.iterdir() if dir.is_dir()
    ]

  def _check_exists(self, path: Path) -> None:
    if not path.exists():
      raise ConverterException(f'path {str(path)} does not exist')

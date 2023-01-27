from pathlib import Path
from typing import List, Optional

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

  def get_channel_path(self, channel: str) -> Path:
    """
    A utility function to retrieve channel path from name
    """
    channel_paths = self.get_channel_dirs()
    found_paths = [ path for path in channel_paths if path.stem == channel ]
    
    if len(found_paths) < 1:
      raise ConverterException(f"channel {channel} does not exist")
    
    return found_paths[0]

  def get_message_files(self, channel: str) -> List[Path]:
    """
    Get message files belonging to a channel
    """
    channel_path = self._export_dir / channel
    self._check_exists(channel_path, f"channel {channel} does not exist")
    return [
      file for file in channel_path.iterdir()
      if file.is_file() and file.suffix == ".json"
    ]

  def _check_exists(self, path: Path, fail_msg: Optional[str] = None) -> None:
    if fail_msg == None:
      fail_msg = f'path {str(path)} does not exist'
    
    if not path.exists():
      raise ConverterException(fail_msg)

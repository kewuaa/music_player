from pathlib import Path
import os


__project_data_path = Path(os.environ['Appdata']) / '^3^'
download_path = __project_data_path / 'audios'
config_path = __project_data_path / 'configs'

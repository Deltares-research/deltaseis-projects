import os
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic

load_dotenv()
folder = Path(os.environ["DIS2025_CONVERT_FOLDER"])

segy_files = [Path(f) for f in folder.iterdir() if f.suffix in ('.SEG','.sgy', '.segy')]
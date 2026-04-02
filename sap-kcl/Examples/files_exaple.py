from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os

saps_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "SAPs"
protcols_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "Protocols"


for f in saps_path.iterdir():
    print(f.name)

for f in protcols_path.iterdir():
    print(f.name)

from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import os

saps_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "SAPs"
protocols_path = Path(os.getenv("SAPAI_SHARED_PATH")) / "Protocols"




template.write_sap(
    protocol_path= Path(protocols_path) / "SAATHI2_Phase_III_trial_protocol_May2025.pdf",
    sap_folder_path = saps_path,
    sap_name = "SAATHI2_sap_v0.1",
)



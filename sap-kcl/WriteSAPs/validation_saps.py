from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template

protcol_foler = "Protocols"
saps_folder = "SAPs/Validation"

protocl_folder = 'Protocols/Validation'

protocol_paths = [
    ('star', f'{protocl_folder}/STAR_PROTOCOL_3.06 15.05.25 (CLEAN).pdf'),
    ('reach-asd', f'{protocl_folder}/REACH-ASD Trial Protocol v8 24.02.2022 - CLEAN.pdf'),
    ('rapid', f'{protocl_folder}/RAPID Trial Protocol v9.0 07 JUN 2024 clean.pdf'),
    ('home', f'{protocl_folder}/Protocol_HOME_344318_v1_230725.pdf'),
    ('promise', f'{protocl_folder}/PROMISE Protocol_V3.1_11.pdf'),
    ('attens', f'{protocl_folder}/ATTENS.pdf'),
    ('attend', f'{protocl_folder}/ATTEND WP3+4 Protocol v1.6 08.05.25 CLEAN.pdf'),
    ('actissist', f'{protocl_folder}/ACTISSIST Protocol-v10-11.04.2019_trackchange accepted.pdf'),
    ('diz_ai', f'{protocl_folder}/Manuscript_Stage_1_Registered_Report.pdf'),
    ('eden', f'{protocl_folder}/340838_EDEN+Protocol+v3.0_05.08.2025.pdf'),
]

for sap_name, protocol_path in protocol_paths:
    print(f"Generating SAP for {sap_name}...")
    template.write_sap(
        protocol_path=protocol_path,  
        sap_folder_path=saps_folder,
        sap_name=f"{sap_name}_sap"
    )
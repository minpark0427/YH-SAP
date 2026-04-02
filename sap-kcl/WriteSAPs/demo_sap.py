from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template

template.write_sap(
    protocol_path="Protocols/STOP-D.pdf",  
    sap_folder_path = "SAPs",
    sap_name = "STOP_D_demo",
)

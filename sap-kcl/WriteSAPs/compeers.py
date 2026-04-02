from auto_sap.generate_templates.generate_kcl_template import kcl_template_v02 as template


template.write_sap(
    protocol_path="Protocols/compeers.pdf",  
    sap_folder_path = "SAPs",
    sap_name = "compeers_v0.1",
)

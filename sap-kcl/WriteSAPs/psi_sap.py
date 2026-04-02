from auto_sap.generate_templates.generate_kcl_template_pilot import kcl_template_v02 as template


template.write_sap(
    protocol_path="Protocols/psider.pdf",  
    sap_folder_path = "SAPs",
    sap_name = "psi_test",
    test = True
)


from auto_sap.generate_templates.generate_simple_template import simple_template as template
from auto_sap.classes.protocol_classes import Protocol

protocol_path="Protocols/boppp.pdf" 
json_save_path = "SAPs/boppp_test.json"
protocol = Protocol(protocol_path)


template.get_sap_content(protocol.protocol_txt, model = "gpt-5-nano")
json = template.get_autocode_json(output_path=json_save_path)
print(json)



import yaml

import os

class MiGECBarcodeFileRecord:
    def __init__(self, sample_name, master_barcode, slave_barcode, R1_path, R2_path):
        self.sample_name = sample_name
        self.master_barcode = master_barcode
        self.slave_barcode = slave_barcode
        self.R1_path = R1_path
        self.R2_path = R2_path

    def get_line(self):
        return self.sample_name + "\t" + self.master_barcode + "\t" + self.slave_barcode + \
               "\t" + self.R1_path + "\t" + self.R2_path


class MiGECAction:
    def __init__(self, records, output_folder):
        self.records = records
        self.output_folder = output_folder


class MiGECParser:
    def get_parser_name(self):
        return "migec"

    def on_traverse_down(self, current_map, current_key, current_element):
        if "sub_field_3" in current_element:
            return [current_map["v1"] + current_element["sub_field_3"]]
        else:
            return None

    def aggregate(self, result1, result2):
        return result1 + result2

    def on_traverse_up(self, current_result, current_map, current_key, current_element):
        if "w1" in current_element:
            return current_result


parsers = [MiGECParser()]


def load_yaml(file_name):
    file_name = os.path.abspath(file_name)
    yml = yaml.load(file_name)
    return {'path': file_name, 'root': yml}


with open('traverse_test.yaml') as f:
    s = yaml.load(f)
    (results, actions) = extract_actions(s)
    print("++++++++")
    print("final result = " + str(results))
    print("final actions = " + str(actions))

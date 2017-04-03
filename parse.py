import yaml

import os

from traverser import Traverser, AbstractParser


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


class MiGECParser(AbstractParser):
    def get_parser_name(self):
        return "migec"

    def on_traverse_down(self, fields, current_fields):
        print("GEC: >>>>>>>>>>>>>>>>>>>>>")
        print("GEC: Field values: " + str(fields))
        print("GEC: Fields: " + str(current_fields))
        print("GEC: >>>>>>>>>>>>>>>>>>>>>")
        if "pattern" in current_fields:
            return None, {"stage": "pattern.matched"}
        else:
            return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        print("GEC: <<<<<<<<<<<<<<<<<<<<<")
        print("GEC: Field values: " + str(fields))
        print("GEC: Fields: " + str(current_fields))
        print("GEC: <<<<<<<<<<<<<<<<<<<<<")
        return []


class MiXCRParser:
    def get_parser_name(self):
        return "mixcr"

    def on_traverse_down(self, fields, current_fields):
        print("XCR: >>>>>>>>>>>>>>>>>>>>>")
        print("XCR: Field values: " + str(fields))
        print("XCR: Fields: " + str(current_fields))
        print("XCR: >>>>>>>>>>>>>>>>>>>>>")
        return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        print("XCR: <<<<<<<<<<<<<<<<<<<<<")
        print("XCR: Field values: " + str(fields))
        print("XCR: Fields: " + str(current_fields))
        print("XCR: <<<<<<<<<<<<<<<<<<<<<")
        return []


parsers = [MiGECParser(), MiXCRParser()]


def load_yaml(file_name):
    file_name = os.path.abspath(file_name)
    yml = yaml.load(file_name)
    return {'path': file_name, 'root': yml}


with open('mice_tissues_metadata.yml') as f:
    s = yaml.load(f)
    traverser = Traverser(*parsers)
    traverser.traverse(s)
    # (results, actions) = extract_actions(s)
    print("++++++++")
    # print("final result = " + str(results))
    # print("final actions = " + str(actions))

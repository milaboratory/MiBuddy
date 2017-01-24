import yaml
import copy
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


# class MiGECParser:
#     def get_traverse_map_key(self):
#         return "migec"
#
#     def on_traverse_down(self, current_map, current_key, current_element):
#
#
#     def on_traverse_up(self, current_map, current_key, current_element):
#

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


def extract_actions(yam):
    return traverse_down({}, "root", yam)


def calculate_results_on_traverse_down(current_map, current_key, current_element):
    result = {}
    for parser in parsers:
        parser_name = parser.get_parser_name()
        current_result = parser.on_traverse_down(current_map, current_key, current_element)
        if current_result:
            result[parser_name] = parser.on_traverse_down(current_map, current_key, current_element)
    return result


def calculate_results_on_traverse_up(current_results, current_map, current_key, current_element):
    actions = []
    for parser in parsers:
        parser_name = parser.get_parser_name()
        parser_actions = parser.on_traverse_up(current_results[parser_name], current_map, current_key,
                                               current_element)
        if parser_actions:
            actions += parser_actions
    return actions


def add_results_for_all_parsers(aggregated_results, result):
    for parser in parsers:
        parser_name = parser.get_parser_name()
        if parser_name in result:
            if parser_name in aggregated_results:
                aggregated_results[parser_name] = parser.aggregate(aggregated_results[parser_name],
                                                                   result[parser_name])
            else:
                aggregated_results[parser_name] = result[parser_name]


def traverse_down(current_map, current_key, current_element):
    '''
    :return: (current_result, actions)
    '''
    print("current_map = " + str(current_map))
    print("current_key = " + str(current_key))
    print("current_element = " + str(current_element))
    print("========")

    aggregated_results = {}
    aggregated_actions = []
    if isinstance(current_element, list):
        for e in current_element:
            (current_result, current_actions) = traverse_down(current_map, current_key, e)
            add_results_for_all_parsers(aggregated_results, current_result)
            aggregated_actions += current_actions

    elif isinstance(current_element, dict):
        aggregated_results = calculate_results_on_traverse_down(current_map, current_key, current_element)
        for key, value in current_element.iteritems():
            new_current_map = copy.deepcopy(current_map)
            for key1, value1 in current_element.iteritems():
                if key1 != key:
                    new_current_map[key1] = value1
            (current_result, current_actions) = traverse_down(new_current_map, key, value)
            add_results_for_all_parsers(aggregated_results, current_result)
            aggregated_actions += current_actions
        aggregated_actions += calculate_results_on_traverse_up(aggregated_results,
                                                               current_map, current_key,
                                                               current_element)

    return aggregated_results, aggregated_actions


with open('traverse_test.yaml') as f:
    s = yaml.load(f)
    (results, actions) = extract_actions(s)
    print("++++++++")
    print("final result = " + str(results))
    print("final actions = " + str(actions))

# e1: e 1 value
# v: v value
# aa:
#   - w1: sd
#     q1: asdafs asd a
#     v1: asdaka asd a
#     sub_aa:
#       - sub_field_1: asd
#         sub_field_3: as
#       - sub_field_1: as,bn
#         sub_field_3: fnmg
#   - w1: ssdff
#     q1: asfnnnklas
#     v1: adnms
#     sub_aa:
#       - sub_field_1: aasdsd
#         sub_field_3: asd
#       - sub_field_1: asafnl
#         sub_field_3: asd
#       - sub_field_1: afsjdll
#         sub_field_3: ag

from traverser import format_string
import os.path as op


class MiXCRAction:
    def __init__(self, r1_path, r2_path, full_base_name):
        self.r1_path = r1_path
        self.r2_path = r2_path
        self.full_base_name = full_base_name


class MiXCRParser:
    def get_parser_name(self):
        return "mixcr"

    def on_traverse_down(self, fields, current_fields):
        if ("perform.clonotyping.on" in fields) and fields["stage"] == fields["perform.ig.tcr.clones.assembling.on"]:
            output_path = format_string(fields["output.path"], fields)
            return [MiXCRAction(fields["r1"], fields["r2"], op.join(output_path, fields["name"]))], \
                   {"stage": "ig.tcr.clones.assembled"}
        else:
            return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        return []

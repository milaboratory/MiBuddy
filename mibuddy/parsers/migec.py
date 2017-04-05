from traverser import AbstractParser, format_string
import re


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

    def __repr__(self):
        return self.get_line()

    def __str__(self):
        return self.get_line()


class MiGECAction:
    def __init__(self, records, input_folder, output_folder):
        self.records = records
        self.input_folder = input_folder
        self.output_folder = output_folder

    def __repr__(self):
        return str(self.input_folder + " -> " + self.output_folder + " : " + str(self.records))


class MiGECParser(AbstractParser):
    def get_parser_name(self):
        return "migec"

    def on_traverse_down(self, fields, current_fields):
        # print("GEC: >>>>>>>>>>>>>>>>>>>>>")
        # print("GEC: Field values: " + str(fields))
        # print("GEC: Fields: " + str(current_fields))
        # print("GEC: >>>>>>>>>>>>>>>>>>>>>")
        do_collect = False
        if "pattern" in fields:
            pattern = fields["pattern"]
            for key in current_fields:
                if key.startswith("pattern.collect."):
                    group_id = key.replace("pattern.collect.", "")
                    pattern, count = re.compile(r"\(" + group_id + r":[ACGTRYSWKMBDHVN]+\)", re.IGNORECASE).subn(
                        fields[key], pattern)
                    assert count > 0, "can't find named capture group " + group_id + " in " + pattern
                    do_collect = True

            if do_collect:
                if "pattern.umiassemble.by" in fields:
                    pattern = re.compile(r"\(" + fields["pattern.umiassemble.by"] + r":([ACGTRYSWKMBDHVN]+)\)",
                                         re.IGNORECASE).sub(
                        r"\1", pattern)
                pattern = pattern.replace(" ", "")
                patterns = pattern.split("~")
                assert "name" in current_fields, "no sample name is provided"
                assert "r1" in fields, "no input file for r1"
                sample_name = fields["name"]
                if len(patterns) == 1:
                    assert "r2" not in fields, "single sided pattern for paired-end input"
                    return [MiGECBarcodeFileRecord(sample_name, patterns[0], ".", fields["r1"],
                                                   ".")], {"stage": "assembled.by.umi",
                                                           "r1": sample_name + "_R0.fastq.gz"}
                else:
                    assert "r2" in fields, "paired end pattern for single-end input"
                    return [MiGECBarcodeFileRecord(sample_name, patterns[0], patterns[1], fields["r1"],
                                                   fields["r2"])], {"stage": "assembled.by.umi",
                                                                    "r1": sample_name + "_R1.fastq.gz",
                                                                    "r2": sample_name + "_R2.fastq.gz"}
        return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        # print("GEC: <<<<<<<<<<<<<<<<<<<<<")
        # print("GEC: Field values: " + str(fields))
        # print("GEC: Fields: " + str(current_fields))
        # print("GEC: Results: " + str(aggregated_result))
        # print("GEC: <<<<<<<<<<<<<<<<<<<<<")
        if "r1" in current_fields:
            return [MiGECAction(aggregated_result, fields["absolute.path"],
                                format_string(fields["output.path"], fields))]
        else:
            return []

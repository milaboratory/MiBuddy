from action import AbstractAction, CreateFile
from traverser import AbstractParser, format_string
import re
import os.path as op


class MiGECBarcodeFileRecord(object):
    def __init__(self, paired, sample_name,
                 master_barcode, slave_barcode,
                 r1_path, r2_path,
                 out_r1_path, out_r2_path,
                 asmb_r1_path, asmb_r2_path,
                 do_assemble):
        self.paired = paired
        self.sample_name = sample_name
        self.master_barcode = master_barcode
        self.slave_barcode = slave_barcode
        self.r1_path = r1_path
        self.r2_path = r2_path
        self.out_r1_path = out_r1_path
        self.out_r2_path = out_r2_path
        self.asmb_r1_path = asmb_r1_path
        self.asmb_r2_path = asmb_r2_path
        self.do_assemble = do_assemble

    def get_line(self):
        return self.sample_name + "\t" + self.master_barcode + "\t" + self.slave_barcode + \
               "\t" + self.r1_path + "\t" + self.r2_path

    def __repr__(self):
        return self.get_line()

    def __str__(self):
        return self.get_line()


class MiGECAction(AbstractAction):
    def __init__(self, records, input_folder, output_folder):
        self.records = records
        self.input_folder = input_folder
        self.output_folder = output_folder

    def get_commands(self):
        content = "#SAMPLE_ID\tMASTER\tSLAVE\n"
        for record in self.records:
            content
        return CreateFile(op.join(self.output_folder, "barcodes.txt"), ""),

    def __repr__(self):
        return str(self.input_folder + " -> " + self.output_folder + " : " + str(self.records))


class MiGECParser(AbstractParser):
    def get_parser_name(self):
        return "migec"

    def on_traverse_down(self, fields, current_fields):
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
                do_assemble = False
                if "pattern.umiassemble.by" in fields:
                    # Separating UMI patterns to assemble by
                    umi_assembling_groups = fields["pattern.umiassemble.by"].split("+")

                    pattern_without_umi = pattern

                    # Validating groups
                    for umi_assembling_group in umi_assembling_groups:
                        rp = re.compile(r"\(" + umi_assembling_group + r":([ACGTRYSWKMBDHVN]+)\)", re.IGNORECASE)
                        groups = rp.findall(pattern)
                        assert len(groups) == 1, "wrong number of groups with name " + umi_assembling_group
                        barcode_string = groups[0]
                        wrong_symbols = re.compile(r"([^N]+)").findall(barcode_string)
                        assert len(wrong_symbols) == 0, \
                            "wrong symbols in UMI group (only N letters supported) found \"" + wrong_symbols[0] + \
                            "\" in \"" + barcode_string + "\""
                        pattern = rp.sub(r"\1", pattern)
                        pattern_without_umi = rp.sub("", pattern_without_umi)

                    assert "N" not in pattern_without_umi, \
                        "\"N\" is not supported outside UMI assembling group: " + fields["pattern"]

                output_path = format_string(fields["output.path"], fields)
                pattern = pattern.replace(" ", "")
                patterns = pattern.split("~")
                assert "name" in current_fields, "no sample name is provided"
                assert "r1" in fields, "no input file for r1"
                sample_name = fields["name"]
                if "r2" not in fields:
                    assert len(patterns) == 2 in fields, "paired end pattern for single-end input"
                    out_r_path = op.join(output_path, sample_name + "_R0.fastq.gz")
                    return [MiGECBarcodeFileRecord(sample_name, patterns[0], None, fields["r1"], "."), do_assemble], \
                           {"stage": "assembled.by.umi",
                            "r1": op.join(output_path, sample_name + "_R0.fastq.gz")}
                else:
                    out_r1_path = op.join(output_path, sample_name + "_R1.fastq.gz")
                    out_r2_path = op.join(output_path, sample_name + "_R2.fastq.gz")
                    asmb_r1_path = op.join(output_path, sample_name + "_asmb_R1.fastq.gz")
                    asmb_r2_path = op.join(output_path, sample_name + "_asmb_R2.fastq.gz")
                    if do_assemble:
                        return [MiGECBarcodeFileRecord(True, sample_name, patterns[0], patterns[1],
                                                       fields["r1"], fields["r2"],
                                                       out_r1_path, out_r2_path,
                                                       asmb_r1_path, asmb_r2_path,
                                                       True)], \
                               {"stage": "assembled.by.umi",
                                "r1": asmb_r1_path,
                                "r2": asmb_r2_path}
                    else:
                        return [MiGECBarcodeFileRecord(True, sample_name, patterns[0], patterns[1],
                                                       fields["r1"], fields["r2"],
                                                       out_r1_path, out_r2_path,
                                                       None, None,
                                                       False)], \
                               {"stage": "assembled.by.umi",
                                "r1": out_r1_path,
                                "r2": out_r2_path}
        return None, {}

    def on_traverse_up(self, aggregated_result, fields, current_fields):
        if "r1" in current_fields:
            return [MiGECAction(aggregated_result, fields["absolute.path"],
                                format_string(fields["output.path"], fields))]
        else:
            return []

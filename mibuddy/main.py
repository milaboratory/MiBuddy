import logging
import yaml
import os
import os.path as op
import sys

from parsers.migec import MiGECParser
from parsers.mixcr import MiXCRParser
from traverser import Traverser, merge_dicts


def is_yaml(file_name):
    return file_name.endswith(".yaml") or file_name.endswith(".yml")


def process_folder(folder, root_folder, fields, parsers):
    logging.info("Processing folder: %s", folder)

    fields = merge_dicts(fields,
                         {"absolute.path": folder,
                          "relative.path": op.relpath(folder, root_folder),
                          "stage": "none"})
    logging.info("Fields: %s", fields)

    for f in ["_.yaml", "_.yml"]:
        file = op.join(folder, f)
        if op.exists(file):
            logging.info("Processing file: %s", file)
            with open(file, 'r') as st:
                fields = merge_dicts(fields, yaml.load(st))
            logging.info("Updated fields: %s", fields)
            break

    actions = []

    for f in os.listdir(folder):
        if is_yaml(f) and not f.startswith("_"):
            file = op.join(folder, f)
            logging.info("Processing file: %s", file)
            with open(file, 'r') as st:
                yml = yaml.load(st)
                traverser = Traverser(*parsers)
                actions += traverser.traverse(yml, fields)

    for f in os.listdir(folder):
        file = op.join(folder, f)
        if op.isdir(file):
            actions += process_folder(file, root_folder, fields, parsers)

    return actions


def main():
    logging.basicConfig(level=logging.DEBUG)
    root_folder = op.abspath(sys.argv[1])
    logging.info('Executing MiBuddy for: %s', root_folder)
    actions = process_folder(root_folder, root_folder, {}, [MiGECParser(), MiXCRParser()])
    logging.info("Actions: %s", actions)

if __name__ == "__main__":
    main()

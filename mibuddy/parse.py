import yaml
import os

from parsers.migec import MiGECParser
from parsers.mixcr import MiXCRParser
from traverser import Traverser

parsers = [MiGECParser(), MiXCRParser()]


def load_yaml(file_name):
    file_name = os.path.abspath(file_name)
    yml = yaml.load(file_name)
    return {'path': file_name, 'root': yml}


with open('mice_tissues_metadata.yml') as f:
    s = yaml.load(f)
    traverser = Traverser(*parsers)
    result = traverser.traverse(s)
    # (results, actions) = extract_actions(s)
    print(result)
    # print("final result = " + str(results))
    # print("final actions = " + str(actions))

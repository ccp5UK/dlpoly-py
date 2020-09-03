"""
CLI for configbuilder
"""


import argparse

_parser = argparse.ArgumentParser(description='Code to compile CONFIG/FIELD files', add_help=True)
_parser.add_argument('sources', nargs="+", help="List of sources to compile")
_parser.add_argument('-o', '--output', help="Filenames to create, default %(default)s", default="a")

def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    argList = _parser.parse_args()
    print(argList)
    if not argList.sources:
        _parser.print_help()
        exit()
    return argList

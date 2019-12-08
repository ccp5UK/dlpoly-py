"""
Set up command line input for DLPOLY parser
"""

import argparse

# SmartFormatter taken from StackOverflow
class SmartFormatter(argparse.HelpFormatter):
    """ Class to allow raw formatting only on certain lines """
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

# DictKeyPair taken from StackOverflow
class StoreDictKeyPair(argparse.Action):
    """ Class to convert a=b into dictionary key, value pair """
    def __call__(self, parser, namespace, values, optionString=None):
        newDict = {}
        for keyVal in values.split(","):
            key, value = keyVal.split("=")
            newDict[key] = value
        setattr(namespace, self.dest, newDict)

_PARSER = argparse.ArgumentParser(description='Parser for the DLPOLY file parser',
                                  add_help=True, formatter_class=SmartFormatter)
_PARSER.add_argument("-s", "--statis", help="Statis file to load", type=str)
_PARSER.add_argument("-c", "--control", help="Control file to load", type=str)
_PARSER.add_argument("-f", "--field", help="Field file to load", type=str)
_PARSER.add_argument("-C", "--config", help="Config file to load", type=str)

def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    return _PARSER.parse_args()

"""
Set up command line input for DLPOLY parser
"""

import argparse as arg
from typing import Optional


# SmartFormatter taken from StackOverflow
class SmartFormatter(arg.HelpFormatter):
    """ Class to allow raw formatting only on certain lines """

    def _split_lines(self, text: str, width: int):
        """ Do not format lines prefixed with R|

        :param text: Texto to parse
        :param width: Max width

        """
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return super()._split_lines(text, width)


# DictKeyPair taken from StackOverflow
class StoreDictKeyPair(arg.Action):
    """ Class to convert a=b into dictionary key, value pair """

    def __call__(self,
                 parser: arg.ArgumentParser,
                 namespace: arg.Namespace,
                 values: str,
                 optionString: Optional[str] = None):
        """ Take a=b and map to dict

        :param parser: Parse in
        :param namespace: Object to write to
        :param values: Vals to map
        :param optionString: Extra options

        """
        new_dict = dict((key_val.split('=') for key_val in values.split(',')))
        setattr(namespace, self.dest, new_dict)


_PARSER = arg.ArgumentParser(
    description="Parser for the DLPOLY file parser",
    add_help=True,
    formatter_class=SmartFormatter,
)
_PARSER.add_argument("-s", "--statis", help="Statis file to load", type=str)
_PARSER.add_argument("-c", "--control", help="Control file to load", type=str)
_PARSER.add_argument("-f", "--field", help="Field file to load", type=str)
_PARSER.add_argument("-C", "--config", help="Config file to load", type=str)
_PARSER.add_argument(
    "-w", "--workdir", help="Work directory in which to run", type=str, default="myRun"
)
_PARSER.add_argument(
    "-e", "--dlp", help="Name of DLP execuable to run", default="DLPOLY.Z"
)


def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    return _PARSER.parse_args()

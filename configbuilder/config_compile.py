"""
Code to compile configs and layouts into DLPoly inputs
Main interface
"""
from .builder import build
from .cli import get_command_args

def main():
    argList = get_command_args()
    for source in argList.sources:
        with open(source, 'r') as sourceFile:
            system = build(sourceFile)
        
if __name__ == "__main__":
    main()

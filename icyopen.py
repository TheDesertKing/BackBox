#!/usr/bin/python3
import sys
from subprocess import call
from importIC import import_signature
from translator import convert_icc_to_icy

ICY_PATH = "./icy/"

def validate_argv(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck search\npython3 importIC.py Signaure Search")
        sys.exit(61)


def main():
    validate_argv(sys.argv)

    file_path = ICY_PATH + sys.argv[1] + '.icy'

    call(['vim',file_path])


main()

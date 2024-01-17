#!/usr/bin/python3
import sys
from subprocess import call
from importIC import import_signature
from translator import convert_icc_to_icy


def validate_argv(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck search\npython3 importIC.py Signaure Search")
        sys.exit(61)


def main():
    validate_argv(sys.argv)

    signature_file_path = import_signature(sys.argv[1:])['sig_file_path']
    file_path = convert_icc_to_icy(signature_file_path)

    call(['vim',file_path])


main()

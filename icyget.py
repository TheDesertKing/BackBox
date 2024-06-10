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

    signature_file_path_list = import_signature(sys.argv[1:])['sig_file_path_list']

    icy_file_path_list = []
    for signature_file_path in signature_file_path_list:
        icy_file_path_list.append(convert_icc_to_icy(signature_file_path))


    if len(icy_file_path_list) == 1:
        call(['vim',icy_file_path_list[0]])


main()

#!/usr/bin/python3
from sys import argv,exit
from importIC import import_signature
from translator import convert_icc_to_icy


def validate_argv(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck search\npython3 importIC.py Signaure Search")
        exit(61)


def main():
    validate_argv(argv)
    signature_file_path = import_signature(argv[1:])['sig_file_path']
    convert_icc_to_icy(signature_file_path)



main()

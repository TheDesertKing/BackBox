#!/usr/bin/python3
import sys
import os
from compiler import compile_icy_to_icc
from uploader import upload_signature_to_server
import icylib


def parse_argv(argv):
    if len(argv) != 2:
        print(f"missing ICC file\n./icyset ICC_File_Path")
        sys.exit(61)

    return argv[1]


def main():
    icy_file_path = parse_argv(sys.argv)

    icc_file_path = compile_icy_to_icc(icy_file_path)
    upload_signature_to_server(icc_file_path)


main()

#!/usr/bin/python3
import sys



CTYPES_NOTATION = {"I":"internal", "R": "remote", "L": "local"}
DEFAULT_TIMEOUT = {"internal": 0, "remote": 60, "local": 30}
DEFAULT_WAITFOR = {
    "internal": "",
    "remote": '[{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]',
    "local": '[{"waitfor":"BBP","status":"success","message":""}]',
}
STATUS = {"S": "success", "F": "failure", "SUS": "suspect"}


def read_icy_file(argv):
    if len(argv) != 2:
        print("missing icy file name\n Usage:\n./compiler.py {signature_name}")

    filename = argv[1]
    with open(filename, 'rt') as icy_file:
        content = icy_file.read()

    return content


def get_command_blocks(argv):
    icy_file_content = read_icy_file(argv)

    return icy_file_content.split("\n\n")


def main():
    command_blocks = get_command_blocks(sys.argv)


main()

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
DEFAULT_COMMAND_DATA = {
        "timeout": 0,
        "sleep": 0,
        "status": None,
        "condition": [],
        "command": "missing command text",
        "queue": 1,
        "is_save": False,
        "is_status": False,
        "is_append": False,
        "file_perm": 664,
        "ctype": "internal",
        "hide_output": False,
        "desc": "",
        "waitfor": "",
        "save": "",
        "save_type": "",
        "error_msg": None
}


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


def parse_condition(command_line):
    single_arg_conditions = ["isempty","isnotempty","exists"]
    parsed_cond_data = []

    cond_part = command_line[6:].split(') ')[0]

    operator = 'AND' if cond_part.count(' AND ') > 0 else 'OR'
    operator_id = '1' if operator == 'AND' else '0'
    parts = cond_part.split(' '+operator+' ')
    for part in parts:
        data = {'operator':operator_id,'arg2':''}

        data['arg1'] = part.split(' ')[0]
        data['condition'] = part.split(' ')[1]

        if data['condition'] not in single_arg_conditions:
            # in case there is a space in arg2
            data['arg2'] = ' '.join(part.split(' ')[2:])

        parsed_cond_data.append(data)

    return parsed_cond_data






def parse_command_line(command_line):
    parsed_data = {}
    parsed_data['ctype'] = CTYPES_NOTATION[command_line[0]]
    if 'if (' in command_line[2:6]:
        parsed_data['condition'] = parse_condition(command_line)

    return parsed_data



def parse_block(block,queue):
    command_data = DEFAULT_COMMAND_DATA | {'queue': queue}

    for line in block.split('\n'):
        if line[0] in CTYPES_NOTATION.keys():
            command_data |= parse_command_line(line)
        elif line[0] == '#':
            pass
        elif line[0] == '&':
            pass
        elif line[0] == '*':
            pass

    #print(command_data)



def parse_command_blocks(command_blocks):
    commands_json_list = []
    queue = 0
    for block in command_blocks:
        queue += 1
        commands_json_list.append(parse_block(block,queue))





def main():
    command_blocks = get_command_blocks(sys.argv)
    commands_json_list = parse_command_blocks(command_blocks)


main()

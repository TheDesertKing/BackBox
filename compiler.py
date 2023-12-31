#!/usr/bin/python3
from sys import argv,exit
import json
from re import split



CTYPES_NOTATION = {"I":"internal", "R": "remote", "L": "local"}
DEFAULT_TIMEOUT = {"internal": 0, "remote": 60, "local": 30}
DEFAULT_WAITFOR = {
    "internal": "",
    "remote": '[{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]',
    "local": '[{"waitfor":"BBP","status":"success","message":""}]',
}
WAITFOR_STATUS = {
    'S:':'success',
    'F:':'failure',
    'SUSPCT:':'suspect'
}
DEFAULT_COMMAND_DATA = {
    "saveFlag": False,
    "statusFlag": False,
    "outputAppendToFile": False,
    "collected": False,
    "addToFileRepository": False,
    "saveToFilePermissions": 664,
    "id": "MISSING ID",
    "status": None,
    "queue": 1,
    "command_TYPE": "MISSING COMMAND_TYPE",
    "hide_OUTPUT": False,
    "description": "",
    "wait_FOR": "MISSING WAIT_FOR",
    "save_OUTPUT": "",
    "output_TYPE": "",
    "timeout": 0,
    "sleep": 0,
    "condition": [],
    "error_MESSAGE": None,
    "command": "MISSING COMMAND",
    "session_ID": "MISSING SESSION_ID"
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


def parse_condition(cond):
    if cond == False:
        return []

    single_arg_conditions = ["isempty","isnotempty","exists"]
    parsed_cond_data = []

    operator = 'AND' if cond.count(' AND ') > 0 else 'OR'
    operator_id = '1' if operator == 'AND' else '2'

    parts = cond.split(' '+operator+' ')
    for part in parts:
        data = {'operator':operator_id,'arg2':''}

        data['arg1'] = part.split(' ')[0]
        data['condition'] = part.split(' ')[1]

        if data['condition'] not in single_arg_conditions:
            # in case there is a space in arg2
            data['arg2'] = ' '.join(part.split(' ')[2:])

        parsed_cond_data.append(data)

    return parsed_cond_data


def get_command_line_parts(command_line):
    p = {}

    p['ctype'] = command_line[0]
    p['cond'] = command_line[6:].split(') ')[0] if 'if (' in command_line[2:6] else False

    if p['cond']:
        remaining_cmd_line = command_line[command_line.index(') ')+2:].split(' ')
    else:
        remaining_cmd_line = command_line[1:].split(' ')

    if 'hide' == remaining_cmd_line[-1]:
        p['hide'] = True
        remaining_cmd_line = remaining_cmd_line[:-1]
    else:
        p['hide'] = False

    if remaining_cmd_line[-1].startswith('slp'):
        p['slp'] = remaining_cmd_line[-1]
        remaining_cmd_line = remaining_cmd_line[:-1]
    else:
        p['slp'] = False

    if remaining_cmd_line[-1].startswith('tout'):
        p['tout'] = remaining_cmd_line[-1]
        remaining_cmd_line = remaining_cmd_line[:-1]
    else:
        p['tout'] = False

    if len(remaining_cmd_line) > 1 and remaining_cmd_line[-2].endswith('>'):
        p['saveto'] = ' '.join(remaining_cmd_line[-2:])
        remaining_cmd_line = remaining_cmd_line[:-2]
    else:
        p['saveto'] = False

    p['cmd'] = ' '.join(remaining_cmd_line)

    return p


def parse_saveto(saveto):
    saveto_data = {
        'statusFlag':False,
        'saveToFilePermissions':664,
        'outputAppendToFile':False,
        'addToFileRepository':False,
    }

    if saveto == False:
        return saveto_data

    first_part = saveto.split(' ')[0]
    second_part = saveto.split(' ')[1]

    saveto_data['statusFlag'] = True

    if '>>' in first_part:
        saveto_data['outputAppendToFile'] = True

    if first_part[0].isnumeric():
        try:
            saveto_data['saveToFilePermissions'] = int(first_part[:3])
        except:
            print('improper File Permissions (not numeric)')
            exit(51)

    if 'V' in first_part:
        saveto_data['output_TYPE'] = 'variable'
    else:
        saveto_data['output_TYPE'] = 'file'

    saveto_data['save_OUTPUT'] = second_part

    return saveto_data


def parse_timeout(tout,ctype):
    if tout == False:
        return DEFAULT_TIMEOUT[ctype]

    try:
        return int(tout[4:])
    except:
        print('improper Timeout (not numeric)')
        exit(52)


def parse_sleep(slp):
    if slp == False:
        return 0

    try:
        return int(slp[3:])
    except:
        print('improper Sleep (not numeric)')
        exit(53)



def parse_command_line(command_line):
    cmd_data = {}
    p = get_command_line_parts(command_line)

    cmd_data['ctype'] = CTYPES_NOTATION[p['ctype']]
    cmd_data['condition'] = parse_condition(p['cond'])
    cmd_data |= parse_saveto(p['saveto'])
    cmd_data['timeout'] = parse_timeout(p['tout'],cmd_data['ctype'])
    cmd_data['sleep'] = parse_sleep(p['slp'])
    cmd_data['hide_OUTPUT'] = p['hide']

    return cmd_data


def parse_desc(desc_line):
    return {'description': desc_line[2:]}


def parse_waitfor(line):
    parsed = split(r'(S:|SUSPCT:|F:)',line[2:])

    key_index = 1
    while key_index < len(parsed):
        new_statement = {
            "waitfor":parsed[key_index+1],
            "status":WAITFOR_STATUS[parsed[key_index]],
            "message":""
        }
    #Currently message is empty, will maybe implement it into translator then into here

    exit(123)
#['& ', 'S:', '(tmos) ', 'S:', '@']
#& S:(tmos) S:@

def parse_default_waitfor(ctype):
    pass


def parse_block(block,queue):
    command_data = DEFAULT_COMMAND_DATA | {'queue': queue}

    for line in block.split('\n'):
        if line[0] in CTYPES_NOTATION.keys():
            command_data |= parse_command_line(line)
        elif line[0] == '#':
            command_data |= parse_desc(line)
        elif line[0] == '&':
            command_data |= parse_waitfor(line)
        elif line[0] == '*':
            pass

    if command_data['wait_FOR'] == 'MISSING COMMAND_TYPE':
        parse_default_waitfor()

    return command_data


def parse_command_blocks(command_blocks):
    commands_json_list = []
    queue = 0
    for block in command_blocks:
        queue += 1
        commands_json_list.append(parse_block(block,queue))

    return commands_json_list




def main():
    command_blocks = get_command_blocks(argv)
    commands_json_list = parse_command_blocks(command_blocks)
    #print(json.dumps(commands_json_list))


main()

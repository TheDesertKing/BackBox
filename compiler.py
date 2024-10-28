#!/usr/bin/python3
from sys import argv,exit
import json
import re
import os
import icylib


CTYPES_NOTATION = {"I":"internal", "R": "remote", "L": "local"}
DEFAULT_TIMEOUT = {"internal": 0, "remote": 60, "local": 30}
DEFAULT_WAITFOR = {
    "internal": "",
    "remote": '[{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]',
    "local": '[{"waitfor":"BBP","status":"success","message":""}]',
}
STATUS = {
    'S':'success',
    'F':'failure',
    'SUS':'suspect'
}
DEFAULT_COMMAND_DATA = {
    "saveFlag": False,
    "statusFlag": False,
    "outputAppendToFile": False,
    "collected": False,
    "addToFileRepository": False,
    "saveToFilePermissions": 664,
    "id": 0,
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
    "session_ID": 0
}


def vailidate_argv(argv):
    if len(argv) != 2:
        print("missing icy file name\n Usage:\n./compiler.py signature_name")
        exit(54)


def read_icy_file(file_path):
    with open(file_path, 'rt') as icy_file:
        content = icy_file.read()

    return content


def remove_extra_newlines(icy_file_content):
    content_lines = re.sub(r'[\n]{2,}', '\n\n', icy_file_content)

    return content_lines


def get_command_blocks(file_path):
    icy_file_content = read_icy_file(file_path)

    return remove_extra_newlines(icy_file_content).split('\n\n')


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

        variable,condition = part.split(' ')[:2]
        data['arg1'] = variable
        if condition == '>':
            condition = 'greater'
        if condition == '<':
            condition = 'less'
        data['condition'] = condition

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
        remaining_cmd_line = command_line[command_line.index(') ')+2:].rstrip().split(' ')
    else:
        remaining_cmd_line = command_line[2:].rstrip().split(' ')

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

    if len(remaining_cmd_line) > 2 and remaining_cmd_line[-2] in ['\>','\>>']:
        # remove the backslash
        remaining_cmd_line[-2] = remaining_cmd_line[-2][1:]
        p['saveto'] = False
    elif len(remaining_cmd_line) > 1 and remaining_cmd_line[-2].endswith('>'):
        p['saveto'] = ' '.join(remaining_cmd_line[-2:])
        remaining_cmd_line = remaining_cmd_line[:-2]
    else:
        p['saveto'] = False

    p['cmd'] = ' '.join(remaining_cmd_line)

    return p


def parse_saveto(saveto):
    saveto_data = {
        'saveFlag':False,
        'saveToFilePermissions':664,
        'outputAppendToFile':False,
        'addToFileRepository':False,
    }

    if saveto == False:
        return saveto_data

    first_part = saveto.split(' ')[0]
    second_part = saveto.split(' ')[1]

    saveto_data['saveFlag'] = True

    if '>>' in first_part:
        saveto_data['outputAppendToFile'] = True

    if first_part[0].isnumeric():
        try:
            saveto_data['saveToFilePermissions'] = int(first_part[:3])
        except:
            print('improper File Permissions (not numeric)')
            exit(51)

    if 'V' in first_part[0]:
        saveto_data['output_TYPE'] = 'variable'
    elif 'performance' in first_part:
        saveto_data['output_TYPE'] = 'performance'
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

    cmd_data['command_TYPE'] = CTYPES_NOTATION[p['ctype']]
    cmd_data['condition'] = parse_condition(p['cond'])
    cmd_data |= parse_saveto(p['saveto'])
    cmd_data['timeout'] = parse_timeout(p['tout'],CTYPES_NOTATION[p['ctype']])
    cmd_data['sleep'] = parse_sleep(p['slp'])
    cmd_data['hide_OUTPUT'] = p['hide']
    cmd_data['command'] = p['cmd']

    return cmd_data


def parse_desc(desc_line):
    if desc_line[1] == ' ':
        return {'description': desc_line[2:]}
    return {'description': desc_line[1:]}


def parse_waitfor(line):
    #Currently message is empty, will maybe implement it into translator then into here
    success = re.findall(r"S:'(.*?)'",line[2:])
    suspect = re.findall(r"SUS:'(.*?)'",line[2:])
    failed = re.findall(r"F:'(.*?)'",line[2:])
    waitfor_data = {
        'success':success,
        'suspect':suspect,
        'failed':failed
        }

    statements = []
    for status, values in waitfor_data.items():
        for val in values:
            new_statement = {
                "waitfor":val,
                "status":status,
                "message":""
            }
            statements.append(new_statement)

    return {'wait_FOR': json.dumps(statements).replace('"','\"').replace(' ','')}


def parse_default_waitfor(ctype):
    return {'wait_FOR': DEFAULT_WAITFOR[ctype].replace('"','\"').replace(' ','')}


def parse_status(line):
    status_data = {'statusFlag':True}

    status_notation = line[2:].split(':')[0]
    status_message = ':'.join(line[2:].split(':')[1:])

    status_data['status'] = STATUS[status_notation]
    status_data['error_MESSAGE'] = status_message

    return status_data


def parse_block(block,queue):
    command_data = DEFAULT_COMMAND_DATA | {'queue': queue}

    for line in block.splitlines():
        if line[0] in CTYPES_NOTATION.keys():
            command_data |= parse_command_line(line)
        elif line[0] == '#':
            command_data |= parse_desc(line)
        elif line[0] == '&':
            command_data |= parse_waitfor(line)
        elif line[0] == '*':
            command_data |= parse_status(line)

    if command_data['wait_FOR'] == 'MISSING WAIT_FOR':
        command_data |= parse_default_waitfor(command_data['command_TYPE'])

    return command_data


def parse_command_blocks(command_blocks):
    commands_json_list = []
    queue = 0
    for block in command_blocks:
        queue += 1
        commands_json_list.append(parse_block(block,queue))

    return commands_json_list


def save_commands_json(filepath,commands_json_list):
    filename = os.path.basename(filepath)
    if filename.endswith('.icy') or filename.endswith('.icc'):
        filename = filename[:-4]

    icc_file_path = icylib.COMPILED_PATH + filename + '.icc'
    with open(icc_file_path, 'wt') as icc_file:
        #icc_file.write(commands_json_list)
        json.dump(commands_json_list,icc_file)

    print(f"compiled successfully: {icc_file_path}")

    return icc_file_path


def compile_icy_to_icc(file_path):
    command_blocks = get_command_blocks(file_path)

    commands_json_list = parse_command_blocks(command_blocks)
    #icylib.write_to_file('piled',json.dumps(commands_json_list,indent=2))
    #print(json.dumps(commands_json_list,indent=2))
    #exit(123)
    icc_file_path = save_commands_json(file_path,commands_json_list)

    return icc_file_path


def main():
    vailidate_argv(argv)

    compile_icy_to_icc(argv[1])



if __name__ == "__main__":
    main()

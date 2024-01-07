#!/usr/bin/python3
'''
TRANSLATOR.PY

This script will translate IntelliCheck commands files (icc) to icy files.

Usage:

./translator.py {signature_name}


'''


import json
import sys
import os

SAVE_PATH = "./icy/"

CTYPES_NOTATION = {"internal": "I", "remote": "R", "local": "L"}
DEFAULT_TIMEOUT = {"internal": 0, "remote": 60, "local": 30}
DEFAULT_WAITFOR = {
    "internal": "",
    "remote": '[{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]',
    "local": '[{"waitfor":"BBP","status":"success","message":""}]',
}
STATUS = {"success": "S", "failure": "F", "suspect": "SUS"}


def parse_commands_file(argv):
    if len(argv) != 2:
        print("missing icc file name\n Usage:\n./translator.py {signature_name}")
        exit(1)

    with open(argv[1], "r") as cfile:
        commands_data = cfile.read()
    commands_json_list = json.loads(commands_data)
    return commands_json_list


def get_command_props(c):
    duplicate_keys = ["timeout", "sleep", "status", "command", "queue"]
    props = {key: c[key] for key in duplicate_keys}
    props["is_save"] = c["saveFlag"]
    props["is_status"] = c["statusFlag"]
    props["is_append"] = c["outputAppendToFile"]
    props["file_perm"] = c["saveToFilePermissions"]
    props["ctype"] = c["command_TYPE"]
    props["hide_output"] = c["hide_OUTPUT"]
    props["desc"] = c["description"]
    props["waitfor"] = c["wait_FOR"]
    props["save"] = c["save_OUTPUT"]
    props["save_type"] = c["output_TYPE"]
    props["conditions"] = c["condition"]
    props["status_text"] = c["error_MESSAGE"]

    return props


def type_notation(p, ctype):
    try:
        p.append(CTYPES_NOTATION[ctype])
    except:
        raise Exception("type_notation: Command type not recognized")


def condition_notation(p, conditions):
    if not conditions:
        return
    operators = {"1": "AND", "2": "OR"}

    # these conditions do not need arg2
    single_arg_conditions = ["isempty","isnotempty","exists"]
    operator = operators[conditions[0]["operator"]]

    statement = []
    for c in conditions:
        if c["condition"] not in single_arg_conditions:
            part = c["arg1"] + " " + c["condition"] + " " + c["arg2"]
        else:
            part = c["arg1"] + " " + c["condition"]
        statement.append(part)
    p.append("if (" + (" "+operator+" ").join(statement) + ")")


def save_notation(p, is_save, save_type, is_append, save_to, file_perm):
    if not is_save:
        return
    elif save_type == "variable":
        save_part = "V>" + " " + save_to
    elif save_type == "file" and not is_append:
        save_part = ">" + " " + save_to
    elif save_type == "file" and is_append:
        save_part = ">>" + " " + save_to
    else:
        raise Exception("save_notation: Can't identify save_type")

    if file_perm != 664:
        p.append(str(file_perm) + save_part)
    else:
        p.append(save_part)


def timout_notation(p, timeout, ctype):
    if timeout == DEFAULT_TIMEOUT[ctype]:
        return
    else:
        p.append("tout" + str(timeout))


def sleep_notation(p, sleep):
    if sleep == 0:
        return
    else:
        p.append("slp" + str(sleep))


def hide_notation(p, hide):
    if hide == False:
        return
    else:
        p.append("hide")


def description_notation(p, desc):
    if desc == "":
        return
    else:
        p.append("\n# " + desc)


def waitfor_notation(p, waitfor, ctype):
    if waitfor == DEFAULT_WAITFOR[ctype]:
        return
    else:
        waitfor_data = json.loads(waitfor)
        options = []
        for option_data in waitfor_data:
            if "regex" in option_data.keys() and option_data["regex"]:
                options.append(
                    STATUS[option_data["status"]]
                    + ":"
                    + "R'"
                    + option_data["waitfor"]
                    + "'"
                )
            else:
                options.append(
                     STATUS[option_data["status"]] + ":" + option_data["waitfor"]
                )
        p.append("\n& " + " ".join(options))


def status_notation(p, status, text):
    if status == None:
        return
    p.append("\n* " + STATUS[status] + ":" + text)


def construct_commad_block(props):
    parts = []
    type_notation(parts, props["ctype"])
    condition_notation(parts, props["conditions"])
    parts.append(props["command"])
    save_notation(
        parts, props["is_save"], props["save_type"], props["is_append"], props["save"], props["file_perm"]
    )
    timout_notation(parts, props["timeout"], props["ctype"])
    sleep_notation(parts, props["sleep"])
    hide_notation(parts, props["hide_output"])
    description_notation(parts, props["desc"])
    waitfor_notation(parts, props["waitfor"], props["ctype"])
    status_notation(parts, props["status"], props["status_text"])
    return " ".join(parts)


def write_ic_file(blocks):
    content = "\n\n".join(blocks)
    #remove '.icc' ending
    filename = sys.argv[1][:-4] if sys.argv[1].endswith('.icc') else sys.argv[1]

    with open(SAVE_PATH + os.path.basename(filename) + '.icy', 'wt') as ic_file:
        ic_file.write(content)


def main():
    command_list = parse_commands_file(sys.argv)
    blocks = []
    for command in command_list:
        props = get_command_props(command)
        blocks.append(construct_commad_block(props))

    write_ic_file(blocks)


if __name__ == "__main__":
    main()

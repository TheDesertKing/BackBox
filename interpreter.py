import json
import sys

CTYPES_NOTATION = {"internal": "I", "remote": "R", "local": "L"}
DEFAULT_TIMEOUT = {"internal": 0, "remote": 60, "local": 30}
DEFAULT_WAITFOR = {
    "internal": "",
    "remote": '[{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]',
    "local": '[{"waitfor":"BBP","status":"success","message":""}]',
}
STATUS = {"success": "S", "failure": "F", "suspect": "SUS"}


def parse_commands_file(filename):
    with open(filename, "r") as cfile:
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
    operators = {"1": "and", "2": "or"}
    operator = operators[conditions[0]["operator"]]
    statement = []
    for c in conditions:
        if c["arg2"]:
            part = c["arg1"] + " " + c["condition"] + " " + c["arg2"]
        else:
            part = c["arg1"] + " " + c["condition"]
        statement.append(part)
    p.append("if (" + operator.join(statement) + ")")


def save_notation(p, is_save, save_type, is_append, save_to):
    if not is_save:
        return
    elif save_type == "variable":
        p.append("V>" + " " + save_to)
    elif save_type == "file" and not is_append:
        p.append(">" + " " + save_to)
    elif save_type == "file" and is_append:
        p.append(">>" + " " + save_to)
    else:
        raise Exception("save_notation: Can't identify save_type")


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
                    "R'"
                    + option_data["waitfor"]
                    + "'"
                    + ":"
                    + STATUS[option_data["status"]]
                )
            else:
                options.append(
                    option_data["waitfor"] + ":" + STATUS[option_data["status"]]
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
        parts, props["is_save"], props["save_type"], props["is_append"], props["save"]
    )
    timout_notation(parts, props["timeout"], props["ctype"])
    sleep_notation(parts, props["sleep"])
    hide_notation(parts, props["hide_output"])
    description_notation(parts, props["desc"])
    waitfor_notation(parts, props["waitfor"], props["ctype"])
    status_notation(parts, props["status"], props["status_text"])
    return " ".join(parts)


def main():
    command_list = parse_commands_file(sys.argv[1])
    for command in command_list:
        props = get_command_props(command)
        block = construct_commad_block(props)
        print(block)


if __name__ == "__main__":
    main()

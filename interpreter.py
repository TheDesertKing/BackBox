import json

def parse_commands_file(filename):
    with open(filename,'r') as cfile:
        commands_data = cfile.read()
    commands_json_list = json.loads(commands_data)
    return commands_json_list

def get_command_props(c):
    duplicate_keys = ['timeout','sleep','status','condition','command','queue']
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
    props["error_msg"] = c["error_MESSAGE"]

    return props


def construct_line(props):
    if props["ctype"] == internal


def main():
    command_list = parse_commands_file('yasers')
    for command in command_list:
        props = get_command_props(command)
        line = construct_line(props)
    pass


if __name__=="__main__":
    main()

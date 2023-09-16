import json

def parse_commands_file(filename):
    with open(filename,'r') as cfile:
        commands_data = cfile.read()
    commands_json_list = json.loads(commands_data)
    print(commands_json_list)

def get_command_props(c):
    props = {}
    props.is_save = c.saveFlag
    props.is_status = c.statusFlag
    props.is_append = c.outputAppendToFile
    props.file_perm = c.saveToFilePermissions
    props.ctype = c.command_TYPE
    props.hide_output = c.hide_OUTPUT
    props.desc = c.description
    props.waitfor = c.wait_FOR
    return props


def main():
    
    pass


if __name__=="__main__":
    main()

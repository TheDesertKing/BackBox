import csv

# Local default wait for
LWF = 'TBD'
# Remote default wait for
RWF = [{"waitfor":"#","status":"success","message":""}, {"waitfor":"%%CURRENT_PROMPT%%","status":"success","message":""}]
# Command type identifier
#COMMAND_TYPE = {}


with open('commands.csv', newline='') as f:
    data = list(csv.reader(f))[2:]
    for c in data:
        if c[0] == "Dynamic field":
            print("D",c[2],c[3],c[6])
        else:
            if c[5] == "remote":
                print(c[3],"R",c[2],c[7],c[8])

# Helper fucntions

    


def parse_command(command_data):
    ctype = command_data[5]


    return command_line


def parse_dynamic_field(dynamic_field_data):
    pass

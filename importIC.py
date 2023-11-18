from sys import argv,exit
import requests

MACHINE_ADDRESS="172.31.252.213"
USERNAME="admin"
PASSWORD="1"
MACHINE_URL=f"https://{MACHINE_ADDRESS}/"

from urllib3.exceptions import InsecureRequestWarning

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_signature_name(argv):
    if len(argv) < 2:
        print("missing IntelliCheck signature name\npython3 importIC.py {SignaureName}")
        exit(-1)

    return argv[1]

 
def backbox_login(verbose):
    sess = requests.Session()
    try:
        sess.get(MACHINE_URL,verify=False)
    except:
        print("can't connect to backbox machine")
        exit(-2)

    login_response = sess.post(MACHINE_URL+f"j_security_check",data=f"j_username={USERNAME}&j_password={PASSWORD}",headers={"Content-Type":"application/x-www-form-urlencoded; charset=utf-8"},verify=False)
    if "network" not in login_response.text:
		# If network isn't in the response, the login failed and we weren't redirected to the app
        print("wrong credentials")
        exit(-3)

    if verbose: print(sess.cookies.get_dict())

    return sess


def get_matching_signatures(signature_name,all_signatures):

    matching_signatures = [sig for sig in all_signatures.json() if signature_name in sig["name"]]

    return matching_signatures


def get_signature_data(matching_signatures):
    if len(matching_signatures) == 0:
        print("no signature matching the name provided was found")
        exit(-4)

    elif len(matching_signatures) == 1:
        return matching_signatures[0]

    else:
        signature_names = [sig["name"] for sig in matching_signatures]
        index = 1
        for name in signature_names:
            print(f"[{index}] {name}")
            index += 1

        print(f"please pick signature using it's index (1-{index-1})")

        while True:
            picked_index = input()

            try:
                picked_index = int(picked_index)

            except Exception as e: 
                print("index picked is not a number, try again")
                continue

            if picked_index < 1 or picked_index > index-1:
                print("index picked is out of range, try again")

            else:
                return matching_signatures[picked_index-1]

                
def get_signature_commands(session_id,sess):
    # due to what seems to be a bug, the sessionCommands always seem to be empty
    # so in order to get them we will use another API call using the sessionId we fetched
    return sess.get(MACHINE_URL + f"rest/data/integrator/session/commands/{session_id}",headers={"Accept":"application/json"}).text


def write_to_file(signature_name,commands):
    # remove characters that might cause issues in file names
    signature_name = signature_name.replace(">","")
    signature_name = signature_name.replace(":","")
    with open(signature_name,'wt') as file:
        file.write(commands)


def main(verbose=False):
    signature_name = get_signature_name(argv)
    sess = backbox_login(verbose)

    all_signatures = sess.get(MACHINE_URL+"rest/data/intelliChecks/signatures/0/true",headers={"Accept":"application/json"})
    matching_signatures = get_matching_signatures(signature_name,all_signatures)
    signature_data = get_signature_data(matching_signatures)
    signature_commands = get_signature_commands(signature_data['sessionId'],sess)
    print(signature_commands)
    write_to_file(signature_data["name"],signature_commands)


if __name__ == "__main__":
    main(verbose=True)
else:
    main()


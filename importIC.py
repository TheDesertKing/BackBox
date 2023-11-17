from sys import argv,exit
import requests

MACHINE_ADDRESS="172.31.254.118"
USERNAME="admin"
PASSWORD="1"

from urllib3.exceptions import InsecureRequestWarning

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_signature_name(argv):
    if len(argv) < 2:
        print("missing IntelliCheck signature name")
        exit()
    return argv[1]


def main(verbose=False):
    signature_name = get_signature_name(argv)
    sess = requests.Session()
    print(sess.get(f"https://{MACHINE_ADDRESS}",verify=False).text)
    login_response = sess.post(f"https://{MACHINE_ADDRESS}/j_security_check",data=f"j_username={USERNAME}&j_password={PASSWORD}",headers={"Content-Type":"application/x-www-form-urlencoded; charset=utf-8"},verify=False)
    print(login_response.text)
    if "network" not in login_response.text:
        print("wrong credentials")
        exit()
    print(sess.cookies.get_dict())








if __name__ == "__main__":
    main(verbose=True)


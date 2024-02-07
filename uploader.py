#!/usr/bin/python3
"""
new signature:
    default:
    "id": 0,
    "description": "",
    "predefined": false,
    "signatureType": "Operations",
    "sessionId": 0,
    "remediationSessionId": 0,
    "siteId": 0,
    "siteName": null,
    "tags": [],
    "document": null,
    "remediationCommands": [],
    "restricted": false,
    "optionsForSignature": []

    to fill:
        name: str,signature name
    to fill after creating:
        id
        sessionId
"""
import sys
import icylib
import os
import json
import requests
from rich import print
# Overriding default print with colored one
from urllib3.exceptions import InsecureRequestWarning
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

MAP_FILE_PATH = "./signature_data.map"
SERVER_CONF_PATH="./conf/88.json"

DEFAULT_SIGNATURE_DATA = {
    "id": 0,
    "description": "",
    "predefined": False,
    "signatureType": "Operations",
    "sessionId": 0,
    "remediationSessionId": 0,
    "siteId": 0,
    "siteName": None,
    "tags": [],
    "document": None,
    "remediationCommands": [],
    "restricted": False,
    "optionsForSignature": []
}


def get_signature_map_data(icc_file_name,machine_ip):
    with open(MAP_FILE_PATH, 'r') as map_file:
        map_file_lines = map_file.readlines()

    for line in map_file_lines:
        line = line.rstrip()
        signature_name,iter_icc_file_name,iter_machine_ip,sessionId,signature_id = line.split(' | ')
        if icc_file_name == iter_icc_file_name and machine_ip == iter_machine_ip:
            return {'name':signature_name,'sessionId':sessionId,'id':signature_id}

    return {'name':'','sessionId':0,'id':0}


def parse_signature_name(icc_file_path):
    filename = os.path.basename(icc_file_path)
    if filename[-4:] == '.icc':
        return filename[:-4]
    return filename


def get_signature_commands(icc_file_path):
    with open(icc_file_path, 'r') as icc_file:
        return json.load(icc_file)


def validate_argv(argv):
    if len(argv) != 2:
        print("missing icc file path\n Usage:\n./uploader.py {file_name.icc}")
        exit(1)


def get_product_options(signature_id,sess,machine_url):
    headers = {'Accept':'application/json','Content-Type':'application/json'}
    product_options_data = sess.post(machine_url + 'rest/data/intelliChecks/signatures/options/in',data=f'[{signature_id}]',headers=headers)

    return [p['optionId'] for p in product_options_data.json()]


def get_signature_data(icc_file_path,icc_file_name,sess,conf):
    map_data = get_signature_map_data(icc_file_name,conf.machine_ip)
    signature_commands = get_signature_commands(icc_file_path)
    product_options = get_product_options(map_data['id'],sess,conf.machine_url)

    signature_data = DEFAULT_SIGNATURE_DATA | map_data | {'sessionCommands':signature_commands} | {'optionsForSignature' : product_options}
    return signature_data


def add_data_to_map_file(signature_name,icc_file_name,machine_ip,sessionId,signature_id):
    with open(MAP_FILE_PATH, 'a') as map_file:
        new_data_mapping = signature_name + ' | ' + icc_file_name + ' | ' + machine_ip + ' | ' + str(sessionId) + ' | '+ str(signature_id) + '\n'
        map_file.write(new_data_mapping)


def create_signature(signature_data,sess,conf,headers):
        response = sess.post(conf.machine_url+"rest/data/intelliChecks/signatures/false",json=signature_data,headers=headers)

        if response.status_code == 500:
            print(f"error while creating signature {signature_data['name']} on {conf.machine_ip}:")
            print(response.text)
            exit(2)

        resp_json = response.json()
        add_data_to_map_file(signature_data['name'],signature_data['name'],conf.machine_ip,resp_json['sessionId'],resp_json['id'])


def find_signature_by_ids(all_signatures_json,signature_data):
    for sig in all_signatures_json:
        if str(sig['id']) == signature_data['id'] and str(sig['sessionId']) == signature_data['sessionId']:
            return sig

    return ''


def update_signature(signature_data,sess,conf,headers):
    all_signatures_json = sess.get(conf.machine_url+"rest/data/intelliChecks/signatures/0/true",headers={"Accept":"application/json"}).json()

    existing_sig_data = find_signature_by_ids(all_signatures_json,signature_data)

    if existing_sig_data == '':
        print(f"signature {signature_data['name']} existed once on {conf.machine_ip} but no longer does")
        exit(3)

    complete_sig_data = existing_sig_data | signature_data
    response = sess.put(conf.machine_url+"rest/data/intelliChecks/signatures/false",json=complete_sig_data,headers=headers)

    if response.text != 'true':
        print(f"failed to update signature {signature_data['name']} on {conf.machine_ip}")
        exit(4)


def upload_signature_data(signature_data,icc_file_name,sess,conf):

    headers={"Accept":"application/json","Content-Type":"application/json;charset=UTF-8"}

    if signature_data['name'] == "":
        signature_data |= {'name':icc_file_name}
        create_signature(signature_data,sess,conf,headers)

    else:
        update_signature(signature_data,sess,conf,headers)


def upload_signature_to_server(icc_file_path):

    conf = icylib.read_conf_file(SERVER_CONF_PATH)
    sess = icylib.backbox_login(conf)

    icc_file_name = parse_signature_name(icc_file_path)
    print(f"Uploading:\t{icc_file_name}\nTo:\t{conf.machine_ip}")

    signature_data = get_signature_data(icc_file_path,icc_file_name,sess,conf)
    #print(json.dumps(signature_data,indent=1))

    upload_signature_data(signature_data,icc_file_name,sess,conf)

    print("\nUpload successful")


def main():

    validate_argv(sys.argv)

    icc_file_path = sys.argv[1]

    upload_signature_to_server(icc_file_path)


if __name__ == "__main__":
    main()

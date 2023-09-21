#!/bin/bash
BACKBOX_IP=172.31.254.118
USERNAME=admin
PASSWORD=1
SESSION_ID=$1

curl -X GET -k -c cookies https://${BACKBOX_IP}/ -L
curl -X POST -k -b cookies -c cookies -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' -d "j_username=${USERNAME}&j_password=${PASSWORD}" 'https://172.31.254.118/j_security_check' -L
curl -X GET -k -b cookies -c cookies -H 'Accept: application/json' "https://172.31.254.118/rest/data/integrator/session/commands/${SESSION_ID}" -L > session_${SESSION_ID}
rm ./cookies

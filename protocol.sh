#!/bin/bash
BACKBOX_IP=calsoft.cloud.backbox.com
USERNAME=admin
PASSWORD=1q2w3e4r
SESSION_ID=$1

curl -X GET -k -c cookies https://${BACKBOX_IP}/ -L
curl -X POST -k -b cookies -c cookies -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' -d "j_username=${USERNAME}&j_password=${PASSWORD}" "https://${BACKBOX_IP}/j_security_check" -L
curl -X GET -k -b cookies -c cookies -H 'Accept: application/json' "https://${BACKBOX_IP}/rest/data/integrator/session/commands/${SESSION_ID}" -L > session_${SESSION_ID}
rm ./cookies

import requests

# Disable no SSL warning
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

BBIP = 'https://'+'172.31.254.118'

def main():
    s = requests.Session()

    #Open login page
    s.get(BBIP, verify=False)

    #Send authentication
    login = {'j_username':'admin','j_password':'1'}
    s.post(BBIP+'/j_security_check',data=login, verify=False)

    #Sanity check
    print('sanity',s.get(BBIP+'/rest/data/integrator/echo', verify=False).text)

    #Get commands for signature 886
    accept_header = {'Accept':'application/json'}
    response = s.get(BBIP+'/rest/data/integrator/session/commands/886',headers=accept_header, verify=False)
    print(response.text)
    print(response)






if __name__ == "__main__":
    main()

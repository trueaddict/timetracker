import requests
import sys, getopt
import pprint

class Harvest:
    user_token = ''
    account_id = ''

    user_details = {}
    user_project_assignments = {}

    def __init__(self, user_token, account_id):
        self.user_token = user_token
        self.account_id = account_id
        self.user_details = self.getResource('users/me')
        self.user_project_assignments = self.getResource('users/me/project_assignments')
        #pprint.pprint(self.user_project_assignments['project_assignments'][-1])

    def getClients(self):
        list_clients = set()
        for project in self.user_project_assignments['project_assignments']:
            client_name = project['client']['name'].lower().replace(' ', '_')
            list_clients.add(f'{client_name} ')
        return list(list_clients)
    
    def getTasks(self):
        list_tasks = set()
        for project in self.user_project_assignments['project_assignments']:
            for task in project['task_assignments']:
                task_name = task['task']['name'].lower().replace(' ', '_')
                list_tasks.add(f'{task_name}')
        return list(list_tasks)



    def getResource(self, resource, params={}):
        try:
            headers = {
                'Harvest-Account-ID': self.account_id,
                'Authorization': 'Bearer '+self.user_token,
                'User-Agent': 'Timetracker API'
            }
            r = requests.get(f'https://api.harvestapp.com/api/v2/{resource}', headers=headers, params=params)
            if r.status_code != 200:
                print(r.text)
                return
            return r.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

def main(argv):
    user_token = ''
    account_id = ''

    try:
        opts, args = getopt.getopt(argv,"t:i:",["token=","account_id="])
    except getopt.GetoptError:
        print('harvest.py -t <token> -id <account_id>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-t', '--token'):
            user_token = arg
        if opt in ('-i', '--account_id'):
            account_id = arg 
    
    harvest = Harvest(user_token, account_id)

if __name__ == '__main__':
    main(sys.argv[1:])
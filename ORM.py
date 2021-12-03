import requests
import boto3
import datetime

class ORM():
    def __init__(self) -> None:
        self.northv = 'us-east-1'
        self.session = boto3.session.Session(region_name=self.northv)
        self.clientLB = self.session.client('elbv2', region_name=self.northv)
        self.LB_name = ''
    def client(self):
        self.LB_DNSname = self.clientLB.describe_load_balancers(Names=[self.LB_name,])['LoadBalancers'][0]['DNSName']
        URL = 'http://{}/tasks'.format(self.LB_DNSname)
        print(URL)
        while 1:
            try:
                print('''
                Create Task     [0]
                Get All Tasks   [1]
                Delete Tasks    [2]
                Sair            [3]
                    ''')
                selector = int(input("\nSelect a function ->"))

                if selector == 0:
                    task = {
                        "title": str(input("Task Title: ")),
                        "pub_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "description": str(input("Task Description: "))
                    }
                    response = requests.post(URL + "/create", json=task)
                    print("\nResponse:", response.text)

                elif selector == 1:
                    response = requests.get(URL + "/get_all")
                    print("\nResponse:", response.text)

                elif selector == 2:
                    response = requests.delete(URL + "/delete_all")
                    print("\nResponse:", response.text)
                else:
                    break
            except Exception as e:
                print(e)
                break
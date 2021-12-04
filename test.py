import requests
import boto3
import datetime

class ORM():
    def __init__(self) -> None:
        self.northv = 'us-east-1'
        self.session = boto3.session.Session(region_name=self.northv)
        self.clientLB = self.session.client('elbv2', region_name=self.northv)
        self.LB_name = 'northv-LB'
    def client(self):
        self.LB_DNSname = self.clientLB.describe_load_balancers(Names=[self.LB_name,])['LoadBalancers'][0]['DNSName']
        URL = 'http://{}/tasks'.format(self.LB_DNSname)
        print(URL)
        while 1:
            try:
                print('\n\tGet All Tasks   [0]\n\tCreate Task     [1]\n\tDelete Tasks    [2]\n\tSair            [3]')
                
                selector = int(input("\nSelect a function ->"))

                if selector == 0:
                    response = requests.get(URL + "/get_tasks")
                    print("\nResponse:", response.text)

                elif selector == 1:
                    task = {
                        "title": str(input("Task Title: ")),
                        "pub_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "description": str(input("Task Description: "))
                    }
                    response = requests.post(URL + "/create_tasks", json=task)
                    print("\nResponse:", response.text)

                elif selector == 2:
                    response = requests.delete(URL + "/delete_tasks")
                    print("\nResponse:", response.text)
                else:
                    break
            except Exception as e:
                print(e)
                break

orm = ORM()
orm.client()
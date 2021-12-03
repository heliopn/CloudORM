import boto3
import time

class OhayoGozaimasu():
    def __init__(self) -> None:
        self.Ohayo = 'us-east-2'
        self.DB_init =  '''#!/bin/bash
        cd /home/ubuntu
        sudo apt update -y
        sudo apt install postgresql postgresql-contrib -y
        sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
        sudo -u postgres psql -c "CREATE DATABASE tasks;"
        sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf      
        sudo sed -i "a\host all all 0.0.0.0/0 trust" /etc/postgresql/10/main/pg_hba.conf
        sudo ufw allow 5432/tcp
        sudo systemctl restart postgresql'''
        self.SG_name =  "ohayo-SG"
        self.SG_ID = ""
        self.publicIP = ""
        self.InstanceID = ''
        self.ImageID =  "ami-020db2c14939a8efb"
        self.session = boto3.session.Session(region_name=self.Ohayo)
        self.client = self.session.client('ec2', region_name=self.Ohayo)
        self.ec2_resource = self.session.resource('ec2')

    def delete_instance(self):
        try:
            instancesIDs = []
            instances = self.client.describe_instances()
            for i in instances['Reservations']:
                for j in i['Instances']:
                    if j['ImageId'] == self.ImageID:
                        instancesIDs.append(j['InstanceId'])
            if instancesIDs!=[]:
                waiter = self.client.get_waiter('instance_terminated')
                self.client.terminate_instances(InstanceIds=instancesIDs)
                waiter.wait(InstanceIds=instancesIDs)
            print("\n------ Instances DELETED ------".format(self.ImageID))
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_SG(self):
        try:
            response = self.client.delete_security_group(GroupName=self.SG_name)
            time.sleep(15)
            print("\n------ SecurityGroup DELETED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_SG(self):

        response = self.client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        try:
            SG = self.client.create_security_group(
                Description='Ohayo SG',
                GroupName='ohayo-SG',
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'Ohayo DB'
                            },
                        ]
                    },
                ]
            )
            self.SG_ID = SG['GroupId']

            response5432 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName='ohayo-SG',
                FromPort=5432,
                ToPort=5432,
                IpProtocol='tcp'
            )
            response22 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName='ohayo-SG',
                FromPort=22,
                ToPort=22,
                IpProtocol='tcp'
            )
            print("\n------ Ohayo Postgres Security Group CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_instance(self):
        try:
            response = self.ec2_resource.create_instances(
                ImageId= self.ImageID,
                MinCount=1,
                MaxCount=1,
                InstanceType="t2.micro",
                KeyName="helio-key",
                SecurityGroups=[
                    self.SG_name,
                ],
                UserData=self.DB_init
            )
            response[0].wait_until_running()
            response[0].reload()
            self.InstanceID = str(response[0].instance_id)
            self.publicIP = str(response[0].public_ip_address)
            print("\n------ Ohayo Postgres Instance CREATED ------")
            print("\n------ Public IP Ohayo {} ------".format(self.publicIP))
            return 1
        except Exception as e:
            print('Error[CR01] - Ohayo Creation failed')
            print(e)
            return 0

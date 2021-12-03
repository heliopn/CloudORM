from typing import Protocol
import boto3
import time

class NorthV():
    def __init__(self) -> None:
        self.northv = 'us-east-1'
        self.ORM_init =  '''#!/bin/bash
        cd /home/ubuntu
        sudo apt update -y
        git clone https://github.com/heliopn/tasks.git
        sudo sed -i "s/node1/OhayoIP/g" /home/ubuntu/tasks/portfolio/settings.py
        cd tasks
        ./install.sh
        sudo reboot'''
        self.SG_name =  "northv-SG"
        self.LBSG_name = 'northv-LBSG'
        self.LB_name = 'northv-LB'
        self.TG_name = "TG-ORM"
        self.LC_name = 'northv-LC'
        self.AS_name = 'northv-AS'
        self.LBArn = ''
        self.SG_ID = ""
        self.LBSG_ID = ''
        self.OhayoIP = ''
        self.publicIP = ''
        self.InstanceID = ''
        self.AMI_name = 'ORM_img'
        self.ImageID =  "ami-0279c3b3186e54acd"
        self.newImageID = ''
        self.session = boto3.session.Session(region_name=self.northv)
        self.client = self.session.client('ec2', region_name=self.northv)
        self.clientLB = self.session.client('elbv2', region_name=self.northv)
        self.clientAS = self.session.client('autoscaling', region_name=self.northv)
        self.ec2_resource = self.session.resource('ec2')

    def delete_AMI(self):
        try:
            images = self.client.describe_images(Owners=['self'])
            for i in images['Images']:
                if i != None and i['Name'] == self.AMI_name:
                    self.client.deregister_image(ImageId=i["ImageId"])
            time.sleep(15)
            print("\n------ Image named {} DELETED ------".format(self.AMI_name))
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_instance(self):
        try:
            list_term_inst = []
            instances = self.client.describe_instances()
            for i in instances['Reservations']:
                for j in i['Instances']:
                    if j['ImageId'] == self.ImageID:
                        list_term_inst.append(j['InstanceId'])
            if list_term_inst!=[]:
                waiter = self.client.get_waiter('instance_terminated')
                self.client.terminate_instances(InstanceIds=list_term_inst)
                waiter.wait(InstanceIds=list_term_inst)
            time.sleep(60)
            print("\n------ Instances with ImageID {} DELETED ------".format(self.ImageID))
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
    
    def delete_TG(self):
        try:
            TGs = self.clientLB.describe_target_groups(Names=[self.TG_name])
            response = self.clientLB.delete_target_group(
                TargetGroupArn=TGs['TargetGroups'][0]['TargetGroupArn']
                )
            time.sleep(15)
            print("\n------ Target Group named {} DELETED ------".format(self.TG_name))
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_LBSG(self):
        try:
            response = self.client.delete_security_group(GroupName=self.LBSG_name)
            time.sleep(15)
            print("\n------ Load Balance SecurityGroup DELETED ------")
            return 1
        except Exception as e:
            print(e)
            return 0
    
    def delete_LB(self):
        try:
            
            # LBs = self.clientLB.describe_load_balancers(
            #             Names=[
            #                 self.LB_name,
            #             ]
            #         )
            # for i in LBs['LoadBalancers']:
            #     if i != None and i['LoadBalancerName'] == self.LB_name:
            self.clientLB.delete_load_balancer(LoadBalancerArn=self.LBArn)
            time.sleep(60)
            print("\n------ Load Balancer named {} DELETED ------".format(self.AMI_name))
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_LC(self):
        try:
            response = self.clientAS.delete_launch_configuration(
                LaunchConfigurationName=self.LC_name
            )
            time.sleep(15)
            print("\n------ Launch Configuration DELETED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_AS(self):
        try:
            response = self.clientAS.delete_auto_scaling_group(
                AutoScalingGroupName= self.AS_name,
                ForceDelete= True
            )
            time.sleep(15)
            print("\n------ ORM Auto Scaling DELETED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete_LS(self):
        try:
            LBs = self.clientLB.describe_load_balancers(
                Names=[
                    self.LB_name,
                ]
            )
            self.LBArn = LBs['LoadBalancers'][0]['LoadBalancerArn']
            response = self.clientLB.describe_listeners(
                LoadBalancerArn=self.LBArn,
            )
            response2 = self.clientLB.delete_listener(
                ListenerArn=response['Listeners'][0]['ListenerArn']
            )
            time.sleep(15)
            print("\n------ ORM Listener DELETED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_LS(self):
        try:
            response = self.clientLB.create_listener(
                LoadBalancerArn=self.LBArn,
                Protocol='HTTP',
                Port=80,
                DefaultActions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': self.TGArn
                    },
                ]
            )
            time.sleep(15)
            print("\n------ ORM Listener CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0
    
    def create_AS(self):
        try:
            Zones = []
            response = self.client.describe_availability_zones()
            for i in response['AvailabilityZones']:
                Zones.append(i['ZoneName'])
            response = self.clientAS.create_auto_scaling_group(
                AutoScalingGroupName=self.AS_name,
                LaunchConfigurationName=self.LC_name,
                MinSize=1,
                MaxSize=3,
                AvailabilityZones=Zones,
                TargetGroupARNs=[
                    self.TGArn,
                ]
            )
            response = self.clientAS.attach_load_balancer_target_groups(
                AutoScalingGroupName=self.AS_name,
                TargetGroupARNs=[
                    self.TGArn,
                ]
            )
            print("\n------ ORM Auto Scaling CREATED AND ATTACHED Load Balancer ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_LC(self):
        try:
            response = self.clientAS.create_launch_configuration(
                LaunchConfigurationName=self.LC_name,
                ImageId=self.ImageID,
                KeyName='helio-key',
                SecurityGroups=[
                    self.SG_ID,
                ],
                InstanceType='t2.micro'
            )
            print("\n------ ORM Launch Configuration CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_LB(self):
        try:
            response = self.client.describe_subnets()
            subnets = []
            for subnet in response["Subnets"]:
                subnets.append(subnet["SubnetId"])

            waiter = self.clientLB.get_waiter('load_balancer_available')
            response = self.clientLB.create_load_balancer(
                Name=self.LB_name,
                Subnets= subnets,
                SecurityGroups=[
                    self.LBSG_ID,
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': 'LB'
                    },
                ],
                IpAddressType='ipv4',
            )
            self.LBArn = response['LoadBalancers'][0]['LoadBalancerArn']
            waiter.wait(LoadBalancerArns=[self.LBArn])
            print("\n------ ORM Load Balancer CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_LBSG(self):
        response = self.client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        try:
            response = self.client.create_security_group(
                Description='northv LoadBalancing SG',
                GroupName=self.LBSG_name,
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'northv LBSG'
                            },
                        ]
                    },
                ]
            )
            self.LBSG_ID = response['GroupId']

            response80 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName=self.LBSG_name,
                FromPort=80,
                ToPort=80,
                IpProtocol='tcp'
            )
            print("\n------ ORM Load Balancer Security Group CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_TG(self):
        try:
            response = self.client.describe_vpcs()
            vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

            response = self.clientLB.create_target_group(
                Name=self.TG_name,
                Port=8080,
                HealthCheckPort='8080',
                Protocol="HTTP",
                VpcId=vpc_id,
                HealthCheckEnabled=True,
                HealthCheckPath='/admin/',
                HealthCheckIntervalSeconds=120,
                HealthCheckTimeoutSeconds=30,
                TargetType='instance'
            )
            self.TGArn = response["TargetGroups"][0]["TargetGroupArn"]
            print("\n------ ORM TargetGroup CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0


    def create_AMI(self):
        try:
            waiter = self.client.get_waiter('image_available')
            response = self.client.create_image(
                Name=self.AMI_name,
                InstanceId=self.InstanceID,
                NoReboot=False
            )
            self.newImageID = response['ImageId']
            waiter.wait(ImageIds=[self.newImageID])
            time.sleep(60)
            print("\n------ ORM Image CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_SG(self):
        response = self.client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        try:
            response = self.client.create_security_group(
                Description='northv SG',
                GroupName=self.SG_name,
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'northv DB'
                            },
                        ]
                    },
                ]
            )
            self.SG_ID = response['GroupId']
            response8080 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName=self.SG_name,
                FromPort=8080,
                ToPort=8080,
                IpProtocol='tcp'
            )
            response80 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName=self.SG_name,
                FromPort=80,
                ToPort=80,
                IpProtocol='tcp'
            )
            response22 = self.client.authorize_security_group_ingress(
                CidrIp='0.0.0.0/0',
                GroupName=self.SG_name,
                FromPort=22,
                ToPort=22,
                IpProtocol='tcp'
            )
            print("\n------ ORM Security Group CREATED ------")
            return 1
        except Exception as e:
            print(e)
            return 0

    def create_instance(self):
        try:
            self.ORM_init = self.ORM_init.replace("OhayoIP", str(self.OhayoIP))
            response = self.ec2_resource.create_instances(
                ImageId= self.ImageID,
                MinCount=1,
                MaxCount=1,
                InstanceType="t2.micro",
                KeyName="helio-key",
                SecurityGroups=[
                    self.SG_name,
                ],
                UserData=self.ORM_init
            )
            waiter = self.client.get_waiter("instance_status_ok")
            waiter.wait(InstanceIds=[response[0].instance_id])
            self.InstanceID = str(response[0].instance_id)
            self.publicIP = str(response[0].public_ip_address)
            print("\n------ ORM Instance CREATED ------")
            print("\n------ Public IP NorthV {} ------".format(self.publicIP))
            return response
        except Exception as e:
            print('Error[CR01] - northv Creation failed')
            print(e)
            return 0

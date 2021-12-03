import boto3
from ohayo  import OhayoGozaimasu
from northv import NorthV
from ORM import ORM
import os

os.system('clear')
print("\t----------------------------------")
print("\t------ Inicialização da AWS ------")
print("\t----------------------------------")

OH = OhayoGozaimasu()

print("\n------ Deleting all instances with ImgID:{} ------".format(OH.ImageID))
check = OH.delete_instance()
print("\n------ Deleting all Security Groups with GroupName:{} ------".format(OH.SG_name))
check = OH.delete_SG()
print("\n------ Inicialização do DataBase Ohayo ------")
print("\n------ Creating Security Group for DataBase ------")
check = OH.create_SG()
print("\n------ Creating Instance for DataBase ------")
check = OH.create_instance()

NV = NorthV()
NV.OhayoIP = OH.publicIP

print("\n------ Deleting Listener with Load Balancer ARN:{} ------".format(NV.LBArn))
check = NV.delete_LS()
print("\n------ Deleting Auto Scaling with name:{} ------".format(NV.AS_name))
check = NV.delete_AS()
print("\n------ Deleting Launch Configuration with name:{} ------".format(NV.LC_name))
check = NV.delete_LC()
print("\n------ Deleting Load Balancer with name:{} ------".format(NV.LB_name))
check = NV.delete_LB()
print("\n------ Deleting Security Group with GroupName:{} ------".format(NV.LBSG_name))
check = NV.delete_LBSG()
print("\n------ Deleting Target Group with name:{} ------".format(NV.TG_name))
check = NV.delete_TG()
print("\n------ Deleting Image with name:{} ------".format(NV.AMI_name))
check = NV.delete_AMI()
print("\n------ Deleting all instances with ImgID:{} ------".format(NV.ImageID))
check = NV.delete_instance()
print("\n------ Deleting Security Group with GroupName:{} ------".format(NV.SG_name))
check = NV.delete_SG()
print("\n------ Inicialização do ORM North Virginia ------")
print("\n------ Creating Security Group for ORM ------")
check = NV.create_SG()
print("\n------ Creating Instance for ORM ------")
check = NV.create_instance()
print("\n------ Creating Image of ORM ------")
check = NV.create_AMI()
print("\n------ Deleting all instances with ImgID:{} ------".format(NV.ImageID))
check = NV.delete_instance()

NV.ImageID = NV.newImageID

print("\n------ Creating TargetGroup of ORM ------")
check = NV.create_TG()
print("\n------ Creating Load Balancer Security Group for ORM ------")
check = NV.create_LBSG()
print("\n------ Creating Load Balancer of ORM ------")
check = NV.create_LB()
print("\n------ Creating Launch Configuration of ORM ------")
check = NV.create_LC()
print("\n------ Creating Auto Scaling of ORM ------")
check = NV.create_AS()
print("\n------ Creating Listener of ORM ------")
check = NV.create_LS()

orm = ORM()
orm.LB_name = NV.LB_name
orm.client()
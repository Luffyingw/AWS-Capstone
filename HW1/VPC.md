# Homework 1 

## Tasks:
    - Create a VPC
    - Create a public subnet
    - Create a private subnet
    - Create a internet gateway and attach to VPC
    - Check ACL and security group
    - Add inbound SSH rule
    - Make sure you can login to you instance in public subnet
    - Create a VPC with both public and private subnet
    - Write a boto3 program to launch two instances in each subnet
    - Verify the one in public subnet can be accessed from internet and another cannot
    - Measure the performance of these two instances (not done yet)

## Reference:

http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-subnets-commands-example.html

http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Scenarios.html


## Table of Content

### Step 1: Create a VPC and Subnets
### Step 2: Make Your Subnet Public
### Step 3: Launch an Instance into Your Subnet
### Step 4: Clean Up

<br>
<br>
<br>
<br>

## Others:
```
aws ec2 describe-vpcs
aws ec2 describe-vpcs --vpc-ids vpc-9e03bfe7
aws ec2 describe-subnets
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-9e03bfe7"
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0aa61173" --query 'Subnets[*].{ID:SubnetId,CIDR:CidrBlock}'
```

## Step1: To create a VPC and subnets using the AWS CLI

**1. Create a VPC with a 10.0.0.0/16 CIDR block.**
```
aws git:(xzhu) aws ec2 create-vpc --cidr-block 10.0.0.0/16
{
    "Vpc": {
        "VpcId": "vpc-0aa61173", 
        "InstanceTenancy": "default", 
        "Tags": [], 
        "Ipv6CidrBlockAssociationSet": [], 
        "State": "pending", 
        "DhcpOptionsId": "dopt-820cc9e4", 
        "CidrBlock": "10.0.0.0/16", 
        "IsDefault": false
    }
}
```
In the output that's returned, take note of the VPC ID.

**2. Using the VPC ID from the previous step, create a subnet with a 10.0.1.0/24 CIDR block.**
```
➜  aws git:(xzhu) aws ec2 create-subnet --vpc-id vpc-0aa61173 --cidr-block 10.0.1.0/24 
{
    "Subnet": {
        "AvailabilityZone": "us-east-1b", 
        "AvailableIpAddressCount": 251, 
        "DefaultForAz": false, 
        "Ipv6CidrBlockAssociationSet": [], 
        "VpcId": "vpc-0aa61173", 
        "State": "pending", 
        "MapPublicIpOnLaunch": false, 
        "SubnetId": "subnet-1cfe9154", 
        "CidrBlock": "10.0.1.0/24", 
        "AssignIpv6AddressOnCreation": false
    }
}
```

**3.Create a second subnet in your VPC with a 10.0.0.0/24 CIDR block.**
```
➜  aws git:(xzhu) aws ec2 create-subnet --vpc-id vpc-0aa61173 --cidr-block 10.0.0.0/24 
{
    "Subnet": {
        "AvailabilityZone": "us-east-1b", 
        "AvailableIpAddressCount": 251, 
        "DefaultForAz": false, 
        "Ipv6CidrBlockAssociationSet": [], 
        "VpcId": "vpc-0aa61173", 
        "State": "pending", 
        "MapPublicIpOnLaunch": false, 
        "SubnetId": "subnet-8dfe91c5", 
        "CidrBlock": "10.0.0.0/24", 
        "AssignIpv6AddressOnCreation": false
    }
}
```

## Step 2: Make Your Subnet Public

**1. Create an Internet gateway.**
```
➜  aws git:(xzhu) aws ec2 create-internet-gateway
{
    "InternetGateway": {
        "Tags": [], 
        "Attachments": [], 
        "InternetGatewayId": "igw-55d6b033"
    }
}
```
In the output that's returned, take note of the Internet gateway ID.


**2.Using the ID from the previous step, attach the Internet gateway to your VPC.**
```
➜  aws git:(xzhu) aws ec2 attach-internet-gateway --vpc-id vpc-0aa61173 --internet-gateway-id igw-55d6b033
```

**3.Create a custom route table for your VPC.**
```
➜  aws git:(xzhu) aws ec2 create-route-table --vpc-id vpc-0aa61173
{
    "RouteTable": {
        "Associations": [], 
        "RouteTableId": "rtb-207f0d58", 
        "VpcId": "vpc-0aa61173", 
        "PropagatingVgws": [], 
        "Tags": [], 
        "Routes": [
            {
                "GatewayId": "local", 
                "DestinationCidrBlock": "10.0.0.0/16", 
                "State": "active", 
                "Origin": "CreateRouteTable"
            }
        ]
    }
}
```
In the output that's returned, take note of the route table ID.

**4. Create a route in the route table that points all traffic (0.0.0.0/0) to the Internet gateway.**
```
➜  aws git:(xzhu) aws ec2 create-route --route-table-id rtb-207f0d58 --destination-cidr-block 0.0.0.0/0 --gateway-id igw-55d6b033
{
    "Return": true
}
```

**5.To confirm that your route has been created and is active, you can describe the route table and view the results.**
```
➜  aws git:(xzhu) aws ec2 describe-route-tables --route-table-id rtb-207f0d58
{
    "RouteTables": [
        {
            "Associations": [], 
            "RouteTableId": "rtb-207f0d58", 
            "VpcId": "vpc-0aa61173", 
            "PropagatingVgws": [], 
            "Tags": [], 
            "Routes": [
                {
                    "GatewayId": "local", 
                    "DestinationCidrBlock": "10.0.0.0/16", 
                    "State": "active", 
                    "Origin": "CreateRouteTable"
                }, 
                {
                    "GatewayId": "igw-55d6b033", 
                    "DestinationCidrBlock": "0.0.0.0/0", 
                    "State": "active", 
                    "Origin": "CreateRoute"
                }
            ]
        }
    ]
}
```

**6.The route table is currently not associated with any subnet. You need to associate it with a subnet in your VPC so that traffic from that subnet is routed to the Internet gateway. First, use the describe-subnets command to get your subnet IDs. You can use the --filter option to return the subnets for your new VPC only, and the --query option to return only the subnet IDs and their CIDR blocks.**
```
➜  aws git:(xzhu) aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0aa61173" --query 'Subnets[*].{ID:SubnetId,CIDR:CidrBlock}'
[
    {
        "CIDR": "10.0.1.0/24", 
        "ID": "subnet-1cfe9154"
    }, 
    {
        "CIDR": "10.0.0.0/24", 
        "ID": "subnet-8dfe91c5"
    }
]
```

**7. You can choose which subnet to associate with the custom route table**
```
➜  aws git:(xzhu) aws ec2 associate-route-table  --subnet-id subnet-1cfe9154 --route-table-id rtb-207f0d58
{
    "AssociationId": "rtbassoc-7defb406"
}
```

**8. You can optionally modify the public IP addressing behavior of your subnet so that an instance launched into the subnet automatically receives a public IP address. Otherwise, you should associate an Elastic IP address with your instance after launch so that it's reachable from the Internet.**
```
➜  aws git:(xzhu) aws ec2 modify-subnet-attribute --subnet-id subnet-1cfe9154 --map-public-ip-on-launch
```




## Step 3: Launch an Instance into Your Subnet

**1.Create a key pair and use the --query option and the --output text option to pipe your private key directly into a file with the .pem extension.**
```
➜  ~ git:(master) ✗ aws ec2 create-key-pair --key-name cs502keyPair --query 'KeyMaterial' --output text > cs502keyPair.pem
```

use the following command to set the permissions of your private key file so that only you can read it.
```
chmod 400 MyKeyPair.pem
```


**2.Create a security group in your VPC, and add a rule that allows SSH access from anywhere.**
```
➜  ~ git:(master) ✗ aws ec2 create-security-group --group-name CS502SSHAccess --description "CS502 Security group for SSH access" --vpc-id vpc-0aa61173
{
    "GroupId": "sg-13914562"
}
```

```
➜  ~ git:(master) ✗ aws ec2 authorize-security-group-ingress --group-id sg-13914562  --protocol tcp --port 22 --cidr 0.0.0.0/0
```

Note
If you use 0.0.0.0/0, you enable all IPv4 addresses to access your instance using SSH. This is acceptable for this short exercise, but in production, authorize only a specific IP address or range of addresses.



**3.Launch an instance into your public subnet, using the security group and key pair you've created. In the output, take note of the instance ID for your instance.**
```
➜  ~ git:(master) ✗ aws ec2 run-instances --image-id ami-a4827dc9 --count 1 --instance-type t2.micro --key-name cs502keyPair --security-group-ids sg-13914562 --subnet-id subnet-1cfe9154
{
    "Instances": [
        {
            "Monitoring": {
                "State": "disabled"
            }, 
            "PublicDnsName": "", 
            "StateReason": {
                "Message": "pending", 
                "Code": "pending"
            }, 
            "State": {
                "Code": 0, 
                "Name": "pending"
            }, 
            "EbsOptimized": false, 
            "LaunchTime": "2017-06-21T04:10:17+00:00", 
            "PrivateIpAddress": "10.0.1.80", 
            "ProductCodes": [], 
            "VpcId": "vpc-0aa61173", 
            "StateTransitionReason": "", 
            "InstanceId": "i-043d5e6104612adef", 
            "ImageId": "ami-a4827dc9", 
            "PrivateDnsName": "ip-10-0-1-80.ec2.internal", 
            "KeyName": "cs502keyPair", 
            "SecurityGroups": [
                {
                    "GroupName": "CS502SSHAccess", 
                    "GroupId": "sg-13914562"
                }
            ], 
            "ClientToken": "", 
            "SubnetId": "subnet-1cfe9154", 
            "InstanceType": "t2.micro", 
            "NetworkInterfaces": [
                {
                    "Status": "in-use", 
                    "MacAddress": "0a:20:4c:c0:a0:62", 
                    "SourceDestCheck": true, 
                    "VpcId": "vpc-0aa61173", 
                    "Description": "", 
                    "NetworkInterfaceId": "eni-221f1ef3", 
                    "PrivateIpAddresses": [
                        {
                            "Primary": true, 
                            "PrivateIpAddress": "10.0.1.80"
                        }
                    ], 
                    "SubnetId": "subnet-1cfe9154", 
                    "Attachment": {
                        "Status": "attaching", 
                        "DeviceIndex": 0, 
                        "DeleteOnTermination": true, 
                        "AttachmentId": "eni-attach-bc7a6183", 
                        "AttachTime": "2017-06-21T04:10:17+00:00"
                    }, 
                    "Groups": [
                        {
                            "GroupName": "CS502SSHAccess", 
                            "GroupId": "sg-13914562"
                        }
                    ], 
                    "Ipv6Addresses": [], 
                    "OwnerId": "956509078878", 
                    "PrivateIpAddress": "10.0.1.80"
                }
            ], 
            "SourceDestCheck": true, 
            "Placement": {
                "Tenancy": "default", 
                "GroupName": "", 
                "AvailabilityZone": "us-east-1b"
            }, 
            "Hypervisor": "xen", 
            "BlockDeviceMappings": [], 
            "Architecture": "x86_64", 
            "RootDeviceType": "ebs", 
            "RootDeviceName": "/dev/xvda", 
            "VirtualizationType": "hvm", 
            "AmiLaunchIndex": 0
        }
    ], 
    "ReservationId": "r-00742ec032514c8ee", 
    "Groups": [], 
    "OwnerId": "956509078878"
}
```
Note
In this example, the AMI is an Amazon Linux AMI in the US East (N. Virginia) region. If you're in a different region, you'll need the AMI ID for a suitable AMI in your region. For more information, see Finding a Linux AMI in the Amazon EC2 User Guide for Linux Instances.


**4.Your instance must be in the running state in order to connect to it. Describe your instance and confirm its state, and take note of its public IP address.**
```
➜  ~ git:(master) ✗ aws ec2 describe-instances --instance-id i-043d5e6104612adef
```


**5.When your instance is in the running state, you can connect to it using an SSH client on a Linux or Mac OS X computer by using the following command:**
```
➜  ~ git:(master) ✗ ssh -i "cs502keyPair.pem" ec2-user@107.23.125.50                 
The authenticity of host '107.23.125.50 (107.23.125.50)' can't be established.
ECDSA key fingerprint is SHA256:LkoUtndUzPNR37e26MTbgMPNNsYiKaR//aXXX1XSlqA.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '107.23.125.50' (ECDSA) to the list of known hosts.
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for 'cs502keyPair.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "cs502keyPair.pem": bad permissions
Permission denied (publickey).
➜  ~ git:(master) ✗ ls -l cs502keyPair.pem 
-rw-r--r--  1 xingyuzhu  staff  1675 Jun 21 00:04 cs502keyPair.pem
➜  ~ git:(master) ✗ chmod 400 cs502keyPair.pem 
➜  ~ git:(master) ✗ ls -l cs502keyPair.pem                          
-r--------  1 xingyuzhu  staff  1675 Jun 21 00:04 cs502keyPair.pem
➜  ~ git:(master) ✗ ssh -i "cs502keyPair.pem" ec2-user@107.23.125.50

       __|  __|_  )
       _|  (     /   Amazon Linux AMI
      ___|\___|___|

https://aws.amazon.com/amazon-linux-ami/2016.03-release-notes/
22 package(s) needed for security, out of 95 available
Run "sudo yum update" to apply all updates.
Amazon Linux version 2017.03 is available.
[ec2-user@ip-10-0-1-80 ~]$ ls
[ec2-user@ip-10-0-1-80 ~]$ ls
[ec2-user@ip-10-0-1-80 ~]$ sudo yum update
```







**Verify the one in public subnet can be accessed from internet and another cannot**

```
➜  ~ git:(master) ✗ ssh -i "cs502keyPair.pem" ec2-user@10.0.0.149    
ssh: connect to host 10.0.0.149 port 22: Network is unreachable
```






## Step 4: Clean Up
**stop and terminate EC2 instances**
```
aws ec2 stop-instances --instance-id i-043d5e6104612adef
aws ec2 terminate-instances --instance-id i-0d66d0d931245cead
```

```
➜  ~ git:(master) ✗ aws ec2 delete-security-group --group-id sg-13914562
➜  ~ git:(master) ✗ aws ec2 delete-subnet --subnet-id subnet-1cfe9154
➜  ~ git:(master) ✗ aws ec2 delete-subnet --subnet-id subnet-8dfe91c5
➜  ~ git:(master) ✗ aws ec2 delete-route-table --route-table-id rtb-207f0d58
➜  ~ git:(master) ✗ aws ec2 detach-internet-gateway --internet-gateway-id igw-55d6b033 --vpc-id vpc-0aa61173
➜  ~ git:(master) ✗ aws ec2 delete-internet-gateway --internet-gateway-id igw-55d6b033
➜  ~ git:(master) ✗ aws ec2 delete-vpc --vpc-id vpc-0aa61173
```







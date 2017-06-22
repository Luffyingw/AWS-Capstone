# Boto 3
import boto3

ec2 = boto3.resource('ec2')


ec2.create_instances(ImageId='ami-a4827dc9', InstanceType='t2.micro', KeyName='cs502keyPair', SecurityGroupIds=['sg-13914562'], MinCount=1, MaxCount=1, SubnetId='subnet-1cfe9154')
print("lanched 2 EC2 instance for public subnet")

ec2.create_instances(ImageId='ami-a4827dc9', InstanceType='t2.micro', KeyName='cs502keyPair', SecurityGroupIds=['sg-13914562'], MinCount=1, MaxCount=1, SubnetId='subnet-8dfe91c5')
print("lanched 2 EC2 instance for private subnet")

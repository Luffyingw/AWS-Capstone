# Boto 3
import boto3

ec2 = boto3.resource('ec2')
# Boto 3
for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
    print(status)
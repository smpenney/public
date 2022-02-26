import boto3

# 1. Setup
profile = 'spenney_lab'
my_ip = '209.6.118.177'
vpc_id = 'vpc-006cc03a47f73b221'
subnet_id = 'subnet-0250fa10629e58f13'
key_name = 'thara-key-pair'

# 2. Create a security group
def create_sg(session, vpc_id, my_ip) -> str:
    print('Creating Security Group...')
    client = session.client('ec2', 'us-east-1')
    response = client.create_security_group(GroupName='Web Server',
                                        Description='Ingress port 80, port 22 restricted',
                                        VpcId=vpc_id)
    sg_id = response['GroupId']
    print(f'Created security group {sg_id} in vpc {vpc_id}')

    sg_data = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
             'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}] # traffic from anywhere in the world
            },
            {
             'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': f'{my_ip}/32'}] # traffic from IP Address only
            }
        ]
    )
    return sg_id

# 3. Create the EC2 server
def create_instance(session, sg_id) -> str:
    ec2_client = session.client('ec2', 'us-east-1')
    print(f'Creating EC2 Instance...')
    # deploys the server
    instances = ec2_client.run_instances(
        ImageId="ami-04505e74c0741db8d",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.nano",
        KeyName=f"{key_name}",
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': [
                    sg_id
                ],
                'AssociatePublicIpAddress': True
            },
        ],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': 10,
                    'VolumeType': 'standard'
                }
            }
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': 'cs6620-ec2-lab2'
                }]
            }
        ],
    )
    instance_id = instances['Instances'][0]['InstanceId']
    return instance_id

# 
def main():
    # session = boto3.Session(
    #    aws_access_key_id=ACCESS_KEY,
    #    aws_secret_access_key=SECRET_KEY
    # )
   
    session = boto3.Session() # creating a session
    sg_id = create_sg(session, vpc_id, my_ip) # creating a security group
    instance_id = create_instance(session, sg_id) # creating a server
    print(f'Created EC2 instance {instance_id} with public IP')


if __name__ == '__main__':
    main()

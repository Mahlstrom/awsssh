import boto3
from src.cache import cache
from pprint import pprint

ec2 = boto3.resource('ec2')


@cache
def get_instances():
    """

    :return: list of ec2.Instance
    """
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    all = {}
    for instance in instances:
        name = ''
        vpcid = ''
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
        if instance.vpc:
            vpcid = instance.vpc.id

        ret = {
            'id': instance.id,
            'name': name,
            'private_ip': instance.private_ip_address,
            'public_ip': instance.public_ip_address,
            'vpc_id': vpcid,
            'image_id': instance.image_id,
            'private_key': instance.key_name
        }
        if not name in all:
            all[name] = []
        all[name].append(ret)
    return all


def get_username(amiid):
    image = ec2.Image(amiid)

    user = 'ec2-user'
    if 'ubuntu' in image.name:
        user = 'ubuntu'
    return user


def get_bastion(vpcId):
    instances = get_instances()
    for name in instances:
        if "bastion" in name:
            for i in instances[name]:
                if i['vpc_id'] == vpcId:
                    return i
    return False

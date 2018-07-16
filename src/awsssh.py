import shlex
import subprocess
from pprint import pprint
from pick import pick

from src.aws import get_instances, get_username, get_bastion


def awsssh(server_name):
    # Fetch all instances grouped by name
    instances = get_instances()
    # List all instance names
    if server_name == '--list':
        for name in sorted(instances.keys()):
            print(name)
        exit()

    # If argument does not match help list or any instance name, exit
    elif server_name not in instances:
        print(server_name + " is not a server")
        exit()

    # ssh command with no strict host key checking
    custom_ssh = ['ssh', '-o', 'StrictHostKeyChecking=no']
    # Do we have mutliple instances for the wanted name
    if len(instances[server_name]) > 1:
        options = [i['id'] for i in instances[server_name]]
        option, index = pick(options, 'Select a server')
        instance = instances[server_name][index]
    else:
        instance = instances[server_name][0]
    # Get username based on amazon image type
    username = get_username(instance['image_id'])
    # Lets check if we need to use bastion servers
    if instance['public_ip'] is None:
        # get bastion from vpc id
        bastion = get_bastion(instance['vpc_id'])
        if not bastion:
            print("can't find bastion")
            exit()
        # get bastion username based on amazon image type
        bastion_user = get_username(bastion['image_id'])

        # extend the ssh command with proxycommand and the username/private ip
        proxy_command = 'ssh ' + bastion_user + '@' + bastion['public_ip'] + ' nc %h %p'
        custom_ssh.extend(['-o ProxyCommand="{0}"'.format(proxy_command)])
        custom_ssh.extend([username + '@' + instance['private_ip']])
    else:
        # Extend the ssh command with username/public ip
        custom_ssh.extend([username + '@' + instance['public_ip']])
    # execute ssh command
    try:
        returncode = subprocess.call(shlex.split(' '.join(custom_ssh)))
    except (KeyboardInterrupt, SystemExit):
        exit()

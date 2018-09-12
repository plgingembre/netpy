#!/usr/bin/env python

import netmiko
import sys
import getpass
username = raw_input('Enter username: ')
password = getpass.getpass('Enter password: ')
devices = open('devices.txt','r')
devices = devices.read()
devices = devices.strip().splitlines()
print(devices)
exceptions = (netmiko.ssh_exception.NetMikoTimeoutException, netmiko.ssh_exception.NetMikoAuthenticationException)
for device in devices:
    try:
        connection = netmiko.ConnectHandler(ip=device, device_type='cisco_nxos', username=username,password=password)
        print 'Connected to', device
        output = connection.send_command('show interface Eth1/1/1-4 status | inc connected')
        print('=' * 80)
        print(output)
        output = output.strip().splitlines()
        print('=' * 80)
        print(output)
        config_list = []
        for lines in output:
            words = lines.split()
            if 'Eth' in lines:
                config_list.append('interface ' + words[0])
                config_list.append('shut')
                print('=' * 80)
                print(config_list)
        connection.send_config_set(config_list)
        connection.disconnect()
    except exceptions as exception_type:
        print(device+' failed connection: ')

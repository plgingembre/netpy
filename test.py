#!/usr/bin/env python

"""
Script to upgrade couple of Pluribus switches. Steps:
1/ Connect to the switch
2/ Enable SFTP on the switch
3/ Push the file on the local disk
4/ Upgrade the switch
"""

import paramiko
import getpass
#import netmiko
import os,sys,time,datetime
# Import hostfile from another directory
sys.path.insert(0, '/Users/pierregi/python/hostfiles/')
import socket
# Import lists of hosts as an object called devices
import hosts as devices
from netmiko import ConnectHandler


#print '!! Enter SSH UserName !!'
#ssh_username = raw_input("Username: ")
ssh_username = 'network-admin'
print '!! Enter SSH Password !!'
ssh_password = getpass.getpass()
#print '!! Enter SFTP UserName !!'
#sftp_username = raw_input("Username: ")
print '!! Enter SFTP Password !!'
sftp_password = getpass.getpass()

#print 'Your SSH username is:',ssh_username
#print 'Your SSH password is:',ssh_password
#print 'Your SFTP username is:',sftp_username
#print 'Your SFTP password is:',sftp_password

switch = {
    'device_type': 'pluribus',
    'ip': '10.36.10.37',
    'username': ssh_username,
    'password': ssh_password,
    'port': 22,
    'verbose': True,
}

net_connect = ConnectHandler(**switch)
output = net_connect.send_command('admin-sftp-show')
print '1st output is:\n' + output + '\n'
output = net_connect.send_command_timing('admin-sftp-modify enable', strip_command=False, strip_prompt=False)
print '2nd output is:\n' + output + '\n'
#prompt =  net_connect.find_prompt()
time.sleep(3)
#if 'sftp password' in output:
#    output += net_connect.send_command_timing("test123\n", strip_command=False, strip_prompt=False)
#    print '3rd output is:\n' + output + '\n'
#if 'confirm sftp password' in output:
#    output += net_connect.send_command_timing("test123\n", strip_command=False, strip_prompt=False)
#    print '4th output is:\n' + output + '\n'

while 'sftp password' in output:
    output = net_connect.send_command_timing("test123\n", strip_command=False, strip_prompt=False)
    print '3rd output is:\n' + output + '\n'

    #net_connect.write_channel(sftp_password + '\n')
    #time.sleep(3)
#time.sleep(5)
#net_connect.send_command('test123')
#net_connect.write_channel(sftp_password + '\n')
#time.sleep(5)
#net_connect.write_channel(sftp_password + '\n')
#time.sleep(5)
#output = net_connect.send_command('admin-sftp-show\n')
#print '5th output is:\n' + output + '\n'

net_connect.disconnect()

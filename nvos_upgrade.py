#!/usr/bin/env python

"""
Utility script to ssh into a switch and check disks from
the NOS and the shell
"""

#import paramiko
import netmiko
from netmiko import ConnectHandler
import os,sys,time
# Import hostfile from another directory
sys.path.insert(0, '/Users/pierregi/python/hostfiles/')
import socket
# Import lists of hosts as an object called devices
import hosts as devices


class Ssh_Util:
    "Class to connect to remote server"


    def __init__(self):
        self.ssh_output = None
        self.ssh_error = None
        self.shell_username = devices.SHELL_USERNAME
        self.solaris_username = devices.SOLARIS_USERNAME
        self.nos_username = devices.NETVISOR_USERNAME
        self.default_password = devices.NETVISOR_DEFAULT_PASSWORD
        self.tme_password = devices.NETVISOR_TME_BE_PASSWORD
        self.ebc_password = devices.NETVISOR_EBC_BE_PASSWORD
        self.timeout = float(devices.TIMEOUT)
        self.pkey = devices.PKEY
        self.port = devices.PORT
        self.platform = devices.PLATFORM


    def nos_connect(self,hosts):
        #print "===> Login to the remote switch (network OS access)\n"
        try:
            print "===> Connecting to switch",hosts,"(network os)"
            if hosts in devices.TME_BE_SWITCHES:
                self.device = ConnectHandler(device_type=self.platform, ip=hosts, username=self.nos_username, password=self.tme_password)
            elif hosts in devices.EBC_ACCTON_SWITCHES_2 or hosts in devices.EBC_DELL_SWITCHES_2:
                self.device = ConnectHandler(device_type=self.platform, ip=hosts, username=self.nos_username, password=self.ebc_password)
            else:
                self.device = ConnectHandler(device_type=self.platform, ip=hosts, username=self.nos_username, password=self.default_password)
        except netmiko.ssh_exception.NetMikoTimeoutException as sshTimeout:
            print "Could not connect to the switch: %s" % sshTimeout
            result_flag = False
        else:
            result_flag = True

        return result_flag


    def execute_nos_command(self,hosts,commands):
        result_flag = True
        try:
            if self.nos_connect(hosts):
                for command in commands:
                    output = self.device.send_command(command)
                    print output
                self.device.disconnect()
            else:
                print "Could not establish SSH connection to",hosts
                result_flag = False
        except netmiko.ssh_exception.NetMikoTimeoutException as sshTimeout:
            print "Could not connect to the switch: %s" % sshTimeout
            result_flag = False
        except socket.error as e:
            print "Connection error"
            result_flag = False
        except Exception,e:
            print '\nException in connecting to the server'
            print 'PYTHON SAYS:',e
            result_flag = False

        return result_flag


if __name__=='__main__':
    #Initialize the ssh object
    ssh_obj = Ssh_Util()

    #hosts = devices.TESTBED
    hosts = ['10.36.10.11']
    nos_commands = ['software-upgrade package nvOS-3.0.4-3000413314-onvl.pkg']
    nos_commands_2 = ['software-upgrade-status-show']

    for host in hosts:
        print "=" * 80
        ssh_obj.execute_nos_command(host,nos_commands)
    time.sleep(5)
    for host in hosts:
        print "=" * 80
        ssh_obj.execute_nos_command(host,nos_commands_2)

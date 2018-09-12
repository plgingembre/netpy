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
import pysftp as sftp
# Import lists of hosts as an object called devices
import hosts as devices
from netmiko import ConnectHandler


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
        try:
            print "===> Connecting to switch",hosts
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


    def enable_sftp(self,hosts):
        result_flag = True
        try:
            if self.nos_connect(hosts):
                print '===> Enabling SFTP on {}'.format(hosts)
                output = self.device.send_command_timing('admin-sftp-modify enable', strip_command=False, strip_prompt=False)
                time.sleep(3)
                while 'sftp password' in output:
                    output = self.device.send_command_timing("test123\n", strip_command=False, strip_prompt=False)
            else:
                print "Could not establish SSH connection to",hosts
                result_flag = False
        except Exception,e:
            print '\nException in connecting to the server'
            print 'PYTHON SAYS:',e
            result_flag = False

        return result_flag


    def upload_file(self,hosts,uploadlocalfilepath,uploadremotefilepath):
        "This method uploads the file to the remote switch"
        result_flag = True
        try:
            print '===> Uploading Netvisor OS image {} to {}'.format(uploadlocalfilepath,hosts)
            s = sftp.Connection(host=hosts, username='sftp', password=self.default_password)
            s.put(uploadlocalfilepath,uploadremotefilepath)
            s.close()
        except Exception,e:
            print '\nUnable to upload the file to the remote server',uploadremotefilepath
            print 'PYTHON SAYS:',e
            result_flag = False
            s.close()
            self.device.close()

        return result_flag


    def execute_nos_upgrade(self,hosts,upgrade_package):
        result_flag = True
        try:
            print '===> Upgrading Netvisor OS image to {} on {}'.format(upgrade_package.strip('import/'),hosts)
            output = self.device.send_command('software-upgrade package '+upgrade_package)
            print output
            self.device.disconnect()
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

    hosts = devices.TESTBED
    print 'Please provide Netvisor OS image name for this upgrade:  '
    source_file_path = raw_input('New Netvisor OS image path: ')
    sftp_password = getpass.getpass('SFTP password: ')
    dest_file_path = 'import/'+source_file_path
    print dest_file_path
    for host in hosts:
        ftp_client = host
        print "=" * 80
        ssh_obj.enable_sftp(host)
        ssh_obj.upload_file(host,source_file_path,dest_file_path)
        ssh_obj.execute_nos_upgrade(host,dest_file_path)

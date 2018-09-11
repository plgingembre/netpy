#!/usr/bin/env python

"""
Utility script to ssh into a switch and check disks from
the NOS and the shell
"""

import paramiko
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
        #self.device = devices.HOSTS # List of elements
        self.shell_username = devices.SHELL_USERNAME
        self.solaris_username = devices.SOLARIS_USERNAME
        self.nos_username = devices.NETVISOR_USERNAME

        #self.shell_password = devices.SHELL_PASSWORD
        self.default_password = devices.NETVISOR_DEFAULT_PASSWORD
        self.tme_password = devices.NETVISOR_TME_BE_PASSWORD
        self.ebc_password = devices.NETVISOR_EBC_BE_PASSWORD

        self.timeout = float(devices.TIMEOUT)
        #self.commands = devices.PN_COMMANDS # List of elements
        self.pkey = devices.PKEY
        self.port = devices.PORT
        self.platform = devices.PLATFORM


    def shell_connect(self,hosts):
        #print "\n===> Login to the remote switch (shell access)"
        try:
            #Paramiko.SSHClient can be used to make connections to the remote server and transfer files
            print "\n===> Connecting to switch",hosts,"(shell)\n"
            self.device = paramiko.SSHClient()
            #Parsing an instance of the AutoAddPolicy to set_missing_host_key_policy() changes it to allow any host.
            self.device.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #Connect to the server
            if hosts in devices.TME_BE_SWITCHES:
                if (self.tme_password == ''):
                    self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey)
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, pkey=self.pkey, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
                else:
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, password=self.tme_password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
            elif hosts in devices.EBC_ACCTON_SWITCHES_2 or hosts in devices.EBC_DELL_SWITCHES_2:
                if (self.tme_password == ''):
                    self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey)
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, pkey=self.pkey, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
                else:
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, password=self.ebc_password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
            elif hosts in devices.TME_SOLARIS_SWITCHES or hosts in devices.DISTRI:
                if (self.tme_password == ''):
                    self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey)
                    self.device.connect(hostname=hosts, port=self.port, username=self.solaris_username, pkey=self.pkey, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
                else:
                    self.device.connect(hostname=hosts, port=self.port, username=self.solaris_username, password=self.default_password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
            else:
                if (self.default_password == ''):
                    self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey)
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, pkey=self.pkey, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
                else:
                    self.device.connect(hostname=hosts, port=self.port, username=self.shell_username, password=self.default_password, timeout=self.timeout, allow_agent=False, look_for_keys=False)
                    #print "===> Connected to the server",hosts,"\n"
        except paramiko.AuthenticationException:
            print "Authentication failed, please verify your credentials"
            result_flag = False
        except paramiko.SSHException as sshException:
            print "Could not establish SSH connection: %s" % sshException
            result_flag = False
        except socket.timeout as e:
            print "Connection timed out"
            result_flag = False
        except Exception,e:
            print '\nException in connecting to the server'
            print 'PYTHON SAYS:',e
            result_flag = False
            self.device.close()
        else:
            result_flag = True

        return result_flag


    def nos_connect(self,hosts):
        print "===> Login to the remote switch (network OS access)\n"
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
        #except socket.error as e:
        #    print "Connection error"
        #    result_flag = False
        #except Exception,e:
        #    print '\nException in connecting to the server'
        #    print 'PYTHON SAYS:',e
        #    result_flag = False
        #    self.device.disconnect()
        else:
            result_flag = True

        return result_flag


    def execute_shell_command(self,hosts,commands):
        """Execute a command on the remote host. Return a tuple containing
        an integer status and a two strings, the first containing stdout
        and the second containing stderr from the command."""
        self.ssh_output = None
        result_flag = True
        try:
            if self.shell_connect(hosts):
                for command in commands:
                    print "===> Executing command \'{}\' on switch {}".format(command,host)
                    #print "Checking if the string starts with 'sudo': "+ str(command.startswith('sudo'))
                    if command.startswith('sudo'):
                        stdin, stdout, stderr = self.device.exec_command(command,timeout=10,get_pty=True)
                        #print "Waiting 1 sec before sending sudo password..."
                        # Waiting a second before sending the root password
                        time.sleep(2)
                        if hosts in devices.TME_BE_SWITCHES:
                            stdin.write(self.tme_password + "\n")
                        else:
                            stdin.write(self.default_password + "\n")
                        stdin.flush()
                    else:
                        stdin, stdout, stderr = self.device.exec_command(command,timeout=10)
                    self.ssh_output = stdout.read()
                    self.ssh_error = stderr.read()
                    if self.ssh_error:
                        print "Problem occurred while running command:"+ command + " The error is " + self.ssh_error
                        result_flag = False
                    else:
                        #print "Command execution completed successfully:",command
                        #print "===> Command output:\n" + self.ssh_output
                        print self.ssh_output
                self.device.close()
            else:
                print "Could not establish SSH connection"
                result_flag = False
        except socket.timeout as e:
            print "Command timed out.",command
            self.device.close()
            result_flag = False
        except paramiko.SSHException:
            print "Failed to execute the command!",command
            self.device.close()
            result_flag = False

        return result_flag


    def execute_nos_command(self,hosts,commands):
        """Execute a command on the remote host. Return a tuple containing
        an integer status and a two strings, the first containing stdout
        and the second containing stderr from the command."""
        self.ssh_output = None
        result_flag = True
        try:
            if self.nos_connect(hosts):
                #print "===> Connected to switch",hosts
                for command in commands:
                    #print "===> Executing command on {} --> {}".format(hosts,command)
                    output = self.device.send_command(command)
                    #self.ssh_output = stdout.read()
                    #self.ssh_error = stderr.read()
                    #if self.ssh_error:
                        #print "Problem occurred while running command:"+ command + " The error is " + self.ssh_error
                        #result_flag = False
                    #else:
                        #print "Command execution completed successfully:",command
                        #print "===> Command output:\n" + self.ssh_output
                    print output
                self.device.disconnect()
            else:
                print "Could not establish SSH connection to",hosts
                result_flag = False

        #except paramiko.AuthenticationException:
        #    print "Authentication failed, please verify your credentials"
        #    result_flag = False
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
        #except paramiko.SSHException as sshException:
        #    print "Could not establish SSH connection: %s" % sshException
        #    result_flag = False

        return result_flag


if __name__=='__main__':
    #Initialize the ssh object
    ssh_obj = Ssh_Util()

    hosts = devices.EBC_DELL_SWITCHES
    shell_commands = ['lsblk', 'sudo -S parted /dev/sda print', 'sudo -S parted /dev/sdb print']
    #shell_commands = ['sudo uname -a']
    nos_commands = ['switch-local switch-info-show format switch,model,chassis-serial,system-mem,disk-model,disk-type,disk-firmware', 'switch-local switch-setup-show format device-id']
    #nos_commands = ['switch-local switch-info-show format switch,model,chassis-serial']

#    print """
#+------------------------------------------------------------------------------+
#|                 Inspecting devices in the TME Backend Fabric                 |
#+------------------------------------------------------------------------------+
#    """
    for host in hosts:
        print "=" * 80
        ssh_obj.execute_nos_command(host,nos_commands)
        ssh_obj.execute_shell_command(host,shell_commands)
    #for host in hosts:
    #    if ssh_obj.execute_shell_command(host,ssh_obj.commands) is True:
    #        print ""
    #    else:
    #        print "Unable to execute the commands\n"

    #hosts = devices.TME_ACCTON_SWITCHES + devices.TME_DELL_SWITCHES + devices.TME_SOLARIS_SWITCHES
    #print "\n===> Inspecting Linux DUTs\n"
    #for host in hosts:
    #    if ssh_obj.execute_command(host,ssh_obj.commands) is True:
    #        print ""
    #    else:
    #        print "Unable to execute the commands\n"

    #hosts = devices.TME_SOLARIS_SWITCHES
    #print "\n===> Inspecting Solaris DUTs\n"
    #for host in hosts:
    #    if ssh_obj.execute_command(host,ssh_obj.commands) is True:
    #        print ""
    #    else:
    #        print "Unable to execute the commands\n"

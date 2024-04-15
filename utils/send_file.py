# Name: send_file.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description:
# Python Version: 3.9

# Importing necessary libraries
import paramiko
import os

from utils import load_config


def send_file_via_ssh(local_path, remote_path):
    # Připojení přes SSH
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(load_config.load_credentials("ftp_server"),
                username=load_config.load_credentials("ftp_username"),
                key_filename=load_config.load_credentials("ssh_private_key_path"))

    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)

    sftp.close()
    ssh.close()

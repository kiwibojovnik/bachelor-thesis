# Name: send_file.py
# Author: Dalibor Kyjovský (xkyjov03)
# Date: April 11, 2024
# Description: Sends a file via SSH.
# Python Version: 3.12.3

# Import necessary libraries
import paramiko  # Importing Paramiko library for SSH functionality
import os  # Importing os module for system-related operations

from utils import load_config  # Importing load_config function from the utils module


def send_file_via_ssh(local_path, remote_path):
    """
    Sends a file via SSH using Paramiko library.

    Args:
        local_path (str): Local path of the file to be sent.
        remote_path (str): Remote path where the file will be sent.
    """
    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the SSH server
    ssh.connect(
        load_config.load_credentials("ftp_server"),
        username=load_config.load_credentials("ftp_username"),
        key_filename=load_config.load_credentials("ssh_private_key_path")
    )

    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)

    sftp.close()
    ssh.close()

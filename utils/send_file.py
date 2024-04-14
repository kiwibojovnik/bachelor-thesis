# TODO: Send file from BElarus over ftp to Czechia


import paramiko
import os
import json


def load_key(path):
    pass  # with open()


def load_config():
    with open(f'config/config.json') as f:
        f.read()


def load_credentials(credentials_type):
    with open(f'config/config.json') as f:
        config_data = json.load(f)

    return config_data[credentials_type]


def send_file_via_ssh(local_path, remote_path):
    # Připojení přes SSH
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(load_credentials("ftp_server"), username=load_credentials("ftp_username"),
                password="mocXot-rerjo6-megzap@")#=load_credentials("ssh_private_key_path"))

    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)

    sftp.close()
    ssh.close()


print(os.getcwd())
load_config()

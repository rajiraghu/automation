from paramiko import client

tgt_ips = ['192.168.47.21', '192.168.47.250', '192.168.47.82']
tgt_username = 'root'
tgt_password = 'Nbv12345'

class ssh(object):
    client = None

    def __init__(self, address, username, password):
        print 'connecting to server with IP {0}'.format(address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)

    def send_command(self, command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata
 
                    #print(str(alldata, "utf8"))
                    return alldata
        else:
            print("Connection not opened.")


def copy_files():
    src_ip = '192.168.47.102'
    src_username = 'rajraghu'
    src_password = 'Nbv12345'

    src_ssh = ssh(src_ip, src_username, src_password)
    src_key = src_ssh.send_command('cat ~/.ssh/id_rsa.pub')

    files = ['/home/rajraghu/iperf-2.0.5-11.el6.x86_64.rpm']
    tgt_dir = '/root'

    for tgt_ip in tgt_ips:
        tgt_ssh = ssh(tgt_ip, tgt_username, tgt_password)
        out = tgt_ssh.send_command('ls ~/.ssh')
        if not out:
            out = tgt_ssh.send_command('mkdir ~/.ssh')
        cmd = 'echo {0} >> ~/.ssh/authorized_keys'.format(src_key)
        tgt_ssh.send_command(cmd)
        cmd = 'chmod 640 ~/.ssh/authorized_keys'
        tgt_ssh.send_command(cmd)
        for file in files:
            cmd = 'scp -o StrictHostKeyChecking=no {0} {1}@{2}:{3}'.format(file, tgt_username, tgt_ip, tgt_dir)
            out = src_ssh.send_command(cmd)
            

def exec_cmds():
    cmds = ['ifconfig -a', 'ls /tmp']

    for tgt_ip in tgt_ips:
        tgt_ssh = ssh(tgt_ip, tgt_username, tgt_password)
        for cmd in cmds:
            out = tgt_ssh.send_command(cmd)
            print 'output for cmd {0}'.format(cmd)
            print out
   
exec_cmds()

from paramiko import client
import time
import subprocess

server_ip = '192.168.101.198'
client_ips = ['192.168.101.196', '192.168.101.208', '192.168.101.206']
# client_ips = ['192.168.100.196']

#client_gids = ['4', '4', '4']
#server_gid = '4'
#client_priorities=['3', '3', '3']
#server_priority = '3'
msg_sizes = ['64', '1024', '2048']
username = 'root'
password = 'pass152'

# ib_write_bw test
server_cmd = 'ib_write_bw --report_gbits -D30 -f 2 -F -R -x 4 -S 3 '
client_cmd = 'ib_write_bw --report_gbits -D30 -f 2 -F -R -x 4 -S 3 '

# ib_read_bw test
# server_cmd = 'ib_read_bw --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '
# client_cmd = 'ib_read_bw --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '

# ib_write_lat test
# server_cmd = 'ib_write_lat --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '
# client_cmd = 'ib_write_lat --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '

# ib_read_lat test
# server_cmd = 'ib_read_lat --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '
# client_cmd = 'ib_read_lat --report_gbits -D120 -f 2 -F -R -x 4 -S 3 '

port_number = 25000

class ssh(object):
    client = None

    def __init__(self, address, username, password):
        print 'connecting to host with IP {0}'.format(address)
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


def exec_cmds():

    client_ssh_list = []
    server_ssh = ssh(server_ip, username, password)
    for client_ip in client_ips:
        client_ssh_list.append(ssh(client_ip, username, password))

    for msg_sz in msg_sizes:
        for i, client_ssh in enumerate(client_ssh_list):
            logfile = '/tmp/ib_test_{0}_{1}.out'.format(port_number+i, msg_sz)
            server_cmd1 = server_cmd+'-p {0} -s {1}'.format(port_number+i, msg_sz)
            print 'server_cmd: {0}'.format(server_cmd1)
            server_ssh.send_command('echo {0} > {1}'.format(server_cmd1, logfile))
            server_out = server_ssh.send_command(server_cmd1+' >> {0} &'.format(logfile))

            client_cmd1 = client_cmd+'{0} -p {1} -s {2}'.format(server_ip, port_number+i, msg_sz)
            print 'client_cmd: {0}'.format(client_cmd1)
            client_ssh.send_command('echo {0} > {1}'.format(client_cmd1, logfile))
            client_out = client_ssh.send_command(client_cmd1+' >> {0} &'.format(logfile))

        time.sleep(40)

        for i, client_ssh in enumerate(client_ssh_list):
            logfile = '/tmp/ib_test_{0}_{1}.out'.format(port_number+i, msg_sz)
            logout = client_ssh.send_command('cat {0}'.format(logfile))
	    subprocess.call("""echo "{0}" >> {1}""".format(logout, logfile), shell=True)

exec_cmds()

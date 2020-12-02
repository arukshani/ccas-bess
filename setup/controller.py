import sys
import os
import subprocess
import threading


def get_mac_hexstr(ip_addr):
    subprocess.check_output(f'ping -c 1 {ip_addr}', shell=True)
    # the tail is for when we have two entries due to multiple interfaces on the machine running this code
    # (e.g. the bess node)
    return subprocess.check_output(f"arp {ip_addr} | " + "awk 'NR>1 {print $3}' | tail -n 1", shell=True) \
        .decode('utf-8') \
        .replace(':', '').strip()


def main():
    if len(sys.argv) != 8:
        print("ERROR: Usage: python3 controller.py bess_left_nic_pci bess_right_nic_pci bess_left_nic_mac"
              " bess_right_nic_mac clients_left_fpath clients_right_fpath config_path")
        exit(1)

    left_nic_pci, right_nic_pci, left_nic_mac, right_nic_mac, clients_left_fpath, clients_right_fpath, \
    config_path = sys.argv[1:]
    clients_left_ip_mac = []
    clients_right_ip_mac = []
    # 1. Get the MAC address of all left clients and right clients
    with open(clients_left_fpath, "r") as f:
        print("Left clients:")
        for ip in f.readlines():
            ip = ip.strip()
            mac = get_mac_hexstr(ip)
            print(ip, mac)
            clients_left_ip_mac.append((ip, mac))
    with open(clients_right_fpath, "r") as f:
        print("Right clients:")
        for ip in f.readlines():
            ip = ip.strip()
            mac = get_mac_hexstr(ip)
            print(ip, mac)
            clients_right_ip_mac.append((ip, mac))

    bess_conf = {}
    bess_conf['left_clients'] = clients_left_ip_mac
    bess_conf['right_clients'] = clients_right_ip_mac
    bess_conf['bw_mbps'] = 10240
    bess_conf['q_size_packets'] = 16384

    bess_conf['left_nic_pci'] = left_nic_pci
    bess_conf['right_nic_pci'] = right_nic_pci
    bess_conf['left_nic_mac'] = left_nic_mac.replace(':', '')
    bess_conf['right_nic_mac'] = right_nic_mac.replace(':', '')

    with open(config_path, "w") as f:
        f.write(str(bess_conf))


if __name__ == '__main__':
    main()

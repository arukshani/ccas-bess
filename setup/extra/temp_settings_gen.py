bess_conf = {}

bess_conf['left_clients'] = [('192.168.1.1', '9cdc7156afd5')]
bess_conf['right_clients'] = [('192.168.1.11', '9cdc715d0191')]
bess_conf['bw_mbps'] = 1024
bess_conf['q_size_packets'] = 4096

bess_conf['left_nic_pci'] = '0000:03:00.1'
bess_conf['right_nic_pci'] = '0000:03:00.0'
bess_conf['left_nic_mac'] = '9cdc715d5121'
bess_conf['right_nic_mac'] = '9cdc715d5120'

print(bess_conf)
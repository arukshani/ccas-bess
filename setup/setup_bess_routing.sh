BESS_LEFT_NIC_PCI='0000:03:00.1'
BESS_RIGHT_NIC_PCI='0000:03:00.0'
BESS_LEFT_NIC_MAC='9c:dc:71:5e:2f:61'
BESS_RIGHT_NIC_MAC='9c:dc:71:5e:2f:60'
BESS_LEFT_NIC_IP='192.168.1.250'
BESS_RIGHT_NIC_IP='192.168.1.251'
CLIENTS_LEFT_FPATH="clients_left_tot"
CLIENTS_RIGHT_FPATH="clients_right_tot"
CONFIG_OP_FPATH="bess_config"
PSSH_OPTIONS="-O UserKnownHostsFile=/dev/null -O StrictHostKeyChecking=no -p 100000"
SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
#USER_NAME='aphilip'
OG_NODE_SUBNET_W_MASK='192.168.1.0/24'
NODE_IF_NAME='ens1f1'

# parallel ssh and change shell to bash
#parallel-ssh $PSSH_OPTIONS -h input_files/clients "sudo chsh -s /bin/bash $USER_NAME;"

# get IP/MAC pairs from all IPs (needs to be done before we change routes) and write config
echo "Getting IP/MAC pairs from all nodes and creating bess config"
python3 controller.py $BESS_LEFT_NIC_PCI $BESS_RIGHT_NIC_PCI  $BESS_LEFT_NIC_MAC $BESS_RIGHT_NIC_MAC $CLIENTS_LEFT_FPATH $CLIENTS_RIGHT_FPATH $CONFIG_OP_FPATH

if [ $? -ne 0 ]; then
  echo "FATAL ERROR: Exiting!"
  exit 1
fi

# Enable hugepages and disable IP forwarding on BESS node
echo "Enabling hugepages and disabling ip forwarding on BESS node"
ssh $SSH_OPTIONS $BESS_LEFT_NIC_IP "sudo sysctl vm.nr_hugepages=1024 && sudo sysctl net.ipv4.ip_forward=0"

if [ $? -ne 0 ]; then
  echo "FATAL ERROR: Exiting!"
  exit 1
fi

# Add arp entries for left and right nodes
echo "Setting up ARP entries for nodes"
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH "sudo arp -s $BESS_LEFT_NIC_IP $BESS_LEFT_NIC_MAC;"
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_RIGHT_FPATH "sudo arp -s $BESS_RIGHT_NIC_IP $BESS_RIGHT_NIC_MAC;"


if [ $? -ne 0 ]; then
  echo "FATAL ERROR: Exiting!"
  exit 1
fi

# Add route entries for left and right nodes, routing all left node packets to the left NIC and similarly for right nodes
echo "Setting up route entries for nodes"
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH "sudo ip route del $OG_NODE_SUBNET_W_MASK dev $NODE_IF_NAME && sudo ip route add $BESS_LEFT_NIC_IP/32 dev $NODE_IF_NAME && sudo ip route add $OG_NODE_SUBNET_W_MASK via $BESS_LEFT_NIC_IP dev $NODE_IF_NAME"
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_RIGHT_FPATH "sudo ip route del $OG_NODE_SUBNET_W_MASK dev $NODE_IF_NAME && sudo ip route add $BESS_RIGHT_NIC_IP/32 dev $NODE_IF_NAME && sudo ip route add $OG_NODE_SUBNET_W_MASK via $BESS_RIGHT_NIC_IP dev $NODE_IF_NAME"

if [ $? -ne 0 ]; then
  echo "FATAL ERROR: Exiting!"
  exit 1
fi
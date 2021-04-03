PSSH_OPTIONS="-O UserKnownHostsFile=/dev/null -O StrictHostKeyChecking=no -p 100000"
SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
USER_NAME='aphilip'
CLIENTS_LEFT_FPATH="clients_left_tot"
CLIENTS_RIGHT_FPATH="clients_right_tot"

# 1. Copy SSH key onto all nodes
parallel-scp $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH -h $CLIENTS_RIGHT_FPATH ~/.ssh/id_rsa ~/.ssh/id_rsa

# 2. Install iperf3 onto the nodes
# NOTE: lib32cz1 is required because of this bug (personally observed on Ubuntu 18.04): https://github.com/esnet/iperf/issues/168
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH -h $CLIENTS_RIGHT_FPATH "git clone https://github.com/adithyaphilip/iperf.git && cd iperf && ./bootstrap.sh && ./configure && make && sudo make install && sudo apt get update && sudo apt install lib32cz1"

# 3. Clone cloudlab repo and run startup.sh from it passing a parameter so it skips setting up ssh
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH -h $CLIENTS_RIGHT_FPATH -t 0 "sudo apt update && rm -rf cloudlab && git clone https://github.com/adithyaphilip/cloudlab --single-branch; cd cloudlab && bash startup.sh nosshsetup;"

# 3. Setup storage on the nodes
parallel-ssh $PSSH_OPTIONS -h $CLIENTS_LEFT_FPATH -h $CLIENTS_RIGHT_FPATH -t 0 "mkdir storage; sudo /usr/local/etc/emulab/mkextrafs.pl -f storage; sudo chown aphilip storage"

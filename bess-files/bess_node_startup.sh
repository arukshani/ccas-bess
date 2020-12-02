# setup hugefiles
sudo sysctl vm.nr_hugepages=1024
echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

# disable ip forwarding
sudo sysctl -w net.ipv4.ip_forward=0
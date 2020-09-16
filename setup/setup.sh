sudo apt update && sudo apt install -y make apt-transport-https ca-certificates g++ make pkg-config libunwind8-dev liblzma-dev zlib1g-dev libpcap-dev libssl-dev libnuma-dev git python python-pip python-scapy libgflags-dev libgoogle-glog-dev libgraph-easy-perl libgtest-dev libgrpc++-dev libprotobuf-dev libc-ares-dev libbenchmark-dev libgtest-dev protobuf-compiler-grpc linux-headers-4.15.0-48-generic libmnl-dev
pip install protobuf grpcio scapy
sudo sysctl vm.nr_hugepages=1024
echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

wget http://content.mellanox.com/ofed/MLNX_OFED-5.1-0.6.6.0/MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64.tgz
tar -xvf MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu18.04-x86_64.tgz
cd MLNX_OFED_LINUX-4.5-1.0.1.0-ubuntu18.04-x86_64
sudo ./mlnxofedinstall --force --upstream-libs --dpdk
sudo apt-get -y --fix-broken install
sudo ./mlnxofedinstall --force --upstream-libs --dpdk
sudo /etc/init.d/openibd restart

cd ..
git clone https://github.com/NetSys/bess
cd bess
./build.py

sudo shutdown -r now

sudo apt update && sudo apt install -y make apt-transport-https ca-certificates g++ make pkg-config libunwind8-dev liblzma-dev zlib1g-dev libpcap-dev libssl-dev libnuma-dev git python python-pip python-scapy libgflags-dev libgoogle-glog-dev libgraph-easy-perl libgtest-dev libgrpc++-dev libprotobuf-dev libc-ares-dev libbenchmark-dev libgtest-dev protobuf-compiler-grpc linux-headers-4.15.0-48-generic libmnl-dev
pip install protobuf grpcio scapy
sudo sysctl vm.nr_hugepages=1024

rm -rf MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64.tgz MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64
wget http://content.mellanox.com/ofed/MLNX_OFED-5.1-0.6.6.0/MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64.tgz
tar -xvf MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64.tgz
cd MLNX_OFED_LINUX-5.1-0.6.6.0-ubuntu18.04-x86_64
sudo ./mlnxofedinstall --force --upstream-libs --dpdk
sudo apt-get -y --fix-broken install
sudo ./mlnxofedinstall --force --upstream-libs --dpdk
sudo /etc/init.d/openibd restart

cd ..
git clone https://github.com/adithyaphilip/bess
rm bess/core/modules/queue.cc
rm bess/core/modules/queue.h
ln -s $(pwd)/queue.cc bess/core/modules/
ln -s $(pwd)/queue.h bess/core/modules/
ln -s $(pwd)/ccas-router.bess bess/bessctl/conf/samples/
cd bess
./build.py

cd ..

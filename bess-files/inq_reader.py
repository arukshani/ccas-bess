import struct


def read_binary_inq_log(path: str):
    '''
    Reads a binary log of packets in flight at different times for different flows
    :return:
    '''
    bytes_read = 0
    with open(path, "rb") as f:
        while True:
            time_bytes = f.read(4)
            if time_bytes == b'':
                break
            time_ms = struct.unpack('<I', time_bytes)[0]
            ip_last = struct.unpack('B', f.read(1))[0]
            port = struct.unpack('>H', f.read(2))[0]
            inq = struct.unpack('<I', f.read(4))[0]
            bytes_read += 11

            print(time_ms, ip_last, port, inq)
    pass


def main():
    read_binary_inq_log('/users/aphilip/in-q.log')


if __name__ == '__main__':
    main()

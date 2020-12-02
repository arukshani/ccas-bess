import struct
import sys
import numpy as np
import plotly.graph_objects as go

import os

from typing import List


def plot_queue_drops_time(drop_tstamps: List, log_name: str, rtt1: int, rtt2: int, colored: bool):
    fh_last_ip = 5

    if not colored:
        drop_tstamps = np.unique([tstamp for tstamp, _, _ in drop_tstamps])
        fig_drops = go.Figure(data=
                              go.Scatter(x=drop_tstamps - drop_tstamps[0], y=[1] * len(drop_tstamps), mode='markers')
                              )
        fig_drops.update_layout(
            title=f"Queue Drops Over Time: {log_name}, {rtt1}ms vs {rtt2}ms",
            xaxis=dict(
                title="Time (micro s)"
            ),
            yaxis=dict(
                title="Drop Occurred (Boolean)",
                range=[0, 1]
            )
        )
        fig_drops.write_html("C://projects/ccas-bess/temp/q_drops_time.html")
        fig_drops.show()
    else:
        min_tstamp = drop_tstamps[0][0]
        tstamps_fh = np.array([tstamp for tstamp, ip, _ in drop_tstamps if ip <= fh_last_ip])
        tstamps_sh = np.array([tstamp for tstamp, ip, _ in drop_tstamps if ip > fh_last_ip])
        traces = []
        traces.append(go.Scatter(x=tstamps_fh - min_tstamp, y=[1] * len(tstamps_fh), mode='markers',
                                 name=f'{rtt1}ms Drops'))
        traces.append(go.Scatter(x=tstamps_sh - min_tstamp, y=[0.99] * len(tstamps_sh), mode='markers',
                                 name=f'{rtt2}ms Drops'))
        fig = go.Figure(data=go.Data(traces))
        fig.update_layout(
            title=f"Queue Drops Over Time: {log_name}, {rtt1}ms vs {rtt2}ms",
            xaxis=dict(
                title="Time (micro s)"
            ),
            yaxis=dict(
                title="Drop Occurred",
                range=[0, 2]
            )
        )
        fig.write_html("C://projects/ccas-bess/temp/q_drops_time_colored.html")
        fig.show()


def plot_queue_drops_intertimes(drop_tstamps: np.array, log_name: str, rtt1: int, rtt2: int, diff_thresh_micro: int):
    diff_tstamps = np.diff(drop_tstamps)
    larger_diffs = diff_tstamps[diff_tstamps > diff_thresh_micro]

    percentiles = list(range(1, 101))
    x = [np.percentile(larger_diffs, percentile) for percentile in percentiles]

    fig_cdf = go.Figure(data=
                        go.Scatter(x=x,
                                   y=percentiles)
                        )
    fig_cdf.update_layout(
        title=f"CDF of Queue Drop Inter-Times: {log_name}, {rtt1}ms vs {rtt2}ms",
        xaxis=dict(
            title="Drop Intertime (micro s)"
        ),
        yaxis=dict(
            title="Percentile",
            range=[0, 100]
        )
    )
    fig_cdf.write_html("C://projects/ccas-bess/temp/q_overall_cdf.html")
    fig_cdf.show()


def plot_drop_intertimes(intertimes_fh: List, intertimes_sh: List, title_suffix: str, rtt1: int, rtt2: int):
    traces_cdf = []
    traces_cdf.append(go.Scatter(x=[np.percentile(intertimes_fh, perc) for perc in range(1, 101)],
                                 y=np.array(range(1, 101)),
                                 name=f'{rtt1}ms flows'))
    traces_cdf.append(
        go.Scatter(x=[np.percentile(intertimes_sh, perc) for perc in range(1, 101)],
                   y=np.array(range(1, 101)),
                   name=f'{rtt2}ms flows'))

    fig_cdf = go.Figure(data=go.Data(traces_cdf))
    fig_cdf.update_layout(
        title=f"Inter-Drop Time CDF: {title_suffix}, {rtt1}ms vs {rtt2}ms",
        xaxis=dict(
            title="Inter-Drop Time (micro s)"
        ),
        yaxis=dict(
            title="Percentile Of Drops",
            range=[0, 100]
        )
    )
    fig_cdf.write_html("C://projects/ccas-bess/temp/bw_cdf_plot.html")
    fig_cdf.show()


def get_drop_intertimes(ip_port_tstamp: dict, half_level: bool):
    fh_last_ip = 5

    intertimes_fh = []
    intertimes_sh = []

    fh_tstamps = []  # only used for half level intertimes
    sh_tstamps = []
    for key, tstamps in ip_port_tstamp.items():
        if half_level:
            ip, port = key
            if ip <= fh_last_ip:
                fh_tstamps.extend(tstamps)
            else:
                sh_tstamps.extend(tstamps)
        else:
            intertimes = np.diff(tstamps)
            if key[0] <= fh_last_ip:
                intertimes_fh.extend(intertimes)  # convert to ms
            else:
                intertimes_sh.extend(intertimes)

    if half_level:
        return np.diff(sorted(fh_tstamps)), np.diff(sorted(sh_tstamps))
    else:
        return intertimes_fh, intertimes_sh


def read_flow_tstamps(log_path: str, return_dict: bool):
    all_ports = set()
    all_ips = set()
    min_timestamp = 2 ** 32
    max_timestamp = 0

    ip_port_tstamp = {}
    tstamps = []
    with open(log_path, "rb") as f:
        tot_size = os.fstat(f.fileno()).st_size
        read_size = 0
        ctr = 0
        while True:
            timestamp = f.read(4)
            ip = f.read(1)
            port = f.read(2)
            if len(timestamp) == 0:
                break
            read_size += 7

            timestamp = struct.unpack('<I', timestamp)[0]
            min_timestamp = min(min_timestamp, timestamp)
            max_timestamp = max(max_timestamp, timestamp)

            # if read_size / tot_size < 0.9994:
            if timestamp - min_timestamp < 700 * 1000 * 1000:
                continue
            # if timestamp - min_timestamp > 800 * 1000 * 1000 + 500 * 1000:
            #     break
            ip, port = struct.unpack('>B H', ip + port)
            all_ports.add(port)
            all_ips.add(ip)
            ctr += 1
            if ctr % 1000000 == 0:
                print(read_size / tot_size * 100)

            if return_dict:
                key = (ip, port)
                if key not in ip_port_tstamp:
                    ip_port_tstamp[key] = [timestamp]
                else:
                    ip_port_tstamp[key].append(timestamp)
            else:
                tstamps.append((timestamp, ip, port))
            # print(timestamp, ip, port)
    print(ctr)
    # print(list(sorted(all_ports)))
    print(len(all_ports))
    print(list(sorted(all_ips)))
    print(min_timestamp, max_timestamp)

    for key, value in ip_port_tstamp.items():
        ip_port_tstamp[key] = np.asarray(value)

    return ip_port_tstamp if return_dict else tstamps


def main():
    log_name = 'bess-drop-2k-5Gbps'
    rtt1 = 10
    rtt2 = 16
    ip_port_tstamp = read_flow_tstamps(f"../../{log_name}.log", True)
    intertimes_fh, intertimes_sh = get_drop_intertimes(ip_port_tstamp, half_level=True)
    plot_drop_intertimes(intertimes_fh, intertimes_sh, log_name, rtt1, rtt2)

    # plot queue drops over time
    # plot_queue_drops_time(read_flow_tstamps(f"../../{log_name}.log", False), log_name, rtt1, rtt2, True)
    # plot_queue_drops_intertimes(read_flow_tstamps(f"../../{log_name}.log", False), log_name, rtt1, rtt2, 10 * 1000)


if __name__ == '__main__':
    main()

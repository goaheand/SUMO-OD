import xml.etree.cElementTree as eT
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import sys
import subprocess
from time import sleep
from sumolib import checkBinary


SUMO_HOME = os.environ.get('SUMO_HOME')
assert SUMO_HOME is not None, "There is no path SUMO_HOME."

sys.path.append(os.path.join(SUMO_HOME, 'tools'))


def generate_xml():
    """生成od.trips.xml,并运行sumo得到仿真结果，生成检测数据od.out.xml和tripinfo.out.xml"""
    od2trips = checkBinary('od2trips')
    options = [od2trips, '-n', 'taz.net.xml', '-d', 'od.mat.xml', '-o', 'od.trips.xml',
               '--timeline.day-in-hours', '--timeline']
    timeline = generate_timeline()
    timeline_str = list(map(lambda x: '{:.1f}'.format(x), timeline))
    timeline = ','.join(timeline_str)
    options.append(timeline)
    subprocess.call(options, cwd='net')  # 生成od.trips.xml
    sleep(1)
    sumo = checkBinary('sumo')
    options = [sumo, '-c', 'od.sumocfg', '--ignore-route-errors', '--tripinfo-output', 'tripinfo.out.xml']
    subprocess.call(options, cwd='net/net1')  # 运行sumo
    subprocess.call(options, cwd='net/net2')


def generate_timeline():
    """车辆生成概率随时间的分布"""
    mu1, std1 = 8, 3.5
    mu2, std2 = 18, 3
    data = gauss_func(mu1, std1) + 0.9 * gauss_func(mu2, std2)
    data = data * 5
    # plt.plot(data)
    # plt.show()
    return data


def gauss_func(mu, std):
    x = np.linspace(1, 24, 24)
    return np.exp(-0.5 * ((x - mu) / std) ** 2)


def get_flow_from_xml(file_path):
    """
    得到不同edge的flow列表.
    :param file_path: the path of det.add.xml
    :return: flow_dict[edge_name] = flow_list
             time_line: the time moment corresponding to the flow_list
    """
    time_line = [0]  # 时间序列
    time_index = -1
    flow_dict = {}  # 不同edges的flow序列，key为edge，value为序列
    out_tree = eT.ElementTree(file=file_path)
    root = out_tree.getroot()
    for elem in root:
        elem_data = elem.attrib
        time_end = float(elem_data['end']) / 3600
        edge = get_edge(elem_data['id'])
        flow = float(elem_data['flow'])

        if time_line[-1] != time_end:
            time_line.append(time_end)
            time_index += 1

        try:
            flow_dict[edge][time_index] += flow
        except KeyError:
            flow_dict[edge] = [flow]
        except IndexError:
            flow_dict[edge].append(flow)

    return flow_dict, time_line[1:]


def get_edge(det_id):
    id_pattern = re.compile(r'(\w+_\d+)_\d+')
    p = re.match(id_pattern, det_id).group(1)
    return p


def plot_flow_all_edges(flow_dict, time_line, save_dir, interval):
    """
    多路口曲线绘制.
    :param flow_dict: 由get_flow_from_xml得到的flow_dict
    :param time_line: 每个flow对应的时间，即时间线列表
    :param save_dir: 图片保存路径
    :param interval: 合并flow点，每个flow对应5min.
    :return:
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    edges = list(flow_dict.keys())
    directions = ['east_', 'south_', 'west_', 'north_']
    tmp = int(np.sqrt(len(edges) // 4))

    new_time_line = [time_line[i] for i in range(0, len(time_line), interval)]
    for i in range(tmp):
        for j in range(tmp):
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            for (k, direction) in enumerate(directions):
                x, y = k // 2, k % 2
                edge_name = direction + '{}{}'.format(i, j)
                edge_flow = merge_interval(flow_dict[edge_name], interval)
                axes[x, y].set_title('traffic flow of edge {}'.format(edge_name))
                axes[x, y].set_xlabel('time/h')
                axes[x, y].set_ylabel('flow')
                axes[x, y].set_xticks(range(0, 25, 4))
                axes[x, y].plot(new_time_line, edge_flow)
            plt.savefig(os.path.join(save_dir, '{}{}.png'.format(i, j)))


def merge_interval(flow_list, interval):
    """一个interval为5min"""
    new_flow_list = []
    for i in range(0, len(flow_list), interval):
        new_flow_list.append(sum(flow_list[i: i + interval]))
    return new_flow_list


def modify_factor(factor):
    with open('net/od.mat.xml', 'r') as f:
        lines = f.readlines()
    pre_line, cur_line = '', ''
    with open('net/od.mat.xml', 'w') as f:
        for line in lines:
            pre_line = cur_line
            cur_line = line
            if 'Factor' in pre_line:
                f.write('{:.2f}\n'.format(factor))
                continue
            f.write(line)


if __name__ == '__main__':
    generate_xml()
    sleep(1)
    d, t = get_flow_from_xml('net/net1/od.out.xml')
    plot_flow_all_edges(d, t, 'curves1', 4)
    d, t = get_flow_from_xml('net/net2/od.out.xml')
    plot_flow_all_edges(d, t, 'curves2', 4)

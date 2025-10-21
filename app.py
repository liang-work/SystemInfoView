#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息监控后端服务
提供系统信息和性能资源的API接口
"""

from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import platform
import os
import time
from datetime import datetime

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域资源共享

# 网络流量历史数据，用于计算速率
network_history = {
    'bytes_recv': 0,
    'bytes_sent': 0,
    'timestamp': 0
}

def get_system_info():
    """
    获取系统基本信息
    """
    try:
        import sys

        hostname = platform.node()
        system = platform.system()
        release = platform.release()
        version = platform.version()
        arch = platform.architecture()[0]
        machine = platform.machine()
        processor = platform.processor()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        total_memory = psutil.virtual_memory().total / (1024**3)  # 转换为GB
        uptime = time.time() - psutil.boot_time()
        load_average = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]

        # 获取CPU频率信息
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_freq_current = cpu_freq.current if cpu_freq and cpu_freq.current else 0
            cpu_freq_min = cpu_freq.min if cpu_freq and cpu_freq.min else 0
            cpu_freq_max = cpu_freq.max if cpu_freq and cpu_freq.max else 0
        except:
            cpu_freq_current = cpu_freq_min = cpu_freq_max = 0

        # 获取系统时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "hostname": hostname,
            "platform": system,
            "release": release,
            "version": version,
            "arch": arch,
            "machine": machine,
            "processor": processor,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "cpu_count": cpu_count,
            "cpu_count_physical": cpu_count_physical,
            "cpu_freq_current": round(cpu_freq_current, 2),
            "cpu_freq_min": round(cpu_freq_min, 2),
            "cpu_freq_max": round(cpu_freq_max, 2),
            "total_memory": round(total_memory, 2),
            "uptime": int(uptime),
            "load_average": [round(avg, 2) for avg in load_average],
            "current_time": current_time,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"获取系统信息时出错: {e}")
        return None

def get_performance_resources():
    """
    获取系统性能资源信息
    """
    try:
        # CPU使用率和频率
        try:
            cpu_usage = psutil.cpu_percent(interval=0.5)  # 减少间隔以适应2秒刷新
            cpu_freq = psutil.cpu_freq()
            cpu_freq_current = cpu_freq.current if cpu_freq and cpu_freq.current else 0
        except:
            cpu_usage = 0
            cpu_freq_current = 0

        # CPU每个核心使用率
        try:
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        except:
            cpu_per_core = []

        # 内存信息
        try:
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_used = memory.used / (1024**3)  # 转换为GB
            memory_available = memory.available / (1024**3)  # 转换为GB
            memory_free = memory.free / (1024**3)  # 转换为GB
        except:
            memory_usage = memory_used = memory_available = memory_free = 0

        # 交换内存信息
        try:
            swap = psutil.swap_memory()
            swap_usage = swap.percent
            swap_used = swap.used / (1024**3)  # 转换为GB
            swap_total = swap.total / (1024**3)  # 转换为GB
        except:
            swap_usage = swap_used = swap_total = 0

        # 磁盘信息 - 获取所有磁盘
        all_disks = []
        disk_usage = disk_used = disk_total = 0
        try:
            # 获取所有磁盘分区
            partitions = psutil.disk_partitions(all=True)

            for partition in partitions:
                try:
                    if partition.device and partition.mountpoint:
                        partition_disk_usage = psutil.disk_usage(partition.mountpoint)
                        if partition_disk_usage.total > 0:
                            all_disks.append({
                                'device': partition.device,
                                'mountpoint': partition.mountpoint,
                                'filesystem': partition.fstype,
                                'total': round(partition_disk_usage.total / (1024**3), 2),  # GB
                                'used': round(partition_disk_usage.used / (1024**3), 2),    # GB
                                'free': round(partition_disk_usage.free / (1024**3), 2),    # GB
                                'usage_percent': round(partition_disk_usage.percent, 2)     # 百分比
                            })

                            # 使用第一个磁盘作为默认显示
                            if not all_disks:
                                disk_usage = partition_disk_usage.percent
                                disk_used = partition_disk_usage.used / (1024**3)
                                disk_total = partition_disk_usage.total / (1024**3)
                except:
                    continue

            # 如果没有获取到任何磁盘，使用根目录作为默认
            if not all_disks:
                try:
                    disk = psutil.disk_usage('/')
                    if disk.total > 0:
                        all_disks.append({
                            'device': '/',
                            'mountpoint': '/',
                            'filesystem': 'unknown',
                            'total': round(disk.total / (1024**3), 2),
                            'used': round(disk.used / (1024**3), 2),
                            'free': round(disk.free / (1024**3), 2),
                            'usage_percent': round(disk.percent, 2)
                        })
                        disk_usage = disk.percent
                        disk_used = disk.used / (1024**3)
                        disk_total = disk.total / (1024**3)
                except:
                    pass
        except:
            all_disks = []
            disk_usage = disk_used = disk_total = 0

        # 磁盘IO信息
        disk_read_rate = disk_write_rate = disk_read_count = disk_write_count = 0
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_read_rate = disk_io.read_bytes / (1024 * 1024) if disk_io.read_bytes else 0  # MB/s
                disk_write_rate = disk_io.write_bytes / (1024 * 1024) if disk_io.write_bytes else 0  # MB/s
                disk_read_count = disk_io.read_count if disk_io.read_count else 0
                disk_write_count = disk_io.write_count if disk_io.write_count else 0
        except:
            pass

        # 网络信息和速率计算
        network_rx = network_tx = network_packets_rx = network_packets_tx = 0
        network_err_in = network_err_out = 0
        try:
            network = psutil.net_io_counters()
            if network:
                current_time = time.time()
                current_bytes_recv = network.bytes_recv
                current_bytes_sent = network.bytes_sent

                # 计算网络速率 (KB/s)
                if network_history['timestamp'] > 0:
                    time_diff = current_time - network_history['timestamp']
                    if time_diff > 0:
                        bytes_recv_diff = current_bytes_recv - network_history['bytes_recv']
                        bytes_sent_diff = current_bytes_sent - network_history['bytes_sent']
                        network_rx = (bytes_recv_diff / time_diff) / 1024  # KB/s
                        network_tx = (bytes_sent_diff / time_diff) / 1024  # KB/s
                    else:
                        network_rx = network_tx = 0
                else:
                    # 首次运行时，只记录数据，不计算速率
                    network_rx = network_tx = 0

                # 更新历史数据
                network_history['bytes_recv'] = current_bytes_recv
                network_history['bytes_sent'] = current_bytes_sent
                network_history['timestamp'] = current_time

                network_packets_rx = network.packets_recv if network.packets_recv else 0
                network_packets_tx = network.packets_sent if network.packets_sent else 0
                network_err_in = network.errin if network.errin else 0
                network_err_out = network.errout if network.errout else 0
        except:
            pass

        # 进程信息
        try:
            process_count = len(psutil.pids())
        except:
            process_count = 0

        return {
            # CPU信息
            "cpu_usage": cpu_usage / 100.0 if cpu_usage else 0,
            "cpu_freq_current": round(cpu_freq_current, 2),
            "cpu_per_core": [round(usage / 100.0, 3) for usage in cpu_per_core] if cpu_per_core else [],

            # 内存信息
            "memory_usage": memory_usage / 100.0 if memory_usage else 0,
            "memory_used": round(memory_used, 2),
            "memory_available": round(memory_available, 2),
            "memory_free": round(memory_free, 2),

            # 交换内存信息
            "swap_usage": swap_usage / 100.0 if swap_usage else 0,
            "swap_used": round(swap_used, 2),
            "swap_total": round(swap_total, 2),

            # 磁盘信息
            "disk_usage": disk_usage / 100.0 if disk_usage else 0,
            "disk_used": round(disk_used, 2),
            "disk_total": round(disk_total, 2),
            "disk_read_rate": round(disk_read_rate, 2),
            "disk_write_rate": round(disk_write_rate, 2),
            "disk_read_count": disk_read_count,
            "disk_write_count": disk_write_count,

            # 网络信息
            "network_rx": round(network_rx, 2),
            "network_tx": round(network_tx, 2),
            "network_packets_rx": network_packets_rx,
            "network_packets_tx": network_packets_tx,
            "network_err_in": network_err_in,
            "network_err_out": network_err_out,

            # 进程信息
            "process_count": process_count,

            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"获取性能资源信息时出错: {e}")
        return None

@app.route('/api/system/info', methods=['GET'])
def api_system_info():
    """
    获取系统基本信息的API接口
    """
    try:
        system_info = get_system_info()
        if system_info is None:
            return jsonify({
                "error": "无法获取系统信息",
                "message": "系统信息获取失败，请检查系统权限或稍后重试"
            }), 500

        return jsonify(system_info)
    except Exception as e:
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e)
        }), 500

@app.route('/api/performance/resources', methods=['GET'])
def api_performance_resources():
    """
    获取系统性能资源信息的API接口
    """
    try:
        performance_info = get_performance_resources()
        if performance_info is None:
            return jsonify({
                "error": "无法获取性能资源信息",
                "message": "性能资源信息获取失败，请检查系统权限或稍后重试"
            }), 500

        return jsonify(performance_info)
    except Exception as e:
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e)
        }), 500

@app.route('/api/disks/all', methods=['GET'])
def api_all_disks():
    """
    获取所有磁盘信息的API接口
    """
    try:
        # 获取所有磁盘分区
        partitions = psutil.disk_partitions(all=True)
        all_disks = []

        for partition in partitions:
            try:
                if partition.device and partition.mountpoint:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    if disk_usage.total > 0:
                        all_disks.append({
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'filesystem': partition.fstype,
                            'total': round(disk_usage.total / (1024**3), 2),  # GB
                            'used': round(disk_usage.used / (1024**3), 2),    # GB
                            'free': round(disk_usage.free / (1024**3), 2),    # GB
                            'usage_percent': round(disk_usage.percent, 2)     # 百分比
                        })
            except:
                continue

        return jsonify({
            'disks': all_disks,
            'count': len(all_disks),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "无法获取磁盘信息",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SystemInfoView Backend"
    })

@app.route('/', methods=['GET'])
def index():
    """
    根路径，重定向到健康检查
    """
    return jsonify({
        "message": "SystemInfoView Backend API",
        "version": "1.0.0",
        "endpoints": {
            "system_info": "/api/system/info",
            "performance_resources": "/api/performance/resources",
            "health": "/health"
        }
    })

if __name__ == '__main__':
    print("🚀 启动系统信息监控后端服务...")
    print("📊 API文档:")
    print("   GET /api/system/info - 获取系统基本信息")
    print("   GET /api/performance/resources - 获取性能资源信息")
    print("   GET /health - 健康检查")
    print("   GET / - API信息")
    print("🔗 前端访问地址: http://localhost:3000")

    app.run(
        host='0.0.0.0',
        port=3000,
        debug=True
    )

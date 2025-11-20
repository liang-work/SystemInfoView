from PySystemInfo import CPU, Memory, Disk, Network, Sensor, SystemConst, GPU
import flask
import os
import platform
import psutil
import time
from datetime import datetime
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'web/')
static_dir = os.path.join(BASE_DIR, 'web/')
app = flask.Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# 全局变量用于存储网络IO计数器的上一次值
last_net_io = None
last_net_time = None

# 全局变量用于存储磁盘IO计数器的上一次值
last_disk_io = None
last_disk_time = None

def get_cpu_info():
    """获取CPU信息"""
    try:
        # 获取CPU使用率
        cpu_usage = CPU.GetCPUUtilization(InterruptsTime=1, EveryCore=False)
        if isinstance(cpu_usage, list):
            cpu_usage = sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0
        
        # 获取CPU频率
        cpu_freq = CPU.GetCPUFrequency(AllCPU=False)
        if isinstance(cpu_freq, list) and cpu_freq:
            cpu_freq = cpu_freq[0].current if hasattr(cpu_freq[0], 'current') else cpu_freq[0]
        elif hasattr(cpu_freq, 'current'):
            cpu_freq = cpu_freq.current
        else:
            cpu_freq = 0
        
        # 获取CPU核心数
        cpu_cores = CPU.GetCPUCoreCount()
        if cpu_cores:
            cpu_cores = len(cpu_cores)
        else:
            cpu_cores = psutil.cpu_count(logical=False) or 1
        
        # 获取CPU温度（如果有传感器）
        cpu_temp = None
        try:
            temps = Sensor.GetTemperature()
            if temps and 'coretemp' in temps:
                core_temps = temps['coretemp']
                if core_temps:
                    cpu_temp = core_temps[0].current if hasattr(core_temps[0], 'current') else core_temps[0]
        except:
            cpu_temp = None
        
        return {
            "usage": round(float(cpu_usage), 1),
            "frequency": round(float(cpu_freq), 1) if cpu_freq else 0,
            "cores": cpu_cores,
            "temperature": round(float(cpu_temp), 1) if cpu_temp else None
        }
    except Exception as e:
        print(f"获取CPU信息失败: {e}")
        return {"error": str(e)}

def get_memory_info():
    """获取内存信息"""
    try:
        memory = Memory.GetRunMemory()
        
        # 计算内存使用率
        memory_usage = (memory.used / memory.total) * 100 if memory.total > 0 else 0
        
        return {
            "usage": round(float(memory_usage), 1),
            "used": memory.used,
            "available": memory.available,
            "total": memory.total
        }
    except Exception as e:
        print(f"获取内存信息失败: {e}")
        return {"error": str(e)}

def get_disk_info():
    """获取磁盘信息"""
    global last_disk_io, last_disk_time

    try:
        partitions = Disk.GetDiskMount(all=False)
        disk_info = []

        # 获取磁盘IO信息
        current_disk_io = psutil.disk_io_counters(perdisk=False)
        current_time = time.time()

        disk_read_speed = 0
        disk_write_speed = 0

        if last_disk_io and last_disk_time:
            time_diff = current_time - last_disk_time
            if time_diff > 0:
                disk_read_speed = (current_disk_io.read_bytes - last_disk_io.read_bytes) / time_diff
                disk_write_speed = (current_disk_io.write_bytes - last_disk_io.write_bytes) / time_diff

        # 更新全局变量
        last_disk_io = current_disk_io
        last_disk_time = current_time

        for partition in partitions:
            try:
                # 处理Windows路径问题
                mountpoint = partition.mountpoint
                # 如果是Windows路径，确保路径格式正确
                if ':' in mountpoint and '\\' in mountpoint:
                    # 使用原始字符串格式避免转义问题
                    mountpoint = mountpoint.replace('\\', '/')

                usage = Disk.GetDiskUsage(mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "usage": round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0,
                    "used": usage.used,
                    "free": usage.free,
                    "total": usage.total
                })
            except Exception as e:
                # 安全地处理设备名称显示
                device_name = str(partition.device).replace('\\', '\\\\')
                continue

        return {
            "partitions": disk_info,
            "io": {
                "read_speed": round(float(disk_read_speed), 1),
                "write_speed": round(float(disk_write_speed), 1)
            }
        }
    except Exception as e:
        print(f"获取磁盘信息失败: {e}")
        return {"error": str(e)}

def get_network_info():
    """获取网络信息"""
    global last_net_io, last_net_time
    
    try:
        current_net_io = Network.GetNetworkIO(Pernic=False)
        current_time = time.time()
        
        upload_speed = 0
        download_speed = 0
        
        if last_net_io and last_net_time:
            time_diff = current_time - last_net_time
            if time_diff > 0:
                upload_speed = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_diff
                download_speed = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_diff
        
        # 更新全局变量
        last_net_io = current_net_io
        last_net_time = current_time
        
        # 获取网络连接数
        connections = len(Network.GetNetworkStats(Pernic='all'))
        
        return {
            "upload": round(float(upload_speed), 1),
            "download": round(float(download_speed), 1),
            "connections": connections
        }
    except Exception as e:
        print(f"获取网络信息失败: {e}")
        return {"error": str(e)}

def get_system_info():
    """获取系统信息"""
    try:
        # 获取系统启动时间
        boot_time = psutil.boot_time()

        # 计算系统运行时间
        uptime = time.time() - boot_time

        # 获取进程数
        processes = len(psutil.pids())

        return {
            "boot_time": boot_time,
            "uptime": uptime,
            "processes": processes
        }
    except Exception as e:
        print(f"获取系统信息失败: {e}")
        return {"error": str(e)}

def get_gpu_info():
    """获取GPU信息"""
    try:
        gpu_data = GPU.GetGPUInfo()
        if not gpu_data:
            return {"gpus": []}

        # 格式化GPU数据，只包含成功获取的信息
        formatted_gpus = []
        for gpu in gpu_data:
            gpu_info = {"id": gpu.get('id'), "name": gpu.get('name')}

            # 只添加成功获取的性能信息
            if 'load' in gpu and gpu['load'] is not None:
                gpu_info['load'] = round(float(gpu['load']), 1)
            if 'memory_used' in gpu and gpu['memory_used'] is not None:
                gpu_info['memory_used'] = gpu['memory_used']
            if 'memory_total' in gpu and gpu['memory_total'] is not None:
                gpu_info['memory_total'] = gpu['memory_total']
            if 'memory_free' in gpu and gpu['memory_free'] is not None:
                gpu_info['memory_free'] = gpu['memory_free']
            if 'memory_util' in gpu and gpu['memory_util'] is not None:
                gpu_info['memory_util'] = round(float(gpu['memory_util']), 1)
            if 'temperature' in gpu and gpu['temperature'] is not None:
                gpu_info['temperature'] = round(float(gpu['temperature']), 1)

            formatted_gpus.append(gpu_info)

        return {"gpus": formatted_gpus}
    except Exception as e:
        print(f"获取GPU信息失败: {e}")
        return {"gpus": []}

@app.route('/')
def index():
    """主页路由"""
    return flask.render_template('index.html')

@app.route('/api/system-info')
def system_info():
    """系统信息API接口"""
    try:
        # 并行获取所有系统信息
        cpu_data = get_cpu_info()
        memory_data = get_memory_info()
        disk_data = get_disk_info()
        network_data = get_network_info()
        system_data = get_system_info()
        gpu_data = get_gpu_info()

        # 组合所有数据
        response_data = {
            "cpu": cpu_data,
            "memory": memory_data,
            "disk": disk_data,
            "network": network_data,
            "system": system_data,
            "gpu": gpu_data,
            "timestamp": datetime.now().isoformat()
        }

        return flask.jsonify(response_data)

    except Exception as e:
        print(f"系统信息API错误: {e}")
        return flask.jsonify({"error": f"获取系统信息失败: {str(e)}"}), 500

@app.route('/api/cpu')
def cpu_info():
    """单独的CPU信息API"""
    try:
        return flask.jsonify(get_cpu_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/memory')
def memory_info():
    """单独的内存信息API"""
    try:
        return flask.jsonify(get_memory_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/disk')
def disk_info():
    """单独的磁盘信息API"""
    try:
        return flask.jsonify(get_disk_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/network')
def network_info():
    """单独的网络信息API"""
    try:
        return flask.jsonify(get_network_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/system')
def system_basic_info():
    """单独的系统基本信息API"""
    try:
        return flask.jsonify(get_system_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/gpu')
def gpu_info():
    """单独的GPU信息API"""
    try:
        return flask.jsonify(get_gpu_info())
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/cpu/detailed')
def cpu_detailed_info():
    """CPU详细信息API"""
    try:
        import psutil
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_per_core": psutil.cpu_percent(percpu=True, interval=1),
            "frequency": psutil.cpu_freq(percpu=True) if psutil.cpu_freq() else None,
            "stats": psutil.cpu_stats()._asdict() if psutil.cpu_stats() else None,
            "times": psutil.cpu_times(percpu=True) if psutil.cpu_times(percpu=True) else None
        }
        return flask.jsonify(cpu_info)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/memory/detailed')
def memory_detailed_info():
    """内存详细信息API"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        memory_info = {
            "virtual_memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent,
                "active": getattr(memory, 'active', None),
                "inactive": getattr(memory, 'inactive', None),
                "buffers": getattr(memory, 'buffers', None),
                "cached": getattr(memory, 'cached', None),
                "shared": getattr(memory, 'shared', None),
                "slab": getattr(memory, 'slab', None)
            },
            "swap_memory": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": swap.sin,
                "sout": swap.sout
            }
        }
        return flask.jsonify(memory_info)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/disk/detailed')
def disk_detailed_info():
    """磁盘详细信息API"""
    try:
        import psutil
        partitions = psutil.disk_partitions(all=False)
        disk_info = []

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "usage": {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                })
            except Exception as e:
                continue

        # IO统计信息
        io_counters = psutil.disk_io_counters(perdisk=True)
        io_stats = {}
        if io_counters:
            for disk, stats in io_counters.items():
                io_stats[disk] = {
                    "read_count": stats.read_count,
                    "write_count": stats.write_count,
                    "read_bytes": stats.read_bytes,
                    "write_bytes": stats.write_bytes,
                    "read_time": stats.read_time,
                    "write_time": stats.write_time,
                    "busy_time": getattr(stats, 'busy_time', None)
                }

        return flask.jsonify({
            "partitions": disk_info,
            "io_stats": io_stats
        })
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/network/detailed')
def network_detailed_info():
    """网络详细信息API"""
    try:
        import psutil
        network_info = {
            "interfaces": psutil.net_if_addrs(),
            "stats": psutil.net_if_stats(),
            "io_counters": psutil.net_io_counters(pernic=True) if psutil.net_io_counters(pernic=True) else {},
            "connections": [conn._asdict() for conn in psutil.net_connections(kind='inet')]
        }
        return flask.jsonify(network_info)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/gpu/detailed')
def gpu_detailed_info():
    """GPU详细信息API"""
    try:
        gpu_data = GPU.GetGPUInfo()
        if not gpu_data:
            return flask.jsonify({"gpus": []})

        detailed_gpus = []
        for gpu in gpu_data:
            gpu_detail = {
                "id": gpu.get('id'),
                "name": gpu.get('name'),
                "load": gpu.get('load'),
                "memory_used": gpu.get('memory_used'),
                "memory_total": gpu.get('memory_total'),
                "memory_free": gpu.get('memory_free'),
                "memory_util": gpu.get('memory_util'),
                "temperature": gpu.get('temperature')
            }
            detailed_gpus.append(gpu_detail)

        return flask.jsonify({"gpus": detailed_gpus})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/system/detailed')
def system_detailed_info():
    """系统详细信息API"""
    try:
        import psutil
        import platform

        system_info = {
            "platform": {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "boot_time": psutil.boot_time(),
            "users": [user._asdict() for user in psutil.users()],
            "pids": psutil.pids(),
            "process_count": len(psutil.pids())
        }
        return flask.jsonify(system_info)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return flask.jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    # 初始化网络监控
    last_net_io = Network.GetNetworkIO(Pernic=False)
    last_net_time = time.time()

    # 初始化磁盘IO监控
    last_disk_io = psutil.disk_io_counters(perdisk=False)
    last_disk_time = time.time()
    
    '''print("系统信息监控服务启动中...")
    print("访问地址: http://localhost:5000")
    print("API文档:")
    print("  - 主页: http://localhost:5000")
    print("  - 完整系统信息: http://localhost:5000/api/system-info")
    print("  - CPU信息: http://localhost:5000/api/cpu")
    print("  - 内存信息: http://localhost:5000/api/memory")
    print("  - 磁盘信息: http://localhost:5000/api/disk")
    print("  - 网络信息: http://localhost:5000/api/network")
    print("  - 系统信息: http://localhost:5000/api/system")
    print("  - 健康检查: http://localhost:5000/health")
    '''
    app.run(debug=True, host='0.0.0.0', port=5000)

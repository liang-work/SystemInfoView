import psutil
import os

def GetDiskMount(all: bool = False):
    """Get disk mount points"""
    return psutil.disk_partitions(all=all)

def GetDiskUsage(Path: str = '/'):
    """Get disk usage"""
    # 处理Windows路径的特殊情况
    if os.name == 'nt':  # Windows系统
        # 确保路径格式正确
        if ':' in Path and '\\' in Path:
            # 将反斜杠转换为正斜杠，或者使用原始字符串
            Path = Path.replace('\\', '/')
        elif ':' in Path and Path.endswith(':'):
            # 处理类似 "C:" 这样的路径
            Path = Path + '/'
    
    try:
        return psutil.disk_usage(Path)
    except Exception as e:
        # 如果标准方法失败，尝试其他方法
        if os.name == 'nt':
            # Windows系统：尝试使用驱动器号
            if ':' in Path:
                drive_letter = Path.split(':')[0] + ':'
                try:
                    return psutil.disk_usage(drive_letter + '\\')
                except:
                    pass
        raise e

def GetDiskIOCounters(PerDisk: bool = False):
    """Get disk IO counters"""
    return psutil.disk_io_counters(perdisk=PerDisk)
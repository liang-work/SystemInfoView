#!/usr/bin/env python3
"""
测试磁盘修复脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from PySystemInfo import Disk
    import psutil
    
    print("测试磁盘信息获取...")
    
    # 获取所有分区
    partitions = Disk.GetDiskMount(all=False)
    print(f"找到 {len(partitions)} 个分区")
    
    for i, partition in enumerate(partitions):
        print(f"\n分区 {i+1}:")
        print(f"  设备: {partition.device}")
        print(f"  挂载点: {partition.mountpoint}")
        print(f"  文件系统: {partition.fstype}")
        
        try:
            # 测试磁盘使用情况获取
            usage = Disk.GetDiskUsage(partition.mountpoint)
            print(f"  ✅ 使用情况获取成功:")
            print(f"     总空间: {usage.total / (1024**3):.2f} GB")
            print(f"     已用空间: {usage.used / (1024**3):.2f} GB") 
            print(f"     可用空间: {usage.free / (1024**3):.2f} GB")
            print(f"     使用率: {(usage.used / usage.total * 100):.1f}%")
        except Exception as e:
            print(f"  ❌ 使用情况获取失败: {e}")
    
    print("\n🎉 磁盘测试完成!")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
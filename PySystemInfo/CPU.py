import psutil

def GetCPURunTimes():
    """Get CPU run times"""
    return psutil.cpu_times()

def GetCPUUtilization(InterruptsTime:int = 1, EveryCore: bool = False):
    """Get CPU utilization"""
    return psutil.cpu_percent(interval=InterruptsTime, percpu=EveryCore)

def GetCPUCoreCount():
    """Get CPU core count"""
    return psutil.Process().cpu_affinity()

def GetCPUFrequency(AllCPU: bool = False):
    """Get CPU frequency"""
    return psutil.cpu_freq(percpu=AllCPU)
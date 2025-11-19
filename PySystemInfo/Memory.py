import psutil

def GetRunMemory():
    """Get run memory info"""
    return psutil.virtual_memory()

def GetSwapMemory():
    """Get swap memory info"""
    return psutil.swap_memory()
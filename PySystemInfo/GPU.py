import GPUtil

def GetGPUInfo():
    """Get GPU information"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return []

        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                'id': gpu.id,
                'name': gpu.name,
                'load': gpu.load * 100,  # Convert to percentage
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal,
                'memory_free': gpu.memoryFree,
                'memory_util': gpu.memoryUtil * 100,  # Convert to percentage
                'temperature': gpu.temperature
            })
        return gpu_info
    except Exception as e:
        # If GPUtil fails, return empty list
        return []

def GetGPUUtilization():
    """Get GPU utilization for all GPUs"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return []

        return [gpu.load * 100 for gpu in gpus]
    except Exception as e:
        return []

def GetGPUMemory():
    """Get GPU memory info for all GPUs"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return []

        memory_info = []
        for gpu in gpus:
            memory_info.append({
                'used': gpu.memoryUsed,
                'total': gpu.memoryTotal,
                'free': gpu.memoryFree,
                'utilization': gpu.memoryUtil * 100
            })
        return memory_info
    except Exception as e:
        return []

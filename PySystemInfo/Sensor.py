import psutil

def GetTemperature() -> dict:
    """Get temperature"""
    return psutil.sensors_temperatures()

def GetFanSpeed() -> dict:
    """Get fan speed"""
    return psutil.sensors_fans()

def GetBatteryInfo():
    """Get battery info"""
    return psutil.sensors_battery()
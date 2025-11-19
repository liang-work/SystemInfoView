import psutil

def GetNetworkIO(Pernic: bool = False):
    """Get network IO counters"""
    return psutil.net_io_counters(pernic=Pernic)

def GetNetworkStats(Pernic: str = 'all') -> list:
    """Get network stats"""
    return psutil.net_connections(kind=Pernic)

def GetNetworkInfo() -> dict:
    """Get network info"""
    return psutil.net_if_addrs()

def GetNetworkCardStatus() -> dict:
    """Get network card status"""
    return psutil.net_if_stats()
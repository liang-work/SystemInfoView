import os
import sys
import platform  # 添加platform模块

PYTHON_VERSION = sys.version.split()[0]
OS = os.name

def GetSystemConst() -> dict:
    """Get system const"""
    try:
        # 兼容Windows系统，Windows上没有os.uname()
        if hasattr(os, 'uname'):
            uname = os.uname()
            return {
                "System": os.name,
                "Platform": uname.sysname,
                "Release": uname.release,
                "Version": uname.version,
                "Machine": uname.machine,
            }
        else:
            # Windows系统使用platform模块
            return {
                "System": os.name,
                "Platform": platform.system(),
                "Release": platform.release(),
                "Version": platform.version(),
                "Machine": platform.machine(),
            }
    except Exception as e:
        return {"error": f"获取系统信息失败: {str(e)}"}

def GetPythonInfo() -> dict:
    """Get python info"""
    return {
        "Version": sys.version,
        "VersionInfo": sys.version_info,
        "Platform": sys.platform,
        "Executable": sys.executable,
        "Prefix": sys.prefix,
        "BasePrefix": sys.base_prefix,
        "Path": sys.path,
    }
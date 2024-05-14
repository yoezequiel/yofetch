import os
import platform
import psutil
import subprocess
import socket


def get_cpu_name():
    return subprocess.getoutput(
        "cat /proc/cpuinfo | grep 'model name' | uniq | awk -F ': ' '{print $2}'"
    )


def get_memory_usage():
    vm = psutil.virtual_memory()
    return f"\033[36m{vm.used / (1024**3):.2f} GB / {vm.total / (1024**3):.2f} GB\033[0m (\033[35m{vm.percent}%\033[0m)"


def get_swap_usage():
    swap = psutil.swap_memory()
    return f"\033[36m{swap.free / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB\033[0m (\033[35m{swap.percent}%\033[0m)"


def get_disk_usage():
    partitions = psutil.disk_partitions()
    disk_usage_str = ""
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_usage_str += f"\033[93m{partition.mountpoint}\033[0m: \033[96m{usage.free / (1024**3):.2f} GB / {usage.total / (1024**3):.2f} GB\033[0m (\033[91m{usage.percent}%\033[0m)\n"
    return disk_usage_str.strip()


def get_linux_distribution():
    with open("/etc/os-release") as f:
        distro_info = {}
        for line in f:
            key, _, value = line.strip().partition("=")
            if key and value:
                distro_info[key] = value.strip('"')
        return distro_info.get("ID", "Unknown"), distro_info.get("VERSION", "Unknown")


def get_battery_info():
    battery_info = subprocess.getoutput("upower -i $(upower -e | grep 'BAT')")
    percentage = None
    for line in battery_info.split("\n"):
        if "percentage" in line:
            percentage = line.split(":")[1].strip()
            break
    state = None
    for line in battery_info.split("\n"):
        if "state" in line:
            state = line.split(":")[1].strip()
            break
    state_symbol = "↑" if state == "charging" else "↓" if state == "discharging" else ""
    return f"{percentage} {state_symbol}"


def get_local_ip():
    try:
        output = subprocess.getoutput("hostname -I")
        return output.strip()
    except Exception as e:
        return f"Error: {str(e)}"


distro_id, distro_version = get_linux_distribution()
system_info = {
    "Operating System": f"\033[91m{distro_id.capitalize()}\033[0m ({distro_version})",
    "Kernel": platform.uname().release,
    "Uptime": subprocess.getoutput("uptime -p"),
    "Packages": subprocess.getoutput("dpkg-query -f '.\n' -W | wc -l"),
    "Shell": os.path.basename(os.environ.get("SHELL")),
    "Display": subprocess.getoutput("xrandr | grep '*' | awk '{print $1}'"),
    "Terminal": os.environ.get("TERM"),
    "IP": get_local_ip(),
    "Battery": get_battery_info(),
    "CPU": get_cpu_name(),
    "RAM": get_memory_usage(),
    "Swap": get_swap_usage(),
    "Disks": get_disk_usage(),
}

for key, value in system_info.items():
    print(f"\033[94m{key}:\033[0m {value}")

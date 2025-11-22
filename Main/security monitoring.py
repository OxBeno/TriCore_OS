#!/usr/bin/env python3
"""
OS Security Hardening Script
Simple security assessment and hardening tool (Enhanced)
"""

import os
import sys
import subprocess
import platform
import getpass
from pathlib import Path

def run_command(cmd):
    """Execute a system command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_root():
    """Check for root privileges"""
    if os.geteuid() != 0:
        print("This script requires root privileges.")
        print("Try: sudo python3 os_security.py")
        sys.exit(1)

def get_system_info():
    """Gather system information"""
    print("Collecting system information...")
    system = platform.system()

    try:
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
            distro_info = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    distro_info[key] = value.strip('"')
        distro = distro_info.get('PRETTY_NAME', 'Unknown')
    except:
        distro = "Unknown"

    print(f"System: {system}")
    print(f"Distribution: {distro}")
    return system

def update_system():
    """Update the system packages"""
    print("Updating system...")

    code, out, err = run_command("apt update && apt upgrade -y")
    if code == 0:
        print("System updated successfully")
    else:
        print("Failed to update system")

# ====================== ENHANCED OPEN PORTS SECTION ======================

def scan_open_ports():
    """Scan for open ports and allow selecting ports for detailed info"""
    print("Scanning open ports...")

    print("\n=== Listening Ports ===")
    code, out, err = run_command("ss -tulnp")
    open_ports_map = {}

    if code == 0 and out.strip():
        lines = out.strip().split('\n')
        header = True
        for line in lines:
            if header:
                header = False
                continue

            parts = line.split()
            if len(parts) >= 5:
                proto = parts[0]
                local_addr = parts[4]

                if ':' in local_addr:
                    port = local_addr.split(':')[-1]
                    if port.isdigit():
                        open_ports_map[port] = proto

        print("\nOpen Ports:")
        for port, proto in open_ports_map.items():
            print(f"  Port {port} ({proto})")
    else:
        print("No open ports found or command failed")
        return

    # Allow selecting a port for detailed explanation
    while True:
        print("\nSelect a port number to view its function or type 'exit' to go back:")
        choice = input("Port: ")

        if choice.lower() == 'exit':
            break
        elif choice in open_ports_map:
            print(f"\nDetails for port {choice}:")
            print(port_function(choice))
        else:
            print("Invalid port or port not in open list.")


def port_function(port):
    """Return the purpose of a given port number"""
    common_ports = {
        "20": "FTP Data Transfer",
        "21": "FTP Control",
        "22": "SSH - Secure Shell Remote Login",
        "23": "Telnet (Unsecure Remote Login)",
        "25": "SMTP Mail Transfer",
        "53": "DNS Domain Name Service",
        "67": "DHCP Server",
        "68": "DHCP Client",
        "69": "TFTP",
        "80": "HTTP Web Traffic",
        "110": "POP3 Email",
        "123": "NTP Time Sync",
        "135": "Microsoft RPC",
        "137": "NetBIOS Name Service",
        "138": "NetBIOS Datagram",
        "139": "NetBIOS Session",
        "143": "IMAP Email",
        "161": "SNMP Monitoring",
        "389": "LDAP Directory Service",
        "443": "HTTPS Secure Web",
        "445": "SMB File Sharing",
        "587": "SMTP Submission",
        "993": "IMAPS Secure Email",
        "995": "POP3S Secure Email",
        "2049": "NFS File System",
        "3306": "MySQL Database",
        "3389": "RDP Remote Desktop",
        "5432": "PostgreSQL Database",
        "6379": "Redis Database",
        "8080": "Alternative HTTP / Proxy",
    }

    return common_ports.get(port, "Unknown or uncommon port. Perform a manual check.")
# ========================================================================

def check_firewall():
    print("Checking firewall...")
    code, out, err = run_command("ufw status")
    if "inactive" in out:
        print("Firewall is inactive")
        enable = input("Enable UFW? (y/n): ")
        if enable.lower() == 'y':
            run_command("ufw enable")
            print("Firewall enabled")
    else:
        print("Firewall is active")


def check_ssh_security():
    print("Checking SSH configuration...")
    ssh_config = "/etc/ssh/sshd_config"
    if os.path.exists(ssh_config):
        with open(ssh_config, 'r') as f:
            content = f.read()

        security_settings = {
            "PasswordAuthentication": "no",
            "PermitRootLogin": "no",
            "Protocol": "2"
        }

        for setting, expected in security_settings.items():
            if f"{setting} {expected}" in content or f"{setting}\t{expected}" in content:
                print(f"SSH setting correct: {setting} = {expected}")
            else:
                print(f"SSH setting needs review: {setting}")


def check_sudo_users():
    print("Checking sudo users...")
    code, out, err = run_command("getent group sudo")
    if code == 0:
        print("Sudo users group:")
        print(out.strip())


def main():
    print("OS Security Hardening Tool")
    print("=" * 40)

    check_root()
    get_system_info()

    while True:
        print("\nAvailable actions:")
        print("1. Update system")
        print("2. Check firewall")
        print("3. Check SSH security")
        print("4. Scan open ports (enhanced)")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            update_system()
        elif choice == '2':
            check_firewall()
        elif choice == '3':
            check_ssh_security()
        elif choice == '4':
            scan_open_ports()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ZIVPN Account Manager (ZIMAN) - Enhanced Version
Professional CLI tool for managing ZIVPN with comprehensive service information
"""

import json
import os
import sys
import random
import string
import subprocess
import time
import psutil
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import socket

CONFIG_FILE = "/etc/zivpn/config.json"
SERVICE_NAME = "zivpn"
LOG_FILE = "/var/log/zivpn.log"
CONFIG_DIR = "/etc/zivpn/"

# ======= Utility Functions =======
class ConfigManager:
    """Handles configuration file operations"""
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load and parse the configuration file"""
        if not os.path.exists(CONFIG_FILE):
            print(f"❌ Configuration file not found: {CONFIG_FILE}")
            sys.exit(1)
            
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Error parsing configuration file: {CONFIG_FILE}")
            sys.exit(1)
        except PermissionError:
            print(f"❌ Permission denied when reading: {CONFIG_FILE}")
            sys.exit(1)
    
    @staticmethod
    def save_config(data: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print("✓ Configuration saved successfully")
        except PermissionError:
            print(f"❌ Permission denied when writing: {CONFIG_FILE}")
            sys.exit(1)
    
    @staticmethod
    def get_config_info() -> Dict[str, Any]:
        """Get comprehensive configuration information"""
        config = ConfigManager.load_config()
        info = {
            "file_path": CONFIG_FILE,
            "file_size": f"{os.path.getsize(CONFIG_FILE):,} bytes",
            "last_modified": datetime.fromtimestamp(
                os.path.getmtime(CONFIG_FILE)
            ).strftime('%Y-%m-%d %H:%M:%S'),
            "config_keys": list(config.keys())
        }
        
        # Extract specific config details
        if "server" in config:
            info["server_port"] = config["server"].get("port", "Not set")
            info["server_protocol"] = config["server"].get("protocol", "Not set")
        
        if "auth" in config:
            info["auth_method"] = config["auth"].get("method", "Not set")
            info["password_count"] = len(config["auth"].get("config", []))
        
        return info


class ServiceManager:
    """Handles service operations and monitoring"""
    
    @staticmethod
    def get_service_status() -> Dict[str, Any]:
        """Get detailed service status"""
        status = {
            "name": SERVICE_NAME,
            "active": False,
            "enabled": False,
            "pid": None,
            "uptime": None,
            "memory_usage": None,
            "cpu_percent": None
        }
        
        try:
            # Check if service is active
            result = subprocess.run(
                ["systemctl", "is-active", SERVICE_NAME],
                capture_output=True,
                text=True
            )
            status["active"] = result.stdout.strip() == "active"
            
            # Check if service is enabled
            result = subprocess.run(
                ["systemctl", "is-enabled", SERVICE_NAME],
                capture_output=True,
                text=True
            )
            status["enabled"] = result.stdout.strip() == "enabled"
            
            # Get PID and process info if running
            if status["active"]:
                result = subprocess.run(
                    ["systemctl", "show", SERVICE_NAME, "--property=MainPID"],
                    capture_output=True,
                    text=True
                )
                pid_line = result.stdout.strip()
                if "MainPID=" in pid_line:
                    pid = pid_line.split("=")[1]
                    if pid.isdigit() and int(pid) > 0:
                        status["pid"] = int(pid)
                        
                        # Get process details
                        try:
                            process = psutil.Process(int(pid))
                            status["uptime"] = str(datetime.now() - datetime.fromtimestamp(
                                process.create_time()
                            )).split(".")[0]
                            status["memory_usage"] = f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
                            status["cpu_percent"] = f"{process.cpu_percent():.1f}%"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            
            # Get last log entries
            status["logs"] = ServiceManager.get_last_logs(10)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return status
    
    @staticmethod
    def get_last_logs(lines: int = 10) -> List[str]:
        """Get last N lines from log file"""
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    logs = f.readlines()[-lines:]
                logs = [log.strip() for log in logs]
            except (PermissionError, IOError):
                logs = ["Unable to read log file"]
        return logs
    
    @staticmethod
    def restart_service() -> bool:
        """Restart the ZIVPN service"""
        print("\n🔄 Restarting ZIVPN service...")
        try:
            result = subprocess.run(
                ["systemctl", "restart", SERVICE_NAME],
                capture_output=True,
                text=True,
                check=True
            )
            print("✓ Service restarted successfully\n")
            
            # Wait and verify service is running
            time.sleep(2)
            status = ServiceManager.get_service_status()
            if status["active"]:
                print("✓ Service verified as active")
            else:
                print("⚠️ Service may not be running properly")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restart service: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ 'systemctl' command not found")
            return False
    
    @staticmethod
    def start_service() -> bool:
        """Start the ZIVPN service"""
        print("\n▶️ Starting ZIVPN service...")
        try:
            subprocess.run(
                ["systemctl", "start", SERVICE_NAME],
                check=True
            )
            print("✓ Service started successfully\n")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to start service")
            return False
    
    @staticmethod
    def stop_service() -> bool:
        """Stop the ZIVPN service"""
        print("\n⏹️ Stopping ZIVPN service...")
        try:
            subprocess.run(
                ["systemctl", "stop", SERVICE_NAME],
                check=True
            )
            print("✓ Service stopped successfully\n")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to stop service")
            return False
    
    @staticmethod
    def get_service_logs(count: int = 20) -> None:
        """Display service logs"""
        print(f"\n📋 Last {count} log entries:")
        print("=" * 60)
        logs = ServiceManager.get_last_logs(count)
        for i, log in enumerate(logs, 1):
            print(f"{i:3d}. {log}")
        print("=" * 60)
    
    @staticmethod
    def get_connection_stats() -> Dict[str, Any]:
        """Get connection statistics"""
        stats = {
            "active_connections": 0,
            "total_connections": 0,
            "bytes_sent": 0,
            "bytes_received": 0
        }
        
        try:
            # This is a placeholder - actual implementation would depend on
            # how ZIVPN tracks connections. You might need to parse logs
            # or check specific files.
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = f.read()
                    # Example patterns - adjust based on actual log format
                    stats["total_connections"] = logs.count("connected")
                    stats["active_connections"] = logs.count("connected") - logs.count("disconnected")
        except:
            pass
        
        return stats


class NetworkManager:
    """Handles network-related information"""
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Get network configuration information"""
        info = {
            "hostname": socket.gethostname(),
            "ip_address": "Unable to determine",
            "interfaces": []
        }
        
        try:
            # Get primary IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["ip_address"] = s.getsockname()[0]
            s.close()
        except:
            pass
        
        # Get network interfaces
        try:
            interfaces = psutil.net_if_addrs()
            for iface, addrs in interfaces.items():
                iface_info = {"name": iface, "addresses": []}
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        iface_info["addresses"].append(f"IPv4: {addr.address}/{addr.netmask}")
                    elif addr.family == socket.AF_INET6:
                        iface_info["addresses"].append(f"IPv6: {addr.address}")
                info["interfaces"].append(iface_info)
        except:
            pass
        
        return info
    
    @staticmethod
    def check_ports() -> List[Dict[str, Any]]:
        """Check which ports are listening"""
        listening_ports = []
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    listening_ports.append({
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "pid": conn.pid or "Unknown",
                        "status": conn.status
                    })
        except:
            pass
        
        return listening_ports


class PasswordManager:
    """Handles password operations"""
    
    def __init__(self):
        self.config = ConfigManager.load_config()
    
    def get_passwords(self) -> List[str]:
        """Get current password list"""
        return self.config.get("auth", {}).get("config", [])
    
    def update_passwords(self, passwords: List[str]) -> None:
        """Update passwords in config and restart service"""
        if "auth" not in self.config:
            self.config["auth"] = {}
        self.config["auth"]["config"] = passwords
        ConfigManager.save_config(self.config)
        
        # Only restart if service is active
        status = ServiceManager.get_service_status()
        if status["active"]:
            ServiceManager.restart_service()
        else:
            print("⚠️ Service is not active. Configuration saved but service not restarted.")
    
    def list_passwords(self) -> None:
        """Display all current passwords"""
        passwords = self.get_passwords()
        
        if not passwords:
            print("\n📭 No passwords registered")
            return
        
        print("\n🔑 Registered Passwords:")
        print("=" * 60)
        for idx, password in enumerate(passwords, 1):
            masked = password[:4] + "*" * (len(password) - 4) if len(password) > 4 else "****"
            print(f"{idx:3d}. {masked} ({len(password)} chars)")
        print(f"\nTotal: {len(passwords)} password(s)")
    
    def add_password(self, password: Optional[str] = None) -> None:
        """Add a new password"""
        if password is None:
            password = input("\nEnter new password: ").strip()
        
        if not password:
            print("❌ Password cannot be empty")
            return
        
        if len(password) < 8:
            print("⚠️  Warning: Password should be at least 8 characters")
            proceed = input("Continue anyway? (y/N): ").lower()
            if proceed != 'y':
                print("Operation cancelled")
                return
        
        passwords = self.get_passwords()
        
        if password in passwords:
            print(f"⚠️  Password '{password[:4]}...' already exists")
            return
        
        passwords.append(password)
        self.update_passwords(passwords)
        print(f"✓ Password '{password[:4]}...' added successfully")
    
    def remove_password(self) -> None:
        """Remove a password by index"""
        passwords = self.get_passwords()
        
        if not passwords:
            print("\n📭 No passwords to remove")
            return
        
        self.list_passwords()
        
        try:
            idx = int(input("\nEnter password number to remove: ").strip())
            if idx < 1 or idx > len(passwords):
                print("❌ Invalid number")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        removed_password = passwords.pop(idx - 1)
        self.update_passwords(passwords)
        print(f"✓ Password '{removed_password[:4]}...' removed successfully")
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Generate a secure random password"""
        # Mix of uppercase, lowercase, digits, and special characters
        chars = {
            'lower': string.ascii_lowercase,
            'upper': string.ascii_uppercase,
            'digits': string.digits,
            'special': '!@#$%^&*'
        }
        
        # Ensure at least one character from each category
        password = [
            random.choice(chars['lower']),
            random.choice(chars['upper']),
            random.choice(chars['digits']),
            random.choice(chars['special'])
        ]
        
        # Fill the rest with random characters
        all_chars = ''.join(chars.values())
        password.extend(random.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password
        random.shuffle(password)
        return ''.join(password)


# ======= CLI Interface =======
class CLIInterface:
    """Handles the command line interface"""
    
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    @staticmethod
    def display_header() -> None:
        """Display application header"""
        CLIInterface.clear_screen()
        print("=" * 60)
        print("            ZIVPN ACCOUNT MANAGER (ZIMAN) v2.0")
        print("=" * 60)
        print("Comprehensive VPN Service Management Tool\n")
    
    @staticmethod
    def display_dashboard() -> None:
        """Display service dashboard"""
        CLIInterface.clear_screen()
        print("=" * 60)
        print("              ZIVPN SERVICE DASHBOARD")
        print("=" * 60)
        
        # Service Status
        status = ServiceManager.get_service_status()
        status_icon = "🟢" if status["active"] else "🔴"
        enabled_icon = "✅" if status["enabled"] else "❌"
        
        print(f"\n📊 SERVICE STATUS")
        print("-" * 40)
        print(f"Status:     {status_icon} {'ACTIVE' if status['active'] else 'INACTIVE'}")
        print(f"Auto-start: {enabled_icon} {'ENABLED' if status['enabled'] else 'DISABLED'}")
        
        if status["active"]:
            print(f"PID:        {status['pid'] or 'Unknown'}")
            print(f"Uptime:     {status['uptime'] or 'Unknown'}")
            print(f"Memory:     {status['memory_usage'] or 'Unknown'}")
            print(f"CPU Usage:  {status['cpu_percent'] or 'Unknown'}")
        
        # Password Info
        pm = PasswordManager()
        passwords = pm.get_passwords()
        print(f"\n🔐 AUTHENTICATION")
        print("-" * 40)
        print(f"Passwords:  {len(passwords)} registered")
        
        # Configuration Info
        config_info = ConfigManager.get_config_info()
        print(f"\n⚙️  CONFIGURATION")
        print("-" * 40)
        print(f"Config File: {config_info['file_path']}")
        print(f"Last Modified: {config_info['last_modified']}")
        if 'server_port' in config_info:
            print(f"Server Port: {config_info['server_port']}")
        
        # Connection Stats
        stats = ServiceManager.get_connection_stats()
        print(f"\n📈 CONNECTION STATISTICS")
        print("-" * 40)
        print(f"Active Connections: {stats['active_connections']}")
        print(f"Total Connections:  {stats['total_connections']}")
        
        # Network Info
        network_info = NetworkManager.get_network_info()
        print(f"\n🌐 NETWORK INFORMATION")
        print("-" * 40)
        print(f"Hostname:   {network_info['hostname']}")
        print(f"IP Address: {network_info['ip_address']}")
        
        print("\n" + "=" * 60)
    
    @staticmethod
    def display_menu() -> None:
        """Display main menu"""
        print("\nMAIN MENU")
        print("-" * 40)
        print("1. 📊 Service Dashboard")
        print("2. 📝 Password Management")
        print("3. ⚙️  Service Control")
        print("4. 📋 View Logs")
        print("5. 🔧 Advanced Tools")
        print("6. 🚪 Exit")
        print("-" * 40)
    
    @staticmethod
    def display_password_menu() -> None:
        """Display password management menu"""
        print("\n🔐 PASSWORD MANAGEMENT")
        print("-" * 40)
        print("1. Add Manual Password")
        print("2. Generate Secure Password")
        print("3. Remove Password")
        print("4. List Passwords")
        print("5. Back to Main Menu")
        print("-" * 40)
    
    @staticmethod
    def display_service_menu() -> None:
        """Display service control menu"""
        status = ServiceManager.get_service_status()
        status_text = "ACTIVE" if status["active"] else "INACTIVE"
        
        print(f"\n⚙️  SERVICE CONTROL [Status: {status_text}]")
        print("-" * 40)
        print("1. Start Service")
        print("2. Stop Service")
        print("3. Restart Service")
        print("4. Check Port Status")
        print("5. Back to Main Menu")
        print("-" * 40)
    
    @staticmethod
    def display_advanced_menu() -> None:
        """Display advanced tools menu"""
        print("\n🔧 ADVANCED TOOLS")
        print("-" * 40)
        print("1. View Configuration Details")
        print("2. Check Network Interfaces")
        print("3. Test Service Connectivity")
        print("4. Backup Configuration")
        print("5. Back to Main Menu")
        print("-" * 40)
    
    @staticmethod
    def get_choice(prompt: str = "\nSelect option: ") -> str:
        """Get user menu choice"""
        return input(prompt).strip()


# ======= Main Application =======
def main():
    """Main application entry point"""
    pm = PasswordManager()
    cli = CLIInterface()
    
    while True:
        cli.display_header()
        cli.display_menu()
        choice = cli.get_choice()
        
        if choice == "1":
            # Service Dashboard
            cli.display_dashboard()
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            # Password Management Submenu
            while True:
                cli.display_header()
                cli.display_password_menu()
                sub_choice = cli.get_choice()
                
                if sub_choice == "1":
                    pm.add_password()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "2":
                    try:
                        length = int(input("\nPassword length (default: 12): ").strip() or "12")
                        if length < 8:
                            print("⚠️  Minimum length is 8 characters")
                            length = 8
                        elif length > 32:
                            print("⚠️  Maximum length is 32 characters")
                            length = 32
                    except ValueError:
                        print("⚠️  Using default length: 12")
                        length = 12
                    
                    password = PasswordManager.generate_password(length)
                    pm.add_password(password)
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "3":
                    pm.remove_password()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "4":
                    pm.list_passwords()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "5":
                    break
                
                else:
                    print("\n❌ Invalid option")
                    input("Press Enter to continue...")
        
        elif choice == "3":
            # Service Control Submenu
            while True:
                cli.display_header()
                cli.display_service_menu()
                sub_choice = cli.get_choice()
                
                if sub_choice == "1":
                    ServiceManager.start_service()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "2":
                    ServiceManager.stop_service()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "3":
                    ServiceManager.restart_service()
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "4":
                    print("\n📡 Listening Ports:")
                    print("-" * 40)
                    ports = NetworkManager.check_ports()
                    for port in ports:
                        print(f"Port {port['port']} on {port['address']} (PID: {port['pid']})")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "5":
                    break
                
                else:
                    print("\n❌ Invalid option")
                    input("Press Enter to continue...")
        
        elif choice == "4":
            # View Logs
            try:
                count = int(input("\nNumber of log entries to view (default: 20): ").strip() or "20")
                if count < 1 or count > 100:
                    print("⚠️  Showing 20 entries (1-100 allowed)")
                    count = 20
            except ValueError:
                print("⚠️  Showing 20 entries")
                count = 20
            
            ServiceManager.get_service_logs(count)
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            # Advanced Tools Submenu
            while True:
                cli.display_header()
                cli.display_advanced_menu()
                sub_choice = cli.get_choice()
                
                if sub_choice == "1":
                    print("\n⚙️  CONFIGURATION DETAILS")
                    print("=" * 40)
                    config_info = ConfigManager.get_config_info()
                    for key, value in config_info.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "2":
                    print("\n🌐 NETWORK INTERFACES")
                    print("=" * 40)
                    network_info = NetworkManager.get_network_info()
                    for iface in network_info["interfaces"]:
                        print(f"\nInterface: {iface['name']}")
                        for addr in iface["addresses"]:
                            print(f"  {addr}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "3":
                    print("\n🔌 Testing Service Connectivity...")
                    status = ServiceManager.get_service_status()
                    if status["active"]:
                        print("✓ Service is running")
                        # Add more connectivity tests here
                    else:
                        print("❌ Service is not running")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "4":
                    # Backup configuration
                    backup_file = f"{CONFIG_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    try:
                        import shutil
                        shutil.copy2(CONFIG_FILE, backup_file)
                        print(f"✓ Configuration backed up to: {backup_file}")
                    except Exception as e:
                        print(f"❌ Backup failed: {e}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == "5":
                    break
                
                else:
                    print("\n❌ Invalid option")
                    input("Press Enter to continue...")
        
        elif choice == "6":
            print("\n👋 Thank you for using ZIMAN. Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option")
            input("Press Enter to continue...")


if __name__ == "__main__":
    # Check if running as root for full functionality
    if os.geteuid() != 0:
        print("⚠️  Warning: Running without root privileges")
        print("Some features may be limited")
        print("Consider running with 'sudo' for full functionality\n")
        input("Press Enter to continue...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

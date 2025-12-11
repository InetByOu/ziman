#!/usr/bin/env python3
"""
ZIVPN Account Manager (ZIMAN)
Professional CLI tool for managing ZIVPN authentication passwords
"""

import json
import os
import sys
import random
import string
import subprocess
from typing import List, Optional, Dict, Any

CONFIG_FILE = "/etc/zivpn/config.json"
SERVICE_NAME = "zivpn"

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


class ServiceManager:
    """Handles service operations"""
    
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
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restart service: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ 'systemctl' command not found")
            return False


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
        ServiceManager.restart_service()
    
    def list_passwords(self) -> None:
        """Display all current passwords"""
        passwords = self.get_passwords()
        
        if not passwords:
            print("\n📭 No passwords registered")
            return
        
        print("\n🔑 Registered Passwords:")
        print("-" * 40)
        for idx, password in enumerate(passwords, 1):
            print(f"{idx:3d}. {password}")
        print(f"\nTotal: {len(passwords)} password(s)")
    
    def add_password(self, password: Optional[str] = None) -> None:
        """Add a new password"""
        if password is None:
            password = input("\nEnter new password: ").strip()
        
        if not password:
            print("❌ Password cannot be empty")
            return
        
        passwords = self.get_passwords()
        
        if password in passwords:
            print(f"⚠️  Password '{password}' already exists")
            return
        
        passwords.append(password)
        self.update_passwords(passwords)
        print(f"✓ Password '{password}' added successfully")
    
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
        print(f"✓ Password '{removed_password}' removed successfully")
    
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
        print("=" * 50)
        print("          ZIVPN ACCOUNT MANAGER (ZIMAN)")
        print("=" * 50)
        print("Professional VPN Authentication Management Tool\n")
    
    @staticmethod
    def display_menu() -> None:
        """Display main menu"""
        print("MAIN MENU")
        print("-" * 30)
        print("1. 📝 Add Manual Password")
        print("2. ⚡ Add Generated Password")
        print("3. 🗑️  Remove Password")
        print("4. 📋 List Passwords")
        print("5. 🚪 Exit")
        print("-" * 30)
    
    @staticmethod
    def get_choice() -> str:
        """Get user menu choice"""
        return input("\nSelect option [1-5]: ").strip()


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
            pm.add_password()
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            # Generate password with user-defined length
            try:
                length = int(input("\nPassword length (default: 12): ").strip() or "12")
                if length < 8:
                    print("⚠️  Password length should be at least 8 characters")
                    length = 8
                elif length > 32:
                    print("⚠️  Password length limited to 32 characters")
                    length = 32
            except ValueError:
                print("⚠️  Using default length: 12")
                length = 12
            
            password = PasswordManager.generate_password(length)
            pm.add_password(password)
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            pm.remove_password()
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            pm.list_passwords()
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print("\n👋 Thank you for using ZIMAN. Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    # Check if running as root for service restart capability
    if os.geteuid() != 0:
        print("⚠️  Warning: Some operations may require root privileges")
        print("Consider running with sudo for full functionality\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

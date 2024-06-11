import subprocess
import re
import os

class WiFiManager:
    @staticmethod
    def find_all_devices():
        """
        Find all wireless devices on the system.
        :return: List of wireless devices.
        """
        result = subprocess.run(['iw', 'dev'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        devices = re.findall(r'Interface\s(\w+)', output)
        return devices

    @staticmethod
    def get_device_info(device):
        """
        Get detailed information about a specific wireless device.
        :param device: The wireless device to query.
        :return: Information about the device.
        """
        result = subprocess.run(['iw', 'dev', device, 'info'], stdout=subprocess.PIPE)
        return result.stdout.decode()

    @staticmethod
    def enable_monitor_mode(device):
        """
        Enable monitor mode on a specific wireless device using ip and iw.
        :param device: The wireless device to put into monitor mode.
        """
        subprocess.run(['ip', 'link', 'set', device, 'down'], check=True)
        subprocess.run(['iw', device, 'set', 'monitor', 'control'], check=True)
        subprocess.run(['ip', 'link', 'set', device, 'up'], check=True)

    @staticmethod
    def disable_monitor_mode(device):
        """
        Disable monitor mode on a specific wireless device using ip and iw.
        :param device: The wireless device to remove from monitor mode.
        """
        subprocess.run(['ip', 'link', 'set', device, 'down'], check=True)
        subprocess.run(['iw', device, 'set', 'type', 'managed'], check=True)
        subprocess.run(['ip', 'link', 'set', device, 'up'], check=True)

    @staticmethod
    def enable_networking():
        """
        Enable networking tasks.
        """
        subprocess.run(['systemctl', 'start', 'NetworkManager'], check=True)
        subprocess.run(['systemctl', 'start', 'wpa_supplicant'], check=True)

    @staticmethod
    def disable_networking():
        """
        Disable networking tasks.
        """
        subprocess.run(['systemctl', 'stop', 'NetworkManager'], check=True)
        subprocess.run(['systemctl', 'stop', 'wpa_supplicant'], check=True)

    @staticmethod
    def kill_interfering_tasks():
        """
        Kill tasks that might interfere with wireless scanning.
        """
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True)

    @staticmethod
    def restore_networking():
        """
        Restore networking tasks to normal after scanning.
        """
        WiFiManager.enable_networking()

    @staticmethod
    def scan_for_networks(device):
        """
        Scan for wireless networks.
        :param device: The wireless device to use for scanning.
        :return: List of available networks.
        """
        result = subprocess.run(['iwlist', device, 'scanning'], stdout=subprocess.PIPE)
        return result.stdout.decode()

    @staticmethod
    def start_monitor_mode_airmon(device):
        """
        Enable monitor mode on a specific wireless device using airmon-ng.
        :param device: The wireless device to put into monitor mode.
        :return: Name of the monitor mode interface or None if failed.
        """
        result = subprocess.run(['airmon-ng', 'start', device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        match = re.search(r'(\w+) mode enabled on (\w+)', output)
        if match:
            return match.group(2)
        else:
            print(f"Error starting monitor mode on {device}: {result.stderr.decode()}")
            return None

    @staticmethod
    def stop_monitor_mode_airmon(device):
        """
        Disable monitor mode on a specific wireless device using airmon-ng.
        :param device: The wireless device to remove from monitor mode.
        """
        subprocess.run(['airmon-ng', 'stop', device], check=True)

# Example usage of the WiFiManager class
if __name__ == "__main__":
    wifi_manager = WiFiManager()

    # Find all devices
    devices = wifi_manager.find_all_devices()
    print(f"Found devices: {devices}")

    if devices:
        device = devices[0]

        # Get device information
        info = wifi_manager.get_device_info(device)
        print(f"Device info for {device}:\n{info}")

        # Kill interfering tasks
        wifi_manager.kill_interfering_tasks()

        # Enable monitor mode using airmon-ng
        monitor_device = wifi_manager.start_monitor_mode_airmon(device)
        if monitor_device:
            print(f"Enabled monitor mode on {device}, new interface: {monitor_device}")

            # Scan for networks
            networks = wifi_manager.scan_for_networks(monitor_device)
            print(f"Networks found:\n{networks}")

            # Disable monitor mode using airmon-ng
            wifi_manager.stop_monitor_mode_airmon(monitor_device)
            print(f"Disabled monitor mode on {monitor_device}")

        # Restore networking
        wifi_manager.restore_networking()
        print("Restored networking")

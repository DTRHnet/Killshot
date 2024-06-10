
import argparse
import sys
import os
import subprocess
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
import logging
import platform
import ctypes
from term_util import TermUtil

# Define version of the script
SCRIPT_VERSION = "1.0"
tu = TermUtil()


# Initialize Rich console for better output
console = Console()
#tu.hTitle( "testing loh", 'left', char='-' )
def main():
    # Display banner
    display_banner()

    # Check for root/administrator privileges
    if not is_root():
        console.print("[bold red]ERROR:[/] This script must be run as root or with administrator privileges.")
        sys.exit(1)

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Scan for WEP/WPS enabled networks on multiple platforms."
    )

    # Adding command-line arguments to the parser
    parser.add_argument(
        '-l', '--log', 
        help="Enable logging to a file. Usage: --log [level] [file]",
        nargs='*',
        default=[]
    )
    parser.add_argument(
        '-v', '--verbose', 
        help="Increase output verbosity",
        action='store_true'
    )
    parser.add_argument(
        '-V', '--version', 
        help="Show the script version and exit",
        action='version',
        version=f'%(prog)s {SCRIPT_VERSION}'
    )
    parser.add_argument(
        '-d', '--device', 
        help="Specify the network device to use",
        type=str,
        required=False
    )
    parser.add_argument(
        '-F', '--filter', 
        help="Apply filters (e.g., channel, band, etc.)",
        type=str,
        nargs='+',
        choices=['channel', 'band']
    )
    parser.add_argument(
        '-b', '--no-banner', 
        help="Do not display the banner",
        action='store_true'
    )
    parser.add_argument(
        '-L', '--list-devices', 
        help="List all network devices",
        action='store_true'
    )
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Handle logging if --log is specified
    if args.log:
        setup_logging(args.log)
    
    # Handle verbosity if --verbose is specified
    if args.verbose:
        enable_verbose_output()

    # List network devices if --list-devices is specified
    if args.list_devices:
        list_network_devices()
        sys.exit(0)
    
    # Extract the network device from the parsed arguments
    device = args.device
    
    # Extract filters if provided
    filters = args.filter

    # Display information about the scanning process
    if device:
        print(f"Scanning using device: {device}")
    if filters:
        print(f"Applying filters: {', '.join(filters)}")

    # Check if the device is in monitor mode
    if device and not is_device_in_monitor_mode(device):
        console.print(f"[bold red]ERROR:[/] Device {device} is not in monitor mode.")
        enable_monitor = console.input(f"Would you like Killshot to attempt to enable monitor mode on {device}? [Y/n]: ").strip().lower()
        
        if enable_monitor == 'y' or enable_monitor == '':
            if enable_monitor_mode(device):
                console.print(f"[bold green]SUCCESS:[/] Monitor mode enabled on {device}.")
            else:
                console.print(f"[bold red]ERROR:[/] Failed to enable monitor mode on {device}.")
                display_all_devices()
                sys.exit(1)
        else:
            display_all_devices()
            sys.exit(1)

    # Placeholder for the actual scanning logic
    if device:
        scan_networks(device, filters)

def display_banner():
    """
    Function to display the ASCII banner.
    """
    banner = """
						    
  888 88P ,e, 888 888       888                 d8   
  888 8P   "  888 888  dP"Y 888 ee   e88 88e   d88   
  888 K   888 888 888 C88b  888 88b d888 888b d88888 
  888 8b  888 888 888  Y88D 888 888 Y888 888P  888   
  888 88b 888 888 888 d,dP  888 888  "88 88"   888   
                                                     
    """
   # tu.hTitle("DTRH.net", position='left', char='-')
    print(banner)

def setup_logging(log_args):
    """
    Function to set up logging based on provided arguments.
    :param log_args: List containing log level and optional file path.
    """
    # Default log level and file path
    log_level = logging.INFO
    log_file = "killshot.log"

    # If log_args is not empty, process the provided arguments
    if log_args:
        if len(log_args) >= 1:
            # Determine the log level
            level_arg = log_args[0].upper()
            level_mapping = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL,
                '1': logging.DEBUG,
                '2': logging.INFO,
                '3': logging.WARNING,
                '4': logging.ERROR,
                '5': logging.CRITICAL
            }
            log_level = level_mapping.get(level_arg, logging.INFO)
        
        if len(log_args) == 2:
            # Determine the log file path
            log_file = log_args[1]

    # Ensure the log file is created if it does not exist
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

    # Configure logging with rich handler
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        datefmt='[%X]',
        handlers=[RichHandler(), logging.FileHandler(log_file)]
    )
    logging.getLogger().info(f"Logging started with level {logging.getLevelName(log_level)} and output to {log_file}")

def enable_verbose_output():
    """
    Function to enable verbose output.
    Uses the rich library to print blue-themed INFO text.
    """
    console.print("[bold blue]INFO:[/] Verbose output is enabled.")

def is_device_in_monitor_mode(device):
    """
    Function to check if the Wi-Fi device is in monitor mode using airmon-ng.
    :param device: The network device to check.
    :return: True if the device is in monitor mode, False otherwise.
    """
    try:
        # Run the airmon-ng command to check for monitor mode
        result = subprocess.run(['airmon-ng', 'status'], capture_output=True, text=True)
        # Check if the device is listed in the monitor mode output
        if f"{device}  monitor mode vif enabled" in result.stdout:
            logging.info(f"Device {device} is already in monitor mode.")
            return True
        else:
            logging.info(f"Device {device} is not in monitor mode.")
            return False
    except FileNotFoundError:
        # airmon-ng is not installed
        console.print("[bold red]ERROR:[/] airmon-ng is not installed. Please install aircrack-ng and try again.")
        logging.error("airmon-ng is not installed. Exiting.")
        sys.exit(1)

def enable_monitor_mode(device):
    """
    Function to enable monitor mode on the specified device using airmon-ng.
    :param device: The network device to enable monitor mode on.
    :return: True if successful, False otherwise.
    """
    try:
        logging.info(f"Attempting to enable monitor mode on {device}.")
        result = subprocess.run(['sudo', 'airmon-ng', 'start', device], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Monitor mode enabled on {device}.")
            return True
        else:
            logging.error(f"Failed to enable monitor mode on {device}. airmon-ng output: {result.stdout}")
            return False
    except Exception as e:
        logging.error(f"Exception occurred while trying to enable monitor mode: {e}")
        return False

def display_all_devices():
    """
    Function to display all wireless devices using airmon-ng.
    """
    try:
        console.print("[bold yellow]INFO:[/] Displaying all wireless devices:")
        subprocess.run(['airmon-ng'], check=True)
    except FileNotFoundError:
        console.print("[bold red]ERROR:[/] airmon-ng is not installed. Please install aircrack-ng and try again.")
        logging.error("airmon-ng is not installed. Cannot display wireless devices.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error displaying wireless devices: {e}")

def list_network_devices():
    """
    Function to list all network devices using the ip link command.
    """
    try:
        # Run the ip link command to get network devices information
        result = subprocess.run(['ip', 'link'], capture_output=True, text=True)
        # Parse the output to extract device information
        devices = parse_ip_link_output(result.stdout)
        
        # Display the devices in a table
        table = Table(title="Network Devices")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")

        for device in devices:
            table.add_row(device['type'], device['name'], device['status'])
        
        console.print(table)
    except FileNotFoundError:
        console.print("[bold red]ERROR:[/] ip command is not found. Please ensure the necessary networking tools are installed.")
        logging.error("ip command is not found.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error listing network devices: {e}")
        console.print(f"[bold red]ERROR:[/] Failed to list network devices: {e}")
        sys.exit(1)

def parse_ip_link_output(output):
    """
    Function to parse the output of the 'ip link' command and extract network device information.
    :param output: The output of the 'ip link' command.
    :return: A list of dictionaries containing device information.
    """
    devices = []
    lines = output.splitlines()
    current_device = {}

    for line in lines:
        if not line.startswith(" "):
            if current_device:
                devices.append(current_device)
                current_device = {}

            parts = line.split(": ")
            if len(parts) >= 2:
                device_name = parts[1].split()[0]
                current_device['name'] = device_name
                current_device['status'] = "UP" if "UP" in parts[1] else "DOWN"
        else:
            if "link/" in line:
                link_type = line.split(" ")[1]
                current_device['type'] = link_type

    if current_device:
        devices.append(current_device)

    return devices

def scan_networks(device, filters):
    """
    Function to scan networks.
    Placeholder implementation.
    """
    logging.info(f"Scanning networks on device {device} with filters: {filters}")
    # Implement the network scanning functionality here

def is_root():
    """
    Function to check if the script is run as root (Linux/macOS) or as an administrator (Windows).
    :return: True if running with required privileges, False otherwise.
    """
    current_os = platform.system()
    if current_os == "Linux" or current_os == "Darwin":
        # Check for root privileges on Linux or macOS
        return os.geteuid() == 0
    elif current_os == "Windows":
        # Check for administrator privileges on Windows
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        # Unsupported OS
        console.print("[bold red]ERROR:[/] Unsupported operating system.")
        sys.exit(1)

if __name__ == "__main__":
    main()

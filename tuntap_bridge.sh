#!/bin/bash

# Default values
SERIAL=""
DEST_IP=""
BAUDRATE=""
INTERFACE=""
IP_ADDRESS=""
SHOW_HELP=false

# Function to display usage information
show_help() {
  echo "Usage: $0 [-s serial] [-b baudrate] [-i interface] [-a ip_address] [-h]"
  echo "Optional parameters:"
  echo "  -s serial      Serial device (default: empty)"
  echo "  -b baudrate    Baudrate (default: empty)"
  echo "  -i interface   Network interface (default: empty)"
  echo "  -a ip_address  IP address (default: empty)"
  echo "  -d dest_ip     Destenation IP for the tun (default: empty)"
  echo "  -h             Display this help message"
  exit 1
}

while getopts "s:b:i:a:d:h:" opt; do
  case $opt in
    s) SERIAL="$OPTARG";;
    d) DEST_IP="$OPTARG";;
    b) BAUDRATE="$OPTARG";;
    i) INTERFACE="$OPTARG";;
    a) IP_ADDRESS="$OPTARG";;
    h) SHOW_HELP=true;;
    \?) echo "Invalid option: -$OPTARG" >&2
        show_help
        exit 1
  esac
done

# Display help message and exit if -h option is specified
if $SHOW_HELP; then
  show_help
fi

shift $((OPTIND-1))

# Check if any parameters are missing
if [ -z "$SERIAL" ] || [ -z "$BAUDRATE" ] || [ -z "$INTERFACE" ] || [ -z "$IP_ADDRESS" ] || [ -z "$DEST_IP" ]; then
  echo "Missing parameters. Please provide all options."
  exit 1
fi

# Use the parameters as needed
echo "Serial: $SERIAL"
echo "Baudrate: $BAUDRATE"
echo "Interface: $INTERFACE"
echo "IP Address: $IP_ADDRESS"
echo "Destination IP: $DEST_IP"

# Function to cleanup and exit
cleanup_and_exit() {
  echo "Received SIGINT. Cleaning up and exiting..."

  # Terminate the background process using its PID
  if [ -n "$subprocess_pid" ]; then
    kill -SIGTERM "$subprocess_pid"
    wait "$subprocess_pid"
  fi

  exit 1
}

# Register the cleanup_and_exit function to run when SIGINT is received
trap cleanup_and_exit SIGINT


python tuntap_bridge.py --local-address $IP_ADDRESS/24 --interface $INTERFACE --baud $BAUDRATE --serial $SERIAL &
subprocess_pid=$!

sleep 3

# Add route to destination IP
sudo ip route add $DEST_IP dev $INTERFACE table 10
# Add rule to destinations table
sudo ip rule add table 10 pref 1
# Remove original local table
sudo ip rule del table local pref 0
# Add local table rule when INTERFACE is input interface
sudo ip rule add iif $INTERFACE pref 0 table local
# Add local table after us
sudo ip rule add table local pref 2

wait $subprocess_pid

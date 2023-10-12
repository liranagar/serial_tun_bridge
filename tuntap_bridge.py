import sys
import argparse
import ipaddress
import threading

import pytun
import serial

import data_manipulator

class TunSerialBridge:
    def __init__(self, serial: serial.Serial, interface: pytun.TunTapDevice,
                 manipulator: data_manipulator.DataManipulator):
        self.serial = serial
        self.interface = interface
        self.manipulator = manipulator

        self.serial.flushInput()
        self.serial.flushOutput()

    def tx_loop(self):
        while True:
            data = self.interface.read(2048)
            data = self.manipulator.tx(data)
            if data is not None:
                self.serial.write(data)

    def rx_loop(self):
        while True:
            data = self.serial.read_all()
            data = self.manipulator.rx(data)
            if data is not None:
                try:
                    self.interface.write(data)
                except pytun.Error as e:
                    print(e, file=sys.stderr)

    def start(self):
        tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        tx_thread.start()

        rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        rx_thread.start()

        tx_thread.join()
        rx_thread.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='/dev/ttyUSB0', metavar='PATH',
                        help='serial port path (default: ttyUSB0)')
    parser.add_argument('--baud', default=460800, type=int,
                        help='serial port baud rate (default: 460800)')
    parser.add_argument('--interface', default='tun0', metavar='NAME',
                        help='force interface name')
    parser.add_argument('--local-address', default='1.2.3.4/24',
                        type=ipaddress.IPv4Interface, metavar='ADDRESS/MASK', 
                        help='set local IP address and network mask')

    args = parser.parse_args()

    uart = serial.Serial(args.serial, args.baud, timeout=None)    
    
    interface = pytun.TunTapDevice(args.interface,
                                   flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
    interface.up()
    interface.addr = str(args.local_address.ip)
    interface.netmask = str(args.local_address.netmask)
    
    manipulator = data_manipulator.ExampleManipulator(b"\xAA\xBB")

    bridge = TunSerialBridge(uart, interface, manipulator)
    bridge.start()


if __name__ == '__main__':
    main()
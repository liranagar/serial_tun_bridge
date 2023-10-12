import struct

class DataManipulator:
    """Data manipulation before TX.

    Args:
        payload: data to manipulate.

    Returns:
        Manipulated data or None incase manipulation fails. 

    Example:
        result = tx(b"test")
        if result is not None:
            print(f"manipulated data {result}")
        else:
            print("No manipulation needed")
    """
    def tx(self, payload: bytes):
        if payload == b'':
            return None

        return payload
    
    """Data manipulation from RX.

    Args:
        payload: data to manipulate.

    Returns:
        Manipulated data or None incase manipulation fails. 

    Example:
        result = rx(b"test")
        if result is not None:
            print(f"manipulated data {result}")
        else:
            print("No manipulation needed")
    """   
    def rx(self, payload: bytes):
        if payload == b'':
            return None

        return payload
    

class ExampleManipulator(DataManipulator):
    
    LEN_WIDTH = 2
    
    def __init__(self, barker: bytes):
        self.barker = barker
        self.rx_data = b""
        self.barker_len = len(self.barker)
        
    def tx(self, payload):
        if payload == b'':
            return None

        payload_len = struct.pack('<H', len(payload))
        data = self.barker + payload_len + payload
        return data
    
    def rx(self, payload):
        if payload == b'':
            return None
        
        self.rx_data += payload
        index = self.rx_data.find(self.barker)
        if index == -1:
            return None
        
        index += self.barker_len
        data_len = int.from_bytes(self.rx_data[index : index + self.barker_len],
                                  "little")
        
        index += self.LEN_WIDTH
        if len(self.rx_data[index:]) >= data_len:
            output = self.rx_data[index : index + data_len]
            self.rx_data = self.rx_data[index + data_len:]
            return output

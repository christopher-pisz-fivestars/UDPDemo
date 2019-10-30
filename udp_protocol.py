from twisted.internet.protocol import DatagramProtocol


class UDPProtocol(DatagramProtocol):
    """
    Implements the Twisted Datagram Protocol enabling us to perform simple UDP send and receives
    """
    def __init__(self):
        pass

    def send(self, addr, port, data):
        """
        Send data to a particular address and port combination
        :param addr: address to send to
        :param port: port to send to
        :param data: data to send
        :return:
        """
        pass

    def datagramReceived(self, data, sender):
        """
        Override base class method
        :param data: data that was received
        :param sender: who sent it
        :return: None
        """
        pass

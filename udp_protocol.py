from twisted.internet.protocol import DatagramProtocol


class UDPProtocol(DatagramProtocol, object):
    """
    Implements the Twisted Datagram Protocol enabling us to perform simple UDP send and receives
    """
    def __init__(self, received_callback):
        self.received_callback = received_callback
        self._broadcast_allowed = False

    @property
    def allow_broadcast(self):
        """
        Gets whether or not we will be listening for broadcast messages
        :return: whether or not we will be listening for broadcast messages
        """
        return self._broadcast_allowed

    @allow_broadcast.setter
    def allow_broadcast(self, value):
        """
        Sets whether or not we will be listening for broadcast messages
        Note - This must be set before listening for it to take effect
        :param value: whether or not we will be listening for broadcast messages
        :return: None
        """
        self._broadcast_allowed = value

    def startProtocol(self):
        self.transport.setBroadcastAllowed(self._broadcast_allowed)

    def send(self, addr, port, data):
        """
        Send data to a particular address and port combination
        :param addr: address to send to
        :param port: port to send to
        :param data: data to send
        :return:
        """
        self.transport.write(data, (addr, port))

    def datagramReceived(self, data, (host, port)):
        """
        Override base class method
        :param data: data that was received
        :param sender: who sent it
        :return: None
        """
        print "received %r from %s:%d" % (data, host, port)
        self.received_callback(data, (host, port))

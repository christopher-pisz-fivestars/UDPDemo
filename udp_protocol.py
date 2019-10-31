from twisted.internet.protocol import DatagramProtocol


class UDPProtocol(DatagramProtocol):
    """
    Implements the Twisted Datagram Protocol enabling us to perform simple UDP send and receives
    """
    def __init__(self, received_callback):
        self.received_callback = received_callback

    def send(self, addr, port, data):
        """
        Send data to a particular address and port combination
        :param addr: address to send to
        :param port: port to send to
        :param data: data to send
        :return:
        """
        # TODO - What is the max length of the message?
        #        Doc mentions a MessageLengthError but give no limits
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

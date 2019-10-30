from udp_protocol import UDPProtocol
from twisted.internet.error import CannotListenError


class PluginBase(object):
    """
    This is just a dummy class to match what is in Falco
    """

    def __init__(self, app_dist, *args, **kwargs):
        pass


class Plugin(PluginBase):
    """
    This will be the plugin, in Falco
    """
#region Plugin interface specific
    DEPENDENCIES = {"required": ["config"]}

    def __init__(self, app_dist, *args, **kwargs):
        super(Plugin, self).__init__(app_dist, *args, **kwargs)
        self.port = None
        self.listener = None
        self.listen_callback = None

    def configure(self, config):
        pass

    def start(self, config):
        pass

    def stop(self):
        pass
#endregion

    def open(self, port, isBroadcast, callback, errback=None):
        """
        :param port: Port to listen on
        :param isBroadcast: TODO - Not sure is we are listeing to broadcasts or sending them
        :param callback - Called when listener was created successfully
        :param errback - Called when listener creation failed
        :return: None
        """
        if self.port is not None:
            raise RuntimeError("Already opened")
        self.port = port

        from twisted.internet import reactor

        # Stop listening if we were listening previously
        if self.listener is not None:
            self.listener.stopListening()
            self.listener = None

        # Start listening
        try:
            self.listener = reactor.listenUDP(self.port, UDPProtocol())
            callback()
        except CannotListenError as err:
            error_json = {"error": err[2].strerror}
            if errback is not None:
                errback(error_json)

    def listen(self, callback):
        """
        :param callback - Called when there is a message received
        :return: None
        """
        self.listen_callback = callback

    def stop_listening(self):
        """
        Stop listening for incoming messages and reset to a state as though we were just initialized
        :return:
        """
        if self.listener is not None:
            self.listener.stopListening()
            self.listener = None

        self.listen_callback = None
        self.port = None

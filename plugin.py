import sys
from enum import Enum
from twisted.internet.error import CannotListenError

from udp_protocol import UDPProtocol

# TODO - Log all errors when in Falco


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
    class State(Enum):
        """
        Represents the states that the plugin can be in
        """
        CLOSED = 0                     # Initial state
        LISTENING = 1                  # After open() is called
        RECV_CALLBACK_REGISTERED = 2   # After listen() is called

#region Plugin interface specific
    DEPENDENCIES = {"required": ["config"]}

    def __init__(self, app_dist, *args, **kwargs):
        super(Plugin, self).__init__(app_dist, *args, **kwargs)
        self.state = self.State.CLOSED
        self.port = None
        self.listener = None
        self.listen_callback = None
        self.protocol = UDPProtocol(self.on_data_received)

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
        :param isBroadcast: TODO - Not sure what to do with this. are we are listening to broadcasts
                                   or sending them?
        :param callback - Called when listener was created successfully
        :param errback - Called when listener creation failed
        :return: None
        """
        if self.state != self.State.CLOSED:
            raise RuntimeError("UDP Plugin already in an opened state")
        self.port = port

        error_json = None
        try:
            from twisted.internet import reactor
            self.listener = reactor.listenUDP(self.port, self.protocol)
            self.state = self.State.LISTENING
            callback()
        except CannotListenError as err:
            error_json = {"error": err[2].strerror}
        except RuntimeError as err:
            error_json = {"error": err.args[0]}
        except:
            error_json = {
                "error": "An unknown exception type was caught: %s" % format(sys.exc_info()[0])}
        finally:
            if error_json is not None and errback is not None:
                errback(error_json)

    def listen(self, callback, errback=None):
        """
        :param callback - Called when there is a message received
        :param errback - Called when registration of the callback failed
        :return: None
        """
        error_json = None
        try:
            if self.state != self.State.LISTENING:
                raise RuntimeError(
                    "UDP Plugin must be in an open state before registering callback with listen")
            self.listen_callback = callback
            self.state = self.State.RECV_CALLBACK_REGISTERED
        except RuntimeError as err:
            error_json = {"error": err.args[0]}
        except:
            error_json = {
                "error": "An unknown exception type was caught: %s" % format(sys.exc_info()[0])}
        finally:
            if error_json is not None and errback is not None:
                errback(error_json)

    def stop_listening(self):
        """
        Stop listening for incoming messages and reset to a state as though we were just initialized
        :return: None
        """
        if self.listener is not None:
            self.listener.stopListening()
            self.listener = None

        self.listen_callback = None
        self.port = None
        self.state = self.State.CLOSED

    def send(self, data, address, port, callback, errback=None):
        """
        Send a UDP message to the specified destination
        :param data: what is being sent to the destination
        :param address: IP address of the destination
        :param port: Port of the destination
        :param callback: Called when the message was successfully sent
        :param errback: Called when if there was an error while sending the message
        :return: None
        """
        error_json = None
        try:
            # While it seems like one could send without listening for incoming messages,
            # twisted's implementation doesn't seem to work that way?
            # The transport in the protocol object only gets created when we call reactor.listenUDP,
            # as far as I can tell
            if self.state == self.State.CLOSED:
                raise RuntimeError(
                    "UDP Plugin must be in an open state before attempting to send")

            self.protocol.send(address, port, data)
            callback()
        except RuntimeError as err:
            error_json = {"error": err.args[0]}
        except:
            error_json = {
                "error": "An unknown exception type was caught: %s" % format(sys.exc_info()[0])}
        finally:
            if error_json is not None and errback is not None:
                errback(error_json)


    def on_data_received(self, data, sender):
        udp_event = {
            "address": sender[0],
            "message": data,
            "port": sender[1]
        }
        if self.listen_callback is not None:
            self.listen_callback(udp_event)


import json
import threading
import time
import wx

from plugin import Plugin


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))
        self.CreateStatusBar()

        menu_file = wx.Menu()
        menu_item_exit = menu_file.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        menu_help = wx.Menu()
        menu_item_about = menu_help.Append(wx.ID_ABOUT, "&About", " Information about this program")

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, "&File")
        menu_bar.Append(menu_help, "&Help")
        self.SetMenuBar(menu_bar)

        self.panel = MainPanel(self)

        self.Bind(wx.EVT_MENU, self.on_about, menu_item_about)
        self.Bind(wx.EVT_MENU, self.on_exit, menu_item_exit)

        self.Show(True)

    def on_about(self, e):
        dlg = wx.MessageDialog(self, "A window to test UDP implementation", "About Test",
                               wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, e):
        self.Close(True)


class MainPanel(wx.Panel):
    def __init__(self, parent):
        self.doing_task_event_loop = False
        self.doing_task_callback = False
        self.listening = False

        wx.Panel.__init__(self, parent)

        # Read only Text Area
        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.horizontal_text = wx.BoxSizer()
        self.horizontal_text.Add(self.textbox, proportion=1, flag=wx.EXPAND)

        # Main Input controls
        self.listen_port_label = wx.StaticText(self, label="Listen Port")
        self.listen_port_text = wx.TextCtrl(self, size=(50, -1), value="5000")
        self.button_open = wx.Button(self, label="Open")
        self.button_listen = wx.Button(self, label="Listen")
        self.subhorizontal_inputs1 = wx.BoxSizer()
        self.subhorizontal_inputs1.Add(self.listen_port_label, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs1.Add(self.listen_port_text, 0, wx.RIGHT, 205)
        self.subhorizontal_inputs1.Add(self.button_open, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs1.Add(self.button_listen, 0, wx.RIGHT, 5)

        self.destination_ip_label = wx.StaticText(self, label="Destination IP")
        self.destination_ip_text = wx.TextCtrl(self, size=(150, -1), value="127.0.0.1")
        self.destination_port_label = wx.StaticText(self, label="Port")
        self.destination_port_text = wx.TextCtrl(self, size=(50, -1), value="5000")
        self.subhorizontal_inputs2 = wx.BoxSizer()
        self.subhorizontal_inputs2.Add(self.destination_ip_label, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs2.Add(self.destination_ip_text, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs2.Add(self.destination_port_label, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs2.Add(self.destination_port_text, 0, wx.RIGHT, 5)

        self.message_label = wx.StaticText(self, label="Message")
        self.message_text = wx.TextCtrl(self, size=(250, -1), value="Lorem ipsum dolor sit amet")
        self.button_send = wx.Button(self, label="Send")
        self.subhorizontal_inputs3 = wx.BoxSizer()
        self.subhorizontal_inputs3.Add(self.message_label, 0, wx.RIGHT, 15)
        self.subhorizontal_inputs3.Add(self.message_text, 0, wx.RIGHT, 5)
        self.subhorizontal_inputs3.Add(self.button_send, 0, wx.RIGHT, 5)

        self.vertical_input_controls = wx.BoxSizer(wx.VERTICAL)
        self.vertical_input_controls.Add(self.subhorizontal_inputs1, 0, wx.BOTTOM, 15)
        self.vertical_input_controls.Add(self.subhorizontal_inputs2, 0, wx.BOTTOM, 5)
        self.vertical_input_controls.Add(self.subhorizontal_inputs3, 0, wx.BOTTOM, 5)

        self.button_task_event_loop = wx.Button(self, label="Start task - event loop")
        self.vertical_extras = wx.BoxSizer(wx.VERTICAL)
        self.vertical_extras.Add(self.button_task_event_loop, 0, wx.ALIGN_RIGHT)

        self.horizontal_input_controls = wx.BoxSizer()
        self.horizontal_input_controls.Add(self.vertical_input_controls, 2, 0, 0)
        self.horizontal_input_controls.Add(self.vertical_extras, 1, 0, 0)

        # Main box
        self.vertical_main = wx.BoxSizer(wx.VERTICAL)
        self.vertical_main.Add(self.horizontal_text, 2, wx.EXPAND | wx.BOTTOM, 10)
        self.vertical_main.Add(self.horizontal_input_controls, 1, wx.LEFT, 10)
        self.SetSizerAndFit(self.vertical_main)

        # Binds and inits
        self.Bind(wx.EVT_BUTTON, self.on_click_button_task_event_loop, self.button_task_event_loop)
        self.Bind(wx.EVT_BUTTON, self.on_click_button_open, self.button_open)
        self.Bind(wx.EVT_BUTTON, self.on_click_button_listen, self.button_listen)
        self.Bind(wx.EVT_BUTTON, self.on_click_button_send, self.button_send)
        self.button_listen.Disable()
        self.textbox.AppendText('Panel created on thread: {}\n'.format(
            threading.current_thread().ident))

        self.udp_plugin = Plugin("notapplicable")

    def on_click_button_task_event_loop(self, event):
        if self.doing_task_event_loop:
            self.doing_task_event_loop = False
            self.button_task_event_loop.SetLabel('Start task - event loop')
            self.textbox.AppendText('Stopping long task in the event loop...\n')
        else:
            self.doing_task_event_loop = True
            self.button_task_event_loop.SetLabel('Stop task - event loop')
            self.textbox.AppendText('Starting long task in the event loop...\n')
            from twisted.internet import reactor
            reactor.callLater(0.25, self.long_task_event_loop)

    def on_click_button_open(self, event):
        self.button_open.Disable()

        # Start listening
        port = self.listen_port_text.GetValue()
        try:
            port = int(port)
        except ValueError:
            self.textbox.AppendText('Listen port was not a valid value. Try again.\n')
            self.listen_port_text.SetValue("")
            self.button_open.Enable()
            return

        self.udp_plugin.open(port, False, self.on_open, self.on_open_error)

    def on_click_button_listen(self, event):
        if not self.listening:
            self.udp_plugin.listen(self.on_message_received)
            self.listening = True
            self.button_listen.Label = "Stop Listening"
            self.textbox.AppendText('Registered receive callback.\n')
        else:
            self.udp_plugin.stop_listening()
            self.listening = False
            self.button_open.Enable()
            self.button_listen.Label = "Listen"
            self.button_listen.Disable()
            self.textbox.AppendText(
                'Closed Listener, unregistered callback, and set port to None.\n')

    def on_click_button_send(self, event):
        message = self.message_text.GetValue()
        address = self.destination_ip_text.GetValue()

        port = self.destination_port_text.GetValue()
        try:
            port = int(port)
        except ValueError:
            self.textbox.AppendText('Destination port was not a valid value. Try again.\n')
            self.listen_port_text.SetValue("")
            self.button_open.Enable()
            return

        self.udp_plugin.send(message, address, port, self.on_send, self.on_send_error)

    def long_task_event_loop(self):
        if self.doing_task_event_loop:
            time.sleep(0.33)
            from twisted.internet import reactor
            self.textbox.AppendText('Event loop task\n')
            reactor.callLater(0.25, self.long_task_event_loop)

    def on_open(self):
        self.textbox.AppendText('Open was successful\n')
        self.button_listen.Enable()

    def on_open_error(self, error_json):
        self.textbox.AppendText('Open failed:%s\n' % json.dumps(error_json))

    def on_message_received(self, udp_event):
        self.textbox.AppendText('a message was received:\n%s' % format(json.dumps(udp_event)))

    def on_listen_error(self, error_json):
        self.textbox.AppendText('Listen failed:%s\n' % json.dumps(error_json))

    def on_send(self):
        self.textbox.AppendText('Send was successful\n')

    def on_send_error(self, error_json):
        self.textbox.AppendText('Send failed:%s\n' % json.dumps(error_json))


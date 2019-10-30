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
        self.called_back_count = 0

        wx.Panel.__init__(self, parent)

        # Read only Text Area
        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.horizontal = wx.BoxSizer()
        self.horizontal.Add(self.textbox, proportion=1, flag=wx.EXPAND)

        # Buttons
        self.button_task_event_loop = wx.Button(self, label="Start task - event loop")
        self.button_open = wx.Button(self, label="Open")
        self.button_listen = wx.Button(self, label="Listen")
        self.horizontal2 = wx.BoxSizer()
        self.horizontal2.Add(self.button_task_event_loop, 0, wx.RIGHT, 5)
        self.horizontal2.Add(self.button_open, 0, wx.RIGHT, 5)
        self.horizontal2.Add(self.button_listen, 0, wx.RIGHT, 5)

        # Input controls
        self.listen_port_label = wx.StaticText(self, label="Listen Port")
        self.listen_port_text = wx.TextCtrl(self, size=(50, -1))
        self.horizontal3 = wx.BoxSizer()
        self.horizontal3.Add(self.listen_port_label, 0, wx.RIGHT, 5)
        self.horizontal3.Add(self.listen_port_text, 0, 0, 0)

        self.message_label = wx.StaticText(self, label="Message")
        self.message_text = wx.TextCtrl(self, size=(250, -1))
        self.horizontal4 = wx.BoxSizer()
        self.horizontal4.Add(self.message_label, 0, wx.RIGHT, 15)
        self.horizontal4.Add(self.message_text, 0, 0, 5)

        self.vertical_input_controls = wx.BoxSizer(wx.VERTICAL)
        self.vertical_input_controls.Add(self.horizontal3, 0, wx.BOTTOM, 5)
        self.vertical_input_controls.Add(self.horizontal4, 0, 0, 0)

        # Main box
        self.sizer_vertical_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_vertical_main.Add(self.horizontal, 2, wx.EXPAND, 0)
        self.sizer_vertical_main.Add(self.horizontal2, 0, wx.ALIGN_CENTER, 0)
        self.sizer_vertical_main.Add(self.vertical_input_controls, 1, 0, 0)
        self.SetSizerAndFit(self.sizer_vertical_main)

        # Binds and inits
        self.Bind(wx.EVT_BUTTON, self.on_click_button_task_event_loop, self.button_task_event_loop)
        self.Bind(wx.EVT_BUTTON, self.on_click_button_open, self.button_open)
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
            # TODO - Reset the text and message
            pass

        self.udp_plugin.open(port, False, self.on_open, self.on_open_error)
        self.udp_plugin.listen("poop")

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

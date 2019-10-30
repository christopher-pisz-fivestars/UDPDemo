import wx
from twisted.internet import wxreactor
from main_window import MainWindow


def main():
    app = wx.App(False)
    frame = MainWindow(None, 'UDP Demo')

    from twisted.internet import reactor
    reactor.registerWxApp(app)
    reactor.run()


if __name__ == "__main__":
    wxreactor.install()
    main()

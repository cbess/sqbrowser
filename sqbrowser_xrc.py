# This file was automatically generated by pywxrc.
# -*- coding: UTF-8 -*-

import wx
import wx.xrc as xrc

__res = None

def get_resources():
    """ This function provides access to the XML resources in this module."""
    global __res
    if __res == None:
        __init_resources()
    return __res




class xrcfrmMain(wx.Frame):
#!XRCED:begin-block:xrcfrmMain.PreCreate
    def PreCreate(self, pre):
        """ This function is called during the class's initialization.
        
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass
        
#!XRCED:end-block:xrcfrmMain.PreCreate

    def __init__(self, parent):
        # Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
        pre = wx.PreFrame()
        self.PreCreate(pre)
        get_resources().LoadOnFrame(pre, parent, "frmMain")
        self.PostCreate(pre)

        # Define variables for the controls, bind event handlers
        self.txtSqlDb = xrc.XRCCTRL(self, "txtSqlDb")
        self.btOpenSqlDb = xrc.XRCCTRL(self, "btOpenSqlDb")
        self.txtSqlFile = xrc.XRCCTRL(self, "txtSqlFile")
        self.btOpenSqlFile = xrc.XRCCTRL(self, "btOpenSqlFile")
        self.chkMonitorFile = xrc.XRCCTRL(self, "chkMonitorFile")
        self.btExecuteFile = xrc.XRCCTRL(self, "btExecuteFile")
        self.btCommit = xrc.XRCCTRL(self, "btCommit")
        self.lstResults = xrc.XRCCTRL(self, "lstResults")
        self.txtMessages = xrc.XRCCTRL(self, "txtMessages")

        self.Bind(wx.EVT_CLOSE, self.OnClose)

#!XRCED:begin-block:xrcfrmMain.OnClose
    def OnClose(self, evt):
        # Replace with event handler code
        print "OnClose()"
#!XRCED:end-block:xrcfrmMain.OnClose        




# ------------------------ Resource data ----------------------

def __init_resources():
    global __res
    __res = xrc.EmptyXmlResource()

    __res.Load('sqbrowser.xrc')

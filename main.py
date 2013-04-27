#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Christopher Bess on 2009-03-15.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import mainwin
import wx

def main():
    app = wx.App()
    frame = mainwin.MainWin()
    frame.Show()
    app.MainLoop()
    pass

if __name__ == '__main__':
	main()


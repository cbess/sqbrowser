#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Christopher Bess on 2009-03-15.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import wx
import os
import sys
# add libs dir to py paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
import mainwin


def main():
    app = wx.App()
    frame = mainwin.MainWin()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()


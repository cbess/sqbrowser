#!/usr/bin/env python
# encoding: utf-8
"""
mainwin.py

Created by Christopher Bess on 2009-03-22.
Copyright (c) 2009 Qu. All rights reserved.

coding guidelines:
http://wxpython.org/codeguidelines.php
"""

import os
import stat  # index constants for os.stat()
import time
from libs import sqlbase
from libs import path
from libs.config import Config
import sys
import re
try:
    import ipdb
    set_trace = ipdb.set_trace
except ImportError:
    import pdb
    set_trace = pdb.set_trace
import codecs
import cPickle as pickle
import wx
import sqbrowser_xrc


## start query (optional)
QUERY_START = (
    "-- returns",
    "--returns"
)
## stop query parse
QUERY_STOP = (
    "--return", 
    "-- return", 
    "__return__"
)

## executes all queries within the query stop (semi-colon delimited)
# regex, if matched then exec all queries
EXEC_ALL = re.compile(r"--(\s|)all").match

# max column count to auto size
# if column count > AUTOSIZE_COLUMNS, then no auto col. sizing
AUTOSIZE_COLUMNS = 5


class MainWin(sqbrowser_xrc.xrcfrmMain):
    """Represents the main query browser window
    """
    configPath = os.path.join(os.path.dirname(__file__), 'app.cfg')

    def __init__(self):
        """__init__
        """
        sqbrowser_xrc.xrcfrmMain.__init__(self, None)
        self.SetSize((650, 500))
        
        # setup the control events
        self.btOpenSqlFile.Bind(wx.EVT_BUTTON, self.btOpenSqlFile_Click)
        self.btOpenSqlDb.Bind(wx.EVT_BUTTON, self.btOpenSqlDb_Click)
        self.btExecuteFile.Bind(wx.EVT_BUTTON, self.btExecuteFile_Click)
        self.btCommit.Bind(wx.EVT_BUTTON, self.btCommit_Click)
        # setup timers
        self._interval = 2  # seconds
        self.tmrCheckFile = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmrCheckFile_Tick, self.tmrCheckFile)
        # file operation vars
        self.file = None
        self._lastCheckTime = None
        # status bar
        self.CreateStatusBar()
        self.SetStatusText("SQBrowser")
        # setup sqlengine
        self._sqlEngine = None
        # misc setup
        self.config = Config(self.configPath)
        self.config.load()
        self.StartTimer()
        if self.config.db_path:
            self.txtSqlDb.SetValue(self.config.db_path)
        if self.config.src_path:
            self.txtSqlFile.SetValue(self.config.src_path)

## EVENTS METHODS
    
    def OnClose(self, evt):
        """OnClose
        @remark: overriden from base class
        """
        if self._sqlEngine:
            self._sqlEngine.disconnect()
        # use default close action
        evt.Skip()

    def btOpenSqlFile_Click(self, evt):
        """btOpenSqlFile_Click
        """
        path = self._openFileDialog(msg="Select the query file")
        if not path:
            return 
        self.config.src_path = path
        self.config.save()
        self.txtSqlFile.SetValue(path)

    def btOpenSqlDb_Click(self, evt):
        """btOpenSqlDb_Click
        """
        path = self._openFileDialog(msg="Select the data source")
        if not path:
            return
        self._clearLog()
        self.config.db_path = path
        self.config.save()
        self.txtSqlDb.SetValue(path)

    def tmrCheckFile_Tick(self, evt):
        """tmrServer_Tick
        """
        if self.chkMonitorFile.IsChecked():
            self.SetStatusText("Monitoring file...")
        else:
            self.SetStatusText("SQBrowser")
            return
        self.StopTimer()
        self._executeSqlFile()
        self.StartTimer()

    def btExecuteFile_Click(self, evt):
        """btExecuteFile_Click
        """
        self._executeSqlFile(force_execute=True)

    def btCommit_Click(self, evt):
        """btCommit_Click
        """
        if not self._sqlEngine:
            return
        self._sqlEngine.commit()
        self._addLog("Changes committed...")

## MISC METHODS

    def _executeSqlFile(self, force_execute=False):
        """executeSqlFile
        """
        path = self.txtSqlFile.GetValue()
        if not os.path.isfile(path):
            self._addLog("Not a file: "+path)
            return
            
        dbPath = self.txtSqlDb.GetValue()
        hasChanged = self._checkFile(path)
        now = wx.DateTime().Now().Format()
        
        if hasChanged:
            self._addLogSplit()
            self._addLog("File Changed: "+now)
        elif not hasChanged:
            if not force_execute:
                return            
        
        # setup the engine
        self._sqlEngine = sqlbase.SqlBase(dbPath)
        if not self._sqlEngine.connect():
            self._addLog("Unable to connect to: "+dbPath)
            return
        
        # get contents of sql file
        contents = self._readContents(path)
        
        # get the query
        query = self._parseQuery(contents)

        self._addLogSplit()

        # exec all queries, semi-colon separated
        queries = [query]
        if EXEC_ALL(query) is not None:
            queries = query.split(";")
            # beseech user
            msg = "Run %d queries?" % len(queries)
            if wx.MessageBox(message=msg, style=wx.YES | wx.NO) == wx.NO:
                self._addLog("Multi-query operation aborted.")
                return
            self._addLog("Running %d queries..." % len(queries))
            
        # execute the queries

        results = {}
        for query in queries:
            self._addLog(query.strip())
            results = self._sqlEngine.execute_query(query)
            if not results:
                self._addLog("SQL ERROR: "+self._sqlEngine.last_error)
                return
                
            self._addLog(results['message'])

        ## display the result data in the table
        
        # insert columns
        self._rebuildColumns(results['columns'])
        # insert rows
        for row in results['rows']:
            self._addRow(row)
        self._resizeColumns(results['columns'])

    def _parseQuery(self, sql):
        """Parses the sql to only show the target query
        @remark: it stops at the first 'query stop' place holder
        @return string the query to execute
        """
        lines = sql.split('\n')
        hasQueryStart = False

        for start in QUERY_START:
            if sql.find(start) >= 0:
                hasQueryStart = True
                break
        doStart = False
        query = ""
        
        for line in lines:
            sLine = line.strip()
            
            # if flag seen, start grabbing
            if not hasQueryStart or doStart:
                # if no starter, then grab until eof
                query += line + "\n"
                
            if sLine in QUERY_START:
                # start grabbing from next line on
                doStart = True  
            
            if not hasQueryStart or doStart:
                if sLine in QUERY_STOP:
                    # done, return query, remove the query stop
                    query = query.replace(sLine, "")
                    break
        return query.strip()
        
    def _addLogSplit(self):
        """Adds an output separator to the log
        """
        count = 70
        self._addLog("-" * count)

    def _addLog(self, msg):
        """Adds a line of text to the output console
        """
        self.txtMessages.AppendText(msg+"\n")

    def _clearLog(self):
        """Clears the output log
        """
        self.txtMessages.Clear()

    def StartTimer(self):
        self.StopTimer()
        self.tmrCheckFile.Start(self._interval * 1000)

    def StopTimer(self):
        self.tmrCheckFile.Stop()

    def _openFileDialog(self, msg="Select the file", path=""):
        """Displays the open file dialog
        """
        path = wx.FileSelector(
            message=msg,
            default_path=path,
            parent=self
        )
        return path
        
    def _rebuildColumns(self, columns):
        """Rebuilds the list ctrl
        @remarks: Deletes all columns and rows
        """
        # remove all cols and rows
        self.lstResults.ClearAll()      
        
        # insert the columns into the header
        for col, text in enumerate(columns):
            self.lstResults.InsertColumn(col, text)

    def _resizeColumns(self, columns):
        """Resizes the columns
        """
        doAutoSize = (len(columns) <= AUTOSIZE_COLUMNS)
        # insert the columns into the header
        if doAutoSize:
            for col, text in enumerate(columns):
                self.lstResults.SetColumnWidth(col, wx.LIST_AUTOSIZE)

    def _addRow(self, row):
        """addRow
        """        
        count = self.lstResults.GetItemCount()
        idx = 0
        for col, col_value in enumerate(row):
            if col == 0:
                idx = self.lstResults.InsertStringItem(sys.maxint, str(count))
            self.lstResults.SetStringItem(idx, col, unicode(col_value))

## FILE CHECK METHODS

    def _checkFile(self, filePath):
        """Checks the modification date for the specified file path
        """
        if not os.path.isfile(filePath):
            return False
        
        hasFileChanged = False
        
        # get file info
        fileStats = os.stat(filePath)
        lastMod = time.localtime(fileStats[stat.ST_MTIME])
        
        # create a dictionary to hold file info
        file_info = {
            'fname': filePath,
            'fsize': fileStats[stat.ST_SIZE],
            # last modified
            'f_lm': time.strftime("%m/%d/%Y %I:%M:%S %p", lastMod),
            # last accessed
            'f_la': time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(fileStats[stat.ST_ATIME])),
            # creation time
            'f_ct': time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(fileStats[stat.ST_CTIME]))
        }
        
        # get the datetime object of the file modification time
        lastModTime = wx.DateTime()
        lastModTime.ParseDateTime(file_info['f_lm'])
    
        if self._lastCheckTime is None:
            self._lastCheckTime = wx.DateTime().Now()
        
        # make sure it is after the last checked time
        if lastModTime.IsLaterThan(self._lastCheckTime):
            hasFileChanged = True
        
        # get the last mod time
        self._lastCheckTime = lastModTime
        return hasFileChanged
        
    def _readContents(self, path):
        """read_contents
        """
        if not os.path.isfile(path):
            return None
        # get the file contents
        with codecs.open(path, "r", encoding="utf-8") as fp:
            contents = fp.read()
        return contents
        
# end CLASS


def main():
    app = wx.App()
    frame = MainWin()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()



#!/usr/bin/env python
# encoding: utf-8
"""
mainwin.py

Created by Christopher Bess on 2009-03-22.
Copyright (c) 2009 Qu. All rights reserved.
"""

import wx
import sqbrowser_xrc
import os
import stat  # index constants for os.stat()
import time
import sqlbase
import sys
import re
import ipdb
import codecs


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
    """Represents the main SQL browser window
    """
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
        self._interval = 2 # seconds
        self.tmrCheckFile = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tmrCheckFile_Tick, self.tmrCheckFile)
        # file operation vars
        self.file = None
        self.last_check_time = None
        # status bar
        self.CreateStatusBar()
        self.SetStatusText("SQBrowser")
        # setup sqlengine
        self.sql_engine = None
        # misc setup
        self.StartTimer()
        self.txtSqlDb.SetValue("")
        self.txtSqlFile.SetValue("")
        pass
    
## EVENTS METHODS
    
    def OnClose(self, evt):
        """OnClose
        @remark: overriden from base class
        """
        if self.sql_engine:
            self.sql_engine.disconnect()
        
        # use default close action
        evt.Skip()
        pass
        
    def btOpenSqlFile_Click(self, evt):
        """btOpenSqlFile_Click
        """
        path = self.openFileDialog(msg="Select the SQL source file")
        self.txtSqlFile.SetValue(path)
        pass
        
    def btOpenSqlDb_Click(self, evt):
        """btOpenSqlDb_Click
        """
        path = self.openFileDialog(msg="Select the SQL DB")
        if path:
            self.clearLog()
        self.txtSqlDb.SetValue(path)
        pass
        
    def tmrCheckFile_Tick(self, evt):
        """tmrServer_Tick
        """
        if self.chkMonitorFile.IsChecked():
            self.SetStatusText("Monitoring file...")
        else:
            self.SetStatusText("SQBrowser")
            return
        self.StopTimer()
        self.executeSqlFile()
        self.StartTimer()
        pass
        
    def btExecuteFile_Click(self, evt):
        """btExecuteFile_Click
        """
        self.executeSqlFile(force_execute=True)
        pass
    
    def btCommit_Click(self, evt):
        """btCommit_Click
        """
        if not self.sql_engine:
            return
        self.sql_engine.commit()
        self.addLog("Changes committed...")
        pass
        
## MISC METHODS

    def executeSqlFile(self, force_execute=False):
        """executeSqlFile
        """
        path = self.txtSqlFile.GetValue()
        if not os.path.isfile(path):
            self.addLog("Not a file: "+path)
            return
            
        db_path = self.txtSqlDb.GetValue()
        has_changed = self.check_file(path)
        now = wx.DateTime().Now().Format()
        
        if has_changed:
            self.addLogSplit()
            self.addLog("File Changed: "+now)
        elif not has_changed:
            if not force_execute:
                return            
        
        # setup the engine
        self.sql_engine = sqlbase.SqlBase(db_path)        
        if not self.sql_engine.connect():
            self.addLog("Unable to connect to: "+db_path)
            return
        
        # get contents of sql file
        contents = self.read_contents(path)
        
        # get the query
        query = self.parse_query(contents)

        self.addLogSplit()

        # exec all queries, semi-colon separated
        queries = [query]
        if EXEC_ALL(query) is not None:
            queries = query.split(";")
            # beseech user
            msg = "Execute %d queries?" % len(queries)
            if wx.MessageBox(message=msg, style=wx.YES|wx.NO) == wx.NO:
                self.addLog("Multi-query operation aborted.")
                return
            self.addLog("Executing %d queries..." % len(queries))
            
        # execute the queries

        for query in queries:
            self.addLog(query.strip())
            results = self.sql_engine.execute_query(query)
            if not results:
                self.addLog("SQL ERROR: "+self.sql_engine.last_error)
                return
                
            self.addLog(results['message'])
            pass
            
        ## display the result data in the table
        
        # insert columns
        self.rebuildColumns(results['columns'])
        # insert rows
        for row in results['rows']:
            self.addRow(row)
        self.resizeColumns(results['columns'])
        pass
        
    def parse_query(self, sql):
        """Parses the sql to only show the target query
        @remark: it stops at the first 'query stop' place holder
        @return string the query to execute
        """
        idx = 0
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
            pass
        return query.strip()
        
    def addLogSplit(self):
        """Adds an output separator to the log
        """
        count = 70
        self.addLog("-" * count)
        pass
        
    def addLog(self, msg):
        """Adds a line of text to the output console
        """
        self.txtMessages.AppendText(msg+"\n")
        pass
        
    def clearLog(self):
        """Clears the output log
        """
        self.txtMessages.Clear()
        pass

    def StartTimer(self):
        self.StopTimer()
        self.tmrCheckFile.Start(self._interval * 1000)
        pass

    def StopTimer(self):
        self.tmrCheckFile.Stop()
        pass
        
    def openFileDialog(self, msg="Select the file", path=""):
        """Displays the open file dialog
        """
        path = wx.FileSelector(
            message=msg,
            default_path=path,
            parent=self
        )
        return path
        
    def rebuildColumns(self, columns):
        """Rebuilds the list ctrl
        @remarks: Deletes all columns and rows
        """
        # remove all cols and rows
        self.lstResults.ClearAll()      
        
        # insert the columns into the header
        for col, text in enumerate(columns):
            self.lstResults.InsertColumn(col, text)
        pass
        
    def resizeColumns(self, columns):
        """Resizes the columns
        """
        doAutoSize = (len(columns) <= AUTOSIZE_COLUMNS)
        # insert the columns into the header
        if doAutoSize:
            for col, text in enumerate(columns):
                self.lstResults.SetColumnWidth(col, wx.LIST_AUTOSIZE)
        pass
        
    def addRow(self, row):
        """addRow
        """        
        count = self.lstResults.GetItemCount()
        idx = 0
        for col, col_value in enumerate(row):
            if col == 0:
                idx = self.lstResults.InsertStringItem(sys.maxint, str(count))
            self.lstResults.SetStringItem(idx, col, str(col_value))
        pass
        
## FILE CHECK METHODS

    def check_file(self, file_path):
        """Checks the modification date for the specified file path
        """
        if not os.path.isfile(file_path):
            return False
        
        has_file_changed = False
        
        # get file info
        file_stats = os.stat(file_path)
        last_mod = time.localtime(file_stats[stat.ST_MTIME])
        
        # create a dictionary to hold file info
        file_info = {
           'fname': file_path,
           'fsize': file_stats[stat.ST_SIZE],
           # last modified
           'f_lm': time.strftime("%m/%d/%Y %I:%M:%S %p", last_mod),
           # last accessed
           'f_la': time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(file_stats[stat.ST_ATIME])),
           # creation time
           'f_ct': time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(file_stats[stat.ST_CTIME]))
        }
        
        # get the datetime object of the file modification time
        last_mod_time = wx.DateTime()
        last_mod_time.ParseDateTime(file_info['f_lm'])
    
        if self.last_check_time is None:
            self.last_check_time = wx.DateTime().Now()
        
        # make sure it is after the last checked time
        if last_mod_time.IsLaterThan(self.last_check_time):
            has_file_changed = True
        
        # get the last mod time
        self.last_check_time = last_mod_time
        return has_file_changed
        
    def read_contents(self, path):
        """read_contents
        """
        if not os.path.isfile(path):
            return None
        contents = ""
        # get the file contents
        fp = codecs.open(path, "r", encoding="utf-8")
        contents = fp.read() 
        fp.close()
        return contents
        
# end CLASS
    
def main():
    app = wx.PySimpleApp()
    frame = MainWin()
    frame.Show()
    app.MainLoop()
    pass

if __name__ == '__main__':
	main()



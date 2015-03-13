# SQBrowser

SQLite3 query browser that can be used with any text editor.

Uses wxPython 2.8+ to provide a UI for sqlite database query results. It is different from other SQLite database managers, because it only displays results. This allows you to use your favorite SQL editor to execute SQL queries against the database.

It uses file monitoring to execute the query upon save and then update the results.

![screenshot](http://1.bp.blogspot.com/_pVeh7_7SuSg/SxxflsbAKAI/AAAAAAAAACs/ukjFeOLrluE/s320/sqbrowser-screenshot.png)

## Setup/Usage

1. Grab the code from git
1. execute: `python main.py`
1. Set the **db** file
1. Set the **SQL** file
1. Open the SQL file in your favorite editor, modify it
1. Click Execute SQL or tick the Autorun SQL file

## Notes

- It logs all queries in the bottom of the window
- Click Commit to commit changes to the DB
- You are able to execute defined blocks of SQL code (see example below)

```sql
--returns
SQL CODE HERE (only this block is executed)
--return
SQL CODE HERE
--return
```

## License

GPL v3

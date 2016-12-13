import sqlite3
import os

#__file__ = "c:\users\shawn\documents\\visual studio 2015\Projects\mtgelo\mtgelo\mtgelo\database.py"

def connect_db():
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'db\playerhistory.db')
    return sqlite3.connect(filename)

def delete_db():
    conn = connect_db()
    c = conn.cursor()
    c.executescript('drop table if exists playerHistory')
    conn.close()

def create_db():
    conn = connect_db()
    c = conn.cursor()
    #c.executescript('drop table if exists playerHistory')
    c.executescript('''create table playerHistory(
                                event text,
                                day text,
                                date text,
                                round text,
                                matchtable text,
                                playername text,
                                playercountry text,
                                result text,
                                vs text,
                                opponentname text,
                                opponentcountry text,
                                CONSTRAINT uniquevalues UNIQUE (event,round,matchtable,playername,opponentname)
                                )''')
    conn.close()

def playerHistoryToDB(playerHistory):
    #print playerHistory
    conn = connect_db()
    c = conn.cursor()
    for item in playerHistory:
            print "ADDING"
            print item
            if (len(item) != 11):
                print "BAD ITEM!!!!"
            else:
                c.execute('insert or replace into playerHistory values (?,?,?,?,?,?,?,?,?,?,?)', item)
    conn.commit()
    conn.close()
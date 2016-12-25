import sqlite3
import os

__file__ = "c:\users\shawn\documents\\visual studio 2015\Projects\mtgelo\mtgelo\mtgelo\database.py"

def reset_db():
    __file__ = "c:\users\shawn\documents\\visual studio 2015\Projects\mtgelo\mtgelo\mtgelo\database.py"
    delete_db()
    create_db()

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
                                coverageid num,
                                eventid num,
                                roundid num,
                                rowid num,
                                eventtype text,
                                eventname text,
                                date text,
                                round text,
                                matchtable text,
                                playerfirstname text,
                                playerlastname text,
                                playercountry text,
                                result text,
                                opponentfirstname text,
                                opponentlastname text,
                                opponentcountry text,
                                won text,
                                lost text,
                                drew text,
                                constraint unique_row unique (coverageid,eventid,roundid,rowid)
                                )''')
    conn.close()

def playerHistoryToDB(playerHistory):
    #print playerHistory
    conn = connect_db()
    c = conn.cursor()
    print ("ADDING", playerHistory)
    if (len(playerHistory) != 19):
        print "BAD ITEM!!!!"
    else:
        c.execute('insert or replace into playerHistory values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', playerHistory)
    conn.commit()
    conn.close()
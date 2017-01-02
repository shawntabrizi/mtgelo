import sqlite3
import os
from mtgelo.scraper.unicode_parser import *

__file__ = "C:\\Users\shawn\PycharmProjects\mtgelo\mtgelo\scraper\database.py"


def reset_db():
    delete_db()
    create_db()


def connect_db():
    file_dir = os.path.dirname(__file__)
    filename = os.path.join(file_dir, '..\db\playerhistory.db')
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
                                modified text,
                                constraint unique_row unique (coverageid,eventid,roundid,rowid)
                                )''')
    conn.close()


def create_playerranking():
    conn = connect_db()
    c = conn.cursor()
    c.executescript('drop table if exists playerRank')
    c.executescript('''create table playerRank(
                                playername text,
                                rating NUMERIC ,
                                sigma NUMERIC,
                                count NUMERIC,
                                mtgelo NUMERIC,
                                tsrating NUMERIC
                                )''')
    conn.close()


def playerHistoryToDB(playerHistory):
    #print playerHistory
    conn = connect_db()
    c = conn.cursor()
    print("ADDING", playerHistory)
    if (len(playerHistory) != 20):
        print("BAD ITEM!!!!")
    else:
        c.execute('insert or replace into playerHistory values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', playerHistory)
    conn.commit()
    conn.close()


def playerRankToDB(player_ratings):
    # print playerHistory
    conn = connect_db()
    c = conn.cursor()
    print("Adding")
    c.executemany('insert into playerRank values (?,?,?,?,?,?)',
                  player_ratings)
    conn.commit()
    conn.close()


def dbNormalizeNames():
    conn = connect_db()
    c = conn.cursor()
    c.execute('select * FROM playerHistory')
    db = c.fetchall()
    strip_db = [[strip_accents(item.lower()) if isinstance(item, str) else item for item in row] for row in db]
    c.executemany("""REPLACE into playerHistory VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", strip_db)
    conn.commit()
    conn.close()

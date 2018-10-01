import datetime, sqlite3
from shutil import copy

db = sqlite3.connect('umikobot.db')


def get_keys(table):
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT key FROM {} ORDER BY key'.format(table))
    all_keys = cursor.fetchall()
    return [k[0] for k in all_keys]


def db_add(table, key, text):
    cursor = db.cursor()
    cursor.execute('INSERT INTO {} (key,text) values(\'{}\', \'{}\')'.format(table, key, text))
    db.commit()
    return 'Successfully added {} to {}!'.format(key, table)


def db_delete(table, key):
    copy('umikobot.db',
         'umikobot.{}_{}.db'.format(datetime.datetime.now().date(), datetime.datetime.now().strftime('%Hh%Mm%Ss')))
    cursor = db.cursor()
    cursor.execute('DELETE FROM {} WHERE key = \'{}\''.format(table, key))
    db.commit()
    return 'Successfully removed {} from {}!'.format(key, table)


def db_retrieve(table, key):
    if key in get_keys(table):
        cursor = db.cursor()
        cursor.execute('SELECT text FROM {} WHERE key=\'{}\''.format(table, key))
        return cursor.fetchone()[0]

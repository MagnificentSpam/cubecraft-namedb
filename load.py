import sqlite3, time, re, argparse
from requests_html import HTMLSession


LOGIN_DATA = {'login': 'wn37t6cfkwwtyiruayniug@mailinator.com', 'password': 'P4yXtxfSXgGm67SHMFSrpV'}
CREATE_NAME_TABLE = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    playername TEXT,
    joined TEXT,
    messages INTEGER
)'''
CREATE_OLDNAMES_TABLE = '''
CREATE TABLE IF NOT EXISTS oldnames (
    user_id INTEGER ,
    name TEXT,
    PRIMARY KEY (user_id, name),
    FOREIGN KEY (user_id) REFERENCES users (id)
)'''
INSERT_USER_STATEMENT = 'INSERT OR REPLACE INTO users (id, name, playername, joined, messages) VALUES (?, ?, ?, ?, ?)'
INSERT_OLDNAME_STATEMENT = 'INSERT OR REPLACE INTO oldnames (user_id, name) VALUES (?, ?)'

parser = argparse.ArgumentParser(description='tool to create database containing the names of forum users')
parser.add_argument('start_id', type=int)
parser.add_argument('end_id', type=int)
parser.add_argument('--delay', type=int, default=50, help='delay between queries in ms')
args = parser.parse_args()

session = HTMLSession()
session.post('https://www.cubecraft.net/login/login', data=LOGIN_DATA)

db_conn = sqlite3.connect('users.db', detect_types=sqlite3.PARSE_DECLTYPES)

with db_conn:
    db_conn.execute(CREATE_NAME_TABLE)
    db_conn.execute(CREATE_OLDNAMES_TABLE)

for i in range(args.start_id, args.end_id):
    time.sleep(args.delay / 1000)
    with db_conn:
        user_profile = session.get('https://www.cubecraft.net/members/{}/'.format(i))
        if user_profile.status_code != 200:
            continue
        name = user_profile.html.find('.username', first=True).text.split('\n')[0]
        progress = (i - args.start_id) / (args.end_id - args.start_id)
        print('{:.2f}% - {}'.format(progress * 100, name))
        playername_html = user_profile.html.find('.playerUsername', first=True)
        playername = playername_html.text if playername_html is not None else None
        infoblock_html = user_profile.html.find('.infoBlock dl dd')
        joined = infoblock_html[1].text
        messages = int(re.sub(r'\D', '', infoblock_html[2].text))
        db_conn.execute(INSERT_USER_STATEMENT, [i, name, playername, joined, messages])
        previous_names = set()
        for name_change in user_profile.html.find('#usernameHistory div ul li'):
            change = name_change.search('On <b>{time}</b> the username was changed from <b>{from}</b> to <b>{to}</b>.')
            previous_names.add(change['from'])
        previous_names.discard(name)
        for oldname in previous_names:
            db_conn.execute(INSERT_OLDNAME_STATEMENT, [i, oldname])


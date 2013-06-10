import sqlite3

import game

DB_NAME = "pmx_game.db"

CREATE_TABLES = ( 
"CREATE TABLE IF NOT EXISTS player "
"(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, nick TEXT, x INT, y INT);",
"CREATE TABLE IF NOT EXISTS world_section "
"(id INTEGER PRIMARY KEY AUTOINCREMENT, player INT, x INT, y INT, section INT);",
"CREATE TABLE IF NOT EXISTS inventory "
"(id INTEGER PRIMARY KEY AUTOINCREMENT, player INT, item INT);",
"CREATE TABLE IF NOT EXISTS world_items "
"(id INTEGER PRIMARY KEY AUTOINCREMENT, world_section INT, item INT);",
)

def create_tables():
    """Create all the tables for the game. Won't overwrite existing tables."""
    for statement in CREATE_TABLES:
        run_command(statement)

def run_command(command, args=()):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        with conn:
            cursor = conn.cursor()
            cursor.execute(command, args)

            return cursor.fetchall()
    except sqlite3.Error, e:
        print "SQL Error %s:" % e.args[0]

def create_player(nick, name=None):
    rows = run_command("SELECT * FROM player WHERE nick=?", (nick, ))
    if rows:
        return "%s already exists!" % (nick, )

    if not name:
        name = nick

    run_command("INSERT INTO player (name, status, nick, x, y) "
        "VALUES (?, 'SLEEPING', ?, -1, -1)",
        (name, nick, )
    )
    return "%s is now %s" % (nick, get_status(nick))
def get_player(nick):
    rows = run_command("SELECT * FROM player WHERE nick=?", (nick,))
    if not rows:
        return None
    else:
        return rows[0]

def get_status(nick):
    player = get_player(nick)
    if player:
        return player['status']
    else:
        return "MISSING"

def update_status(nick, status):
    run_command("UPDATE player SET status=?", (status, ))

def get_location(nick):
    player = get_player(nick)
    section_rows = run_command(
        "SELECT * FROM world_section WHERE player=? AND x=? AND y=?", 
        (player['id'], player['x'], player['y'])
    )
    if not section_rows:
        return None
    else:
        return section_rows[0]

def set_location(nick, x, y):
    run_command("UPDATE player SET x=?, y=? WHERE nick=?", (x, y, nick,))

def get_world_items(location_id):
    return run_command("SELECT * FROM world_items WHERE world_section = ?", (location_id, ))

def wipe_world(player_id):
    run_command("DELETE FROM world_section WHERE player = ?", (player_id, ))

def wipe_inventory(player_id):
    run_command("DELETE FROM inventory WHERE player = ?", (player_id, ))

def get_inventory(nick):
    player = get_player(nick)
    return run_command("SELECT * FROM inventory WHERE player = ?", (player['id'], ))

def add_to_inventory(nick, item):
    player = get_player(nick)
    run_command("INSERT INTO inventory (player, item) VALUES (?, ?)",
        (player['id'], item)
    )

def remove_from_inventory(nick, item):
    player = get_player(nick)
    run_command("DELETE FROM inventory WHERE player=? AND item=?",
        (player['id'], item)
    )

def create_world_section(player_id, section, x, y):
    run_command("INSERT INTO world_section (player, section, x, y) VALUES (?, ?, ?, ?)",
        (player_id, section, x, y)
    )
def get_world_section(player_id, x, y):
    rows = run_command("SELECT * FROM world_section WHERE player=? AND x=? AND y=?",
        (player_id, x, y),
    )
    if rows:
        return rows[0]
    else:
        return None

def create_world_item(location_id, item):
    run_command("INSERT INTO world_items (world_section, item) VALUES (?, ?)", 
        (location_id, item),
    )
def remove_world_item(item_id):
    run_command("DELETE FROM world_items WHERE id=?", 
        (item_id, )
    )

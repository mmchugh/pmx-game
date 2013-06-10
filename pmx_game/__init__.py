from pmxbot.core import command

import sql, game

def parse_action(command_str):
    if command_str == 'north' or command_str == 'move north':
        return ('north', )
    if command_str == 'south' or command_str == 'move south':
        return ('south', )
    if command_str == 'east' or command_str == 'move east':
        return ('east', )
    if command_str == 'west' or command_str == 'move west':
        return ('west', )

    if command_str.startswith('take'):
        return ('take', command_str[5:])
    if command_str.startswith('pick up'):
        return ('take', command_str[8:])

    if command_str.startswith('use'):
        command_str = command_str[4:]
        if ' on ' in command_str:
            objects = command_str.split(' on ')
            return ('use', objects[0], objects[1], )
        if ' with ' in command_str:
            objects = command_str.split(' with ')
            return ('use', objects[0], objects[1], )
        return ('use', command_str, 'self')

@command('do', doc="perform a game action")
def game_action(client, event, channel, nick, rest):
    if not rest:
        yield "do what, %s?" % (nick)
    else:
        action = parse_action(rest.strip().lower())
        print action
        if action[0] == 'north':
            yield game.move(nick, game.NORTH)
        elif action[0] == 'south':
            yield game.move(nick, game.SOUTH)
        elif action[0] == 'east':
            yield game.move(nick, game.EAST)
        elif action[0] == 'west':
            yield game.move(nick, game.WEST)
        elif action[0] == 'take':
            yield "%s%s" % (nick, game.take(nick, action[1]), )
        elif action[0] == 'use':
            yield game.use(nick, action[1], action[2])

@command('status', doc="check the status of yourself, or another")
def player_status(client, event, channel, nick, rest):
    if not rest:
        return "%s is %s" % (nick, sql.get_status(nick))
    else:
        return "%s is %s" % (rest, sql.get_status(rest))

@command("current", doc="display your current game state")
def display(client, event, channel, nick, rest):
    return game.describe_current(nick)

@command("inventory", doc="display your current game inventory")
def display_inventory(client, event, channel, nick, rest):
    current_inventory = nick + ": you are currently holding "
    inv_items = sql.get_inventory(nick)
    if inv_items:
        current_inventory += ', '.join(game.ITEMS[int(item['item'])]['name'] for item in inv_items)
    else:
        current_inventory += 'nothing.'

    return current_inventory

@command("describe", doc="display more information about an item")
def describe_item(client, event, channel, nick, rest):
    item = game.find_item(rest)
    if item is None:
        return "what's a %s, %s" % (rest, nick)
    return "%s: %s" % (nick, game.ITEMS[item]['description'])

@command("resetgame", doc="rebuild a new world for you to escape")
def reset_game(client, event, channel, nick, rest):
    game.build_world_for(nick)
    return game.describe_current(nick)

import random
import sql

WORLD_SIZE = 10

NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4

SECTIONS = (
    ('plains', ),
    ('mountains', ),
    ('lakes', ),
)


ITEMS = (
    {
        'name': "stick", 
        'description': "A mighty stick. It may be used for bludgeoning, poking and if you have a good imagination, sword fighting.", 
        'carryable': True,
        'interactions': [
            {
                'item': 'self',
                'description': 'You bludgeon yourself to death with your stick. Why would you do that to yourself?',
                'function': lambda nick: kill(nick, "bludgeoned self to a pulp"),
            },
        ],
    },
    {
        'name': "fire", 
        'description': "A roiling mass of fire. It can be used for burning. That's kind of it's thing.", 
        'carryable': True,
        'interactions': [
            {
                'item': 'stick', 
                'description': 'You light the stick on fire. It is now a flaming stick.', 
                'function': lambda nick: burn(nick)
            },
            {
                'item': 'self',
                'description': '...really? You light yourself on fire. You are dead.',
                'function': lambda nick: kill(nick, "due to self immolation"),
            },
        ],
    },
    {
        'name': "flaming stick", 
        'description': "Your stick is on fire. Conveniently, it doesn't appear to actually be harming the stick.", 
        'carryable': True,
        'interactions': [
            {
                'item': 'self',
                'description': "That doesn't seem smart... You try to play with the flaming stick, and end up skewering yourself, cooking yourself from the inside out.",
                'function': lambda nick: kill(nick, "impaled themselves on a flaming stick"),
            },
        ],
    },
)

def burn(nick):
    sql.remove_from_inventory(nick, find_item('stick'))
    sql.remove_from_inventory(nick, find_item('fire'))
    sql.add_to_inventory(nick, find_item('flaming stick'))

def kill(nick, manner):
    sql.update_status(nick, "DEAD: " + manner)

def find_item(item_name):
    for i in xrange(len(ITEMS)):
        if ITEMS[i]['name'] == item_name:
            return i

    return None

def build_world_for(nick):
    """ This will reset a player's world. 
    All items will be deleted, all world locations will be regenerated.
    """
    player = sql.get_player(nick)
    if not player:
        sql.create_player(nick)
        player = sql.get_player(nick)

    sql.wipe_world(player['id'])
    sql.wipe_inventory(player['id'])
    
    # create random world
    for x in xrange(WORLD_SIZE):
        for y in xrange(WORLD_SIZE):
            sql.create_world_section(player['id'], random.randrange(len(SECTIONS)), x, y)

    sql.set_location(nick, random.randrange(WORLD_SIZE), random.randrange(WORLD_SIZE))
    sql.update_status(nick, "ALIVE, for now")

    # fill with items
    for x in xrange(WORLD_SIZE):
        for y in xrange(WORLD_SIZE):
            location = sql.get_world_section(player['id'], x, y)
            if location: 
                sql.create_world_item(location['id'], random.randrange(2))
            else:
                print "No location at %d %s" % (x, y)

def describe_current(nick):
    player = sql.get_player(nick)
    location = sql.get_location(nick)

    if not location or not player:
        return "%s doesn't exist in this world. Maybe they disappeared. Maybe they were launched into space. Maybe nobody cares enough to keep track of where they are." % (nick, )

    world_items = sql.get_world_items(location['id'])

    description = "%s is in %s." % (nick, SECTIONS[location['section']][0])

    description += " There are %s in the NORTH, " % ( 
        SECTIONS[sql.get_world_section(player['id'], player['x'], player['y']-1)['section']][0] if player['y'] > 0 else 'oceans'
    )
    description += "%s in the SOUTH, " % ( 
        SECTIONS[sql.get_world_section(player['id'], player['x'], player['y']+1)['section']][0] if player['y'] < WORLD_SIZE else 'oceans'
    )
    description += "%s to the EAST, " % ( 
        SECTIONS[sql.get_world_section(player['id'], player['x']+1, player['y'])['section']][0] if player['x'] < WORLD_SIZE else 'oceans'
    )
    description += "and %s in the WEST." % ( 
        SECTIONS[sql.get_world_section(player['id'], player['x']-1, player['y'])['section']][0] if player['x'] > 0 else 'oceans'
    )

    if world_items:
        description += (" There is " + 
            ', '.join(ITEMS[int(item['item'])]['name'] for item in world_items) +
            ' nearby.')
    # describe directions
    return description

def move(nick, direction):
    player = sql.get_player(nick)
    if not player:
        return None
    
    if direction == NORTH and player['y'] > 0:
        sql.set_location(nick, player['x'], player['y']-1)
    elif direction == SOUTH and player['y'] < WORLD_SIZE - 1:
        sql.set_location(nick, player['x'], player['y']+1)
    elif direction == WEST and player['x'] > 0:
        sql.set_location(nick, player['x']-1, player['y'])
    elif direction == EAST and player['x'] < WORLD_SIZE - 1:
        sql.set_location(nick, player['x']+1, player['y'])

    return describe_current(nick)

def take(nick, item_name):
    player = sql.get_player(nick)
    world_items = sql.get_world_items(sql.get_location(nick)['id'])

    for item in world_items:
        if ITEMS[int(item['item'])]['name'] == item_name:
            if ITEMS[int(item['item'])]['carryable'] == True:
               sql.remove_world_item(int(item['id']))
               sql.add_to_inventory(nick, int(item['item']))
               return ' took %s' % ITEMS[int(item['item'])]['name']
            else:
               return ', okay. Good luck with that.'

    return " can't seem to find what they're looking for."

def use(nick, first_item_name, second_item_name):
    # check to see if nick actually has the items available
    item_index = find_item(first_item_name)
    if item_index is None:
        return "%s, there's no %s to use!" % (nick, first_item_name)

    first_item = ITEMS[item_index]

    for interaction in first_item['interactions']:
        if interaction['item'] == second_item_name:
            if interaction['function']:
                interaction['function'](nick)
            return '%s: %s' % (nick, interaction['description'], )

    return "%s tried to use a %s with %s. Try not to laugh at them, it's not REALLY their fault." % (
        nick, first_item_name, second_item_name,
    )

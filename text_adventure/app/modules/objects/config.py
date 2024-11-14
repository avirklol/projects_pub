settings = {
    "victorian_mansion": "a twisted Victorian mansion",
    "ancient_dungeon": "an ancient dungeon",
    "royal_dungeon": "a royal dungeon",
    "ancient_temple": "an ancient temple",
    "cursed_forest": "a cursed forest",
    "haunted_cave": "a haunted cave",
    "abandoned_castle": "an abandoned castle",
    "dark_tower": "a dark tower",
    "lost_city": "a lost city",
}
alignments = {
    "good": ["chaotic good", "neutral good", "lawful good"],
    "neutral": ["true neutral"],
    "evil": ["chaotic evil", "neutral evil", "lawful evil"],
}

sexes = ["male", "female"]

npc_race = ["human", "dwarf", "elf", "halfling", "gnome", "half-elf", "half-orc", "orc", "troll", "goblin", "dark-elf", "vampire", "werewolf", "centaur", "giant"]

npc_class = ["warrior", "mage", "rogue", "cleric", "ranger", "paladin", "bard", "druid", "sorcerer", "monk", "barbarian", "fighter", "wizard", "thief", "assassin", "necromancer", "illusionist", "enchanter", "conjurer", "summoner", "elementalist"]

npc_roles = ["merchant", "ally", "enemy"]

items = {
    "keys": ["brass key", "silver key", "gold key"],
    "weapons": ["dagger", "sword", "axe"],
    "potions": ["health potion", "mana potion", "strength potion"],
}

item_conditions = {
    "keys": ["rusty", "old", "new"],
    "weapons": ["rusty", "old", "new"],
    "potions": ["half-full", "full", "empty"],
}

challenges = ["LOCKED ROOM"]

directions = ["north", "south", "east", "west"]

locked_room_warning = [
    "The door is locked; you'll have to find some way to open it.",
    "You'll need a key to open this door.",
    "The door is locked; you'll need to find a key.",
    "The door is locked; you'll need to find a key to open it.",
]

direction_warning = [
    "You can't go that way!",
    "You can't move in that direction.",
    "You can't move that way.",
]

item_not_found_warning = [
    "That item is not here.",
    "You can't find that item.",
    "That item is not in this room.",
]

item_not_in_inventory_warning = [
    "You don't have that item.",
    "That item is not in your inventory.",
    "You're not carrying that item.",
]

item_not_usable_warning = [
    "You can't use that item.",
    "That item is not usable.",
    "That item can't be used.",
]

useless_key_warning = [
    "This key doesn't work here.",
    "This key is useless here.",
    "Your key has no use here.",
    "This key won't work here.",
]

search_failure_warning = [
    "You found nothing.",
    "You searched the room but found nothing.",
    "You found nothing of interest.",
]

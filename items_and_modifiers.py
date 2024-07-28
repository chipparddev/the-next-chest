from math import ceil

item_searcher = {
    'weapon' : {
        'melee' : {
            'light' : {
                1 : 'Claws',
                2 : 'Dagger',
            },
            'medium' : {
                1 : 'Longsword',
                2 : 'Battleaxe',
            },
            'heavy' : {
                1 : 'Halberd',
                2 : 'Greatmace',
            },
        },
        'ranged' : {
            'light' : {
                1 : 'Throwing Darts',
                2 : 'Throwing Knives',
            },
            'medium' : {
                1 : 'Throwing Axes',
                2 : 'Javelins',
            },
            'heavy' : {
                1 : 'Longbow',
                2 : 'Crossbow',
            },
        },
    },
    'shield' : {
        'melee' : {
            'light' : 'Light Kite Shield',
            'medium' : 'Medium Kite Shield',
            'heavy' : 'Heavy Kite Shield',
        },
        'ranged' : {
            'light' : 'Light Round Shield',
            'medium' : 'Medium Round Shield',
            'heavy' : 'Heavy Round Shield',
        },
    },
    'armour' : {
        'melee' : {
            'light' : 'Light Plate Armour',
            'medium' : 'Medium Plate Armour',
            'heavy' : 'Heavy Plate Armour',
        },
        'ranged' : {
            'light' : 'Light Leather Armour',
            'medium' : 'Medium Leather Armour',
            'heavy' : 'Heavy Leather Armour',
        },
    },
    'gem' : {
        'melee' : {
            'light' : 'Topaz',
            'medium' : 'Sapphire',
            'heavy' : 'Ruby',
        },
        'ranged' : {
            'light' : 'Amethyst',
            'medium' : 'Citrine',
            'heavy' : 'Emerald',
        },
    },
}

item_stat_finder = {
    'Starter Stick' : {
        'two-handed' : False,
        'base-damage' : lambda tier : 4,
        'base-attack-time' : 1.0,
    },
    'Claws' : {
        'two-handed' : True,
        'base-damage' : lambda tier : tier * 6,
        'base-attack-time' : 1.0,
    },
    'Dagger' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 6,
        'base-attack-time' : 1.2,
    },
    'Longsword' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 7,
        'base-attack-time' : 1.4,
    },
    'Battleaxe' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 8,
        'base-attack-time' : 1.6,
    },
    'Halberd' : {
        'two-handed' : True,
        'base-damage' : lambda tier : tier * 11,
        'base-attack-time' : 1.8,
    },
    'Greatmace' : {
        'two-handed' : True,
        'base-damage' : lambda tier : tier * 12,
        'base-attack-time' : 2.0,
    },
    'Throwing Darts' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 4,
        'base-attack-time' : 0.8,
    },
    'Throwing Knives' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 5,
        'base-attack-time' : 1.0,
    },
    'Throwing Axes' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 6,
        'base-attack-time' : 1.2,
    },
    'Javelins' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 7,
        'base-attack-time' : 1.4,
    },
    'Longbow' : {
        'two-handed' : True,
        'base-damage' : lambda tier : tier * 10,
        'base-attack-time' : 1.6,
    },
    'Crossbow' : {
        'two-handed' : False,
        'base-damage' : lambda tier : tier * 9,
        'base-attack-time' : 1.8,
    },
    'Light Kite Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 5,
            'ranged-light-penalty' : lambda tier : 10,
            'ranged-medium-penalty' : lambda tier : 10,
        },
    },
    'Medium Kite Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 6,
            'melee-light-penalty' : lambda tier : 10,
            'ranged-light-penalty' : lambda tier : 20,
            'ranged-medium-penalty' : lambda tier : 20,
        },
    },
    'Heavy Kite Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 7,
            'melee-light-penalty' : lambda tier : 20,
            'melee-medium-penalty' : lambda tier : 10,
            'ranged-light-penalty' : lambda tier : 40,
            'ranged-medium-penalty' : lambda tier : 40,
            'ranged-heavy-penalty' : lambda tier : 10,
        },
    },
    'Light Round Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 2,
            'ranged-light-percent-damage' : lambda tier : tier * 10,
            'ranged-medium-percent-damage' : lambda tier : tier * 10,
            'ranged-heavy-percent-damage' : lambda tier : tier * 10,
        },
    },
    'Medium Round Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 3,
            'ranged-medium-percent-damage' : lambda tier : tier * 10,
            'ranged-heavy-percent-damage' : lambda tier : tier * 10,
        },
    },
    'Heavy Round Shield' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 4,
            'ranged-heavy-percent-damage' : lambda tier : tier * 10,
        },
    },
    'Light Plate Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 10,
            'ranged-light-penalty' : lambda tier : 20,
            'ranged-medium-penalty' : lambda tier : 20,
        },
    },
    'Medium Plate Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 12,
            'melee-light-penalty' : lambda tier : 20,
            'ranged-light-penalty' : lambda tier : 40,
            'ranged-medium-penalty' : lambda tier : 40,
        },
    },
    'Heavy Plate Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 14,
            'melee-light-penalty' : lambda tier : 40,
            'melee-medium-penalty' : lambda tier : 20,
            'ranged-light-penalty' : lambda tier : 80,
            'ranged-medium-penalty' : lambda tier : 80,
            'ranged-heavy-penalty' : lambda tier : 20,
        },
    },
    'Light Leather Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 4,
            'ranged-light-percent-damage' : lambda tier : tier * 15,
            'ranged-medium-percent-damage' : lambda tier : tier * 15,
            'ranged-heavy-percent-damage' : lambda tier : tier * 15,
        },
    },
    'Medium Leather Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 6,
            'ranged-medium-percent-damage' : lambda tier : tier * 15,
            'ranged-heavy-percent-damage' : lambda tier : tier * 15,
        },
    },
    'Heavy Leather Armour' : {
        'implicit-modifiers' : {
            'flat-hp' : lambda tier : tier * 8,
            'ranged-heavy-percent-damage' : lambda tier : tier * 15,
        },
    },
    'Topaz' : {
        'unique-modifiers' : ('melee-light-percent-damage', 'melee-light-flat-damage', 'melee-light-attack-speed'),
    },
    'Sapphire' : {
        'unique-modifiers' : ('melee-medium-percent-damage', 'melee-medium-flat-damage', 'melee-medium-attack-speed'),
    },
    'Ruby' : {
        'unique-modifiers' : ('melee-heavy-percent-damage', 'melee-heavy-flat-damage', 'melee-heavy-attack-speed'),
    },
    'Amethyst' : {
        'unique-modifiers' : ('ranged-light-percent-damage', 'ranged-light-flat-damage', 'ranged-light-attack-speed'),
    },
    'Citrine' : {
        'unique-modifiers' : ('ranged-medium-percent-damage', 'ranged-medium-flat-damage', 'ranged-medium-attack-speed'),
    },
    'Emerald' : {
        'unique-modifiers' : ('ranged-heavy-percent-damage', 'ranged-heavy-flat-damage', 'ranged-heavy-attack-speed'),
    },
}

explicit_modifier_function_finder = {
    'percent-damage' : lambda variant : (lambda knowledge : knowledge * {'weapon' : 15, 'gem' : 12}[variant]),
    'melee-percent-damage' : lambda variant : (lambda knowledge : knowledge * {'shield-melee' : 10, 'gem' : 16}[variant]),
    'ranged-percent-damage' : lambda variant : (lambda knowledge : knowledge * {'shield-ranged' : 10, 'armour-ranged' : 15, 'gem' : 16}[variant]),
    'melee-light-percent-damage' : lambda knowledge : knowledge * 20,
    'melee-medium-percent-damage' : lambda knowledge : knowledge * 20,
    'melee-heavy-percent-damage' : lambda knowledge : knowledge * 20,
    'ranged-light-percent-damage' : lambda knowledge : knowledge * 20,
    'ranged-medium-percent-damage' : lambda knowledge : knowledge * 20,
    'ranged-heavy-percent-damage' : lambda knowledge : knowledge * 20,
    'flat-damage' : lambda variant : (lambda knowledge : ceil(knowledge * (knowledge + 1) / {'weapon' : 2, 'gem' : (10 / 3)}[variant])),
    'melee-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2.5),
    'ranged-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2.5),
    'melee-light-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'melee-medium-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'melee-heavy-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'ranged-light-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'ranged-medium-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'ranged-heavy-flat-damage' : lambda knowledge : ceil(knowledge * (knowledge + 1) / 2),
    'attack-speed' : lambda variant : (lambda knowledge : knowledge * {'weapon' : 10, 'gem' : 6}[variant]),
    'melee-attack-speed' : lambda variant : (lambda knowledge : knowledge * {'shield-melee' : 5, 'gem' : 8}[variant]),
    'ranged-attack-speed' : lambda variant : (lambda knowledge : knowledge * {'shield-ranged' : 5, 'gem' : 8}[variant]),
    'melee-light-attack-speed' : lambda knowledge : knowledge * 10,
    'melee-medium-attack-speed' : lambda knowledge : knowledge * 10,
    'melee-heavy-attack-speed' : lambda knowledge : knowledge * 10,
    'ranged-light-attack-speed' : lambda knowledge : knowledge * 10,
    'ranged-medium-attack-speed' : lambda knowledge : knowledge * 10,
    'ranged-heavy-attack-speed' : lambda knowledge : knowledge * 10,
    'percent-hp' : lambda variant : (lambda knowledge : knowledge * {'shield' : 5, 'armour' : 10, 'gem' : 5}[variant]),
    'percent-implicit-hp' : lambda knowledge : knowledge * 25,
    'flat-hp' : lambda variant : (lambda knowledge : knowledge ** 2 * {'shield' : 1, 'armour' : 2, 'gem' : 1}[variant]),
}

modifier_output_finder = { 
    'percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage',
    },
    'melee-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with melee weapons',
    },
    'ranged-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with ranged weapons',
    },
    'melee-light-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with light melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with light melee weapons',
    },
    'melee-medium-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with medium melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with medium melee weapons',
    },
    'melee-heavy-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with heavy melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with heavy melee weapons',
    },
    'ranged-light-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with light ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with light ranged weapons',
    },
    'ranged-medium-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with medium ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with medium ranged weapons',
    },
    'ranged-heavy-percent-damage' : {
        'basic' : lambda magnitude : f'{magnitude}% increased damage with heavy ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased damage with heavy ranged weapons',
    },
    'flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage',
    },
    'melee-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with melee weapons',
    },
    'ranged-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with ranged weapons',
    },
    'melee-light-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with light melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with light melee weapons',
    },
    'melee-medium-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with medium melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with medium melee weapons',
    },
    'melee-heavy-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with heavy melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with heavy melee weapons',
    },
    'ranged-light-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with light ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with light ranged weapons',
    },
    'ranged-medium-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with medium ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with medium ranged weapons',
    },
    'ranged-heavy-flat-damage' : {
        'basic' : lambda magnitude : f'{magnitude} additional damage with heavy ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional damage with heavy ranged weapons',
    },
    'attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed',
    },
    'melee-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with melee weapons',
    },
    'ranged-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with ranged weapons',
    },
    'melee-light-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with light melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with light melee weapons',
    },
    'melee-medium-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with medium melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with medium melee weapons',
    },
    'melee-heavy-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with heavy melee weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with heavy melee weapons',
    },
    'ranged-light-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with light ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with light ranged weapons',
    },
    'ranged-medium-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with medium ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with medium ranged weapons',
    },
    'ranged-heavy-attack-speed' : {
        'basic' : lambda magnitude : f'{magnitude}% increased attack speed with heavy ranged weapons',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased attack speed with heavy ranged weapons',
    },
    'percent-hp' : {
        'basic' : lambda magnitude : f'{magnitude}% increased total HP',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased total HP',
    },
    'percent-implicit-hp' : {
        'basic' : lambda magnitude : f'{magnitude}% increased effect of implicit HP modifier',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max})% increased effect of implicit HP modifier',
    },
    'flat-hp' : {
        'basic' : lambda magnitude : f'{magnitude} additional HP',
        'detailed' : lambda magnitude, max : f'{magnitude}(0-{max}) additional HP',
    },
    'melee-light-penalty' : {
        'basic' : lambda magnitude : f'{magnitude}% damage penalty with light melee weapons',
    },
    'melee-medium-penalty' : {
        'basic' : lambda magnitude : f'{magnitude}% damage penalty with medium melee weapons',
    },
    'ranged-light-penalty' : {
        'basic' : lambda magnitude : f'{magnitude}% damage penalty with light ranged weapons',
    },
    'ranged-medium-penalty' : {
        'basic' : lambda magnitude : f'{magnitude}% damage penalty with medium ranged weapons',
    },
    'ranged-heavy-penalty' : {
        'basic' : lambda magnitude : f'{magnitude}% damage penalty with heavy ranged weapons',
    },
}
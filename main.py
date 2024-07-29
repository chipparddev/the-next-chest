import curses
import os
import random
from math import floor, ceil
from collections import deque
from time import perf_counter
from items_and_modifiers import *
from window_writers import *
from personal_best import *

# Classes

class Item_Manager:
    def __init__(self):
        self.equipment = {'weapon' : None, 'shield' : None, 'armour' : None, 'gem' : None}
        self.inventory = []
        self.knowledge = 1
        self.knowledge_progress = 0
        self.total_stat_magnitudes = {}

    def add_item(self, item):
        self.inventory.append(item)
        return f"Obtained {item.get_output('compact')}"

    def remove_equipment(self, slot, variant):
        item = self.equipment[slot]
        if item is None:
            return False, ''
        
        self.equipment[slot] = None
        self.update_stats(item.get_total_stat_magnitudes(), True)

        if variant == 'unequip':
            self.inventory.append(item)
            return True, f"Unequipped {item.get_output('compact')}"
        
        if variant == 'scrap':
            self.knowledge_progress += item.get_tier()
            self.check_for_knowledge_level()
            return True, f"Scrapped {item.get_output('compact')}"
        
        if variant == 'delete':
            return True, f"Deleted {item.get_output('compact')}"

    def equip_or_unequip_item(self, page, page_position):
        if page == 2 and len(self.inventory) == 0:
            return False, page, page_position, ''

        if page == 1:
            success, message = self.remove_equipment(get_equipment_slot(page_position), 'unequip')
            return success, page, page_position, message

        else:
            item = self.inventory.pop(get_inventory_position(page, page_position))
            slot = item.get_slot()
            self.remove_equipment(slot, 'unequip')

            if slot == 'weapon':
                if item.is_two_handed():
                    self.remove_equipment('shield', 'unequip')

            if slot == 'shield':
                if self.equipment['weapon'] and self.equipment['weapon'].is_two_handed():
                    self.remove_equipment('weapon', 'unequip')

            self.equipment[slot] = item
            self.update_stats(item.get_total_stat_magnitudes())
            page, page_position = self.check_cursor_validity(page, page_position)
            return True, page, page_position, f"Equipped {item.get_output('compact')}"

    def identify_item(self, page, page_position):
        if page == 2 and len(self.inventory) == 0:
            return False, ''
        
        item = self.equipment[get_equipment_slot(page_position)] if page == 1 else self.inventory[get_inventory_position(page, page_position)]
        if item is None:
            return False, ''
        
        success, stat_changes, message = item.identify(self.knowledge)

        if page == 1:
            self.update_stats(stat_changes)

        if success:
            self.knowledge_progress += item.get_tier()
            self.check_for_knowledge_level()

        return success, message
    
    def reroll_item(self, page, page_position):
        if page == 2 and len(self.inventory) == 0:
            return False, ''

        item = self.equipment[get_equipment_slot(page_position)] if page == 1 else self.inventory[get_inventory_position(page, page_position)]
        if item is None:
            return False, ''
        
        success, stat_changes, message = item.reroll(self.knowledge)

        if page == 1:
            self.update_stats(stat_changes)

        return success, message

    def recycle_item(self, page, page_position, other_page = None, other_page_position = None):
        if page == other_page and page_position == other_page_position:
            return False, page, page_position, 'Item is already selected'

        if page == 2 and len(self.inventory) == 0:
            return False, page, page_position, ''
        
        item = self.equipment[get_equipment_slot(page_position)] if page == 1 else self.inventory[get_inventory_position(page, page_position)]
        if item is None:
            return False, page, page_position, ''
        
        tier = item.get_tier()
        if tier == 0:
            return False, page, page_position, 'Item can not be modified'
        
        if tier + 1 > self.knowledge:
            return False, page, page_position, f'Level {tier + 1} knowledge is required to recycle this'
        
        if other_page is None and other_page_position is None:
            return True, page, page_position, 'Select item 2 (Enter: Select, Backspace: Go back)'

        other_item = self.equipment[get_equipment_slot(other_page_position)] if other_page == 1 else self.inventory[get_inventory_position(other_page, other_page_position)]

        if tier != other_item.get_tier():
            return False, page, page_position, f'Item tiers do not match'
        
        else:
            sorted_inventory_positions = []

            if page == 1:
                self.remove_equipment(get_equipment_slot(page_position), 'delete')
            else:
                sorted_inventory_positions.append(get_inventory_position(page, page_position))

            if other_page == 1:
                self.remove_equipment(get_equipment_slot(other_page_position), 'delete')
            else:
                sorted_inventory_positions.append(get_inventory_position(other_page, other_page_position))

            sorted_inventory_positions.sort()

            while len(sorted_inventory_positions) > 0:
                self.inventory.pop(sorted_inventory_positions.pop())

            new_item = generate_recycle_item(tier + 1, other_item, item)
            self.inventory.append(new_item)
            page, page_position = (len(self.inventory) + 19) // 10, (len(self.inventory) - 1) % 10
            return True, page, page_position, f"Created {new_item.get_output('compact')}"

    def scrap_item(self, page, page_position):
        if page == 2 and len(self.inventory) == 0:
            return False, page, page_position, ''

        if page == 1:
            success, message = self.remove_equipment(get_equipment_slot(page_position), 'scrap')
            return success, page, page_position, message
        
        else:
            item = self.inventory.pop(get_inventory_position(page, page_position))
            self.knowledge_progress += item.get_tier()
            self.check_for_knowledge_level()
            page, page_position = self.check_cursor_validity(page, page_position)
            return True, page, page_position, f"Scrapped {item.get_output('compact')}"
        
    def delete_item(self, page, page_position):
        if page == 2 and len(self.inventory) == 0:
            return False, page, page_position, ''
        
        if page == 1:
            success, message = self.remove_equipment(get_equipment_slot(page_position), 'delete')
            return success, page, page_position, message
        
        else:
            item = self.inventory.pop(get_inventory_position(page, page_position))
            page, page_position = self.check_cursor_validity(page, page_position)
            return True, page, page_position, f"Deleted {item.get_output('compact')}"
        
    def sort_inventory(self):
        self.inventory.sort(key = lambda item : item.get_sorting_priority())

    def update_stats(self, stat_changes, reverse = False):
        for stat_name, magnitude in stat_changes.items():
            if reverse:
                update_stat_tracker(self.total_stat_magnitudes, stat_name, -magnitude)
            else:
                update_stat_tracker(self.total_stat_magnitudes, stat_name, magnitude)

    def check_cursor_validity(self, page, page_position):
        max_page_position = 0 if len(self.inventory) == 0 else len(self.inventory) - get_inventory_position(page, 0) - 1

        if page_position > max_page_position:
            page_position -= 1
            if page_position < 0:
                page -= 1
                page_position = 9

        return page, page_position

    def check_for_knowledge_level(self):
        while self.knowledge_progress >= self.knowledge * 15:
            self.knowledge_progress -= self.knowledge * 15
            self.knowledge += 1

    def get_knowledge(self):
        return self.knowledge
    
    def get_knowledge_progress(self):
        return self.knowledge_progress
    
    def get_equipment_tier_total(self):
        total = 0
        for slot, item in self.equipment.items():
            if slot == 'weapon' and item and item.is_two_handed():
                total += get_item_tier(item) * 2
            else:
                total += get_item_tier(item)

        return total

    def get_damage(self):
        weapon = self.equipment['weapon']
        if weapon is None:
            return 0
        
        base_damage = weapon.get_base_damage()
        style, weight = weapon.get_damage_type()

        primary_stat = 'percent-damage'
        secondary_stat = f'{style}-{primary_stat}'
        tertiary_stat = f'{style}-{weight}-{primary_stat}'
        total_percent_damage = get_stat_magnitude(self.total_stat_magnitudes, primary_stat) + get_stat_magnitude(self.total_stat_magnitudes, secondary_stat) + get_stat_magnitude(self.total_stat_magnitudes, tertiary_stat)

        primary_stat = 'flat-damage'
        secondary_stat = f'{style}-{primary_stat}'
        tertiary_stat = f'{style}-{weight}-{primary_stat}'
        total_flat_damage = get_stat_magnitude(self.total_stat_magnitudes, primary_stat) + get_stat_magnitude(self.total_stat_magnitudes, secondary_stat) + get_stat_magnitude(self.total_stat_magnitudes, tertiary_stat)

        penalty_stat = f'{style}-{weight}-penalty'
        total_penalty = min(100, get_stat_magnitude(self.total_stat_magnitudes, penalty_stat))

        return floor((base_damage + total_flat_damage) * (1 + total_percent_damage / 100) * (1 - total_penalty / 100))

    def get_attack_time(self):
        weapon = self.equipment['weapon']
        if weapon is None:
            return 999
        
        base_attack_time = weapon.get_base_attack_time()
        style, weight = weapon.get_damage_type()

        primary_stat = 'attack-speed'
        secondary_stat = f'{style}-{primary_stat}'
        tertiary_stat = f'{style}-{weight}-{primary_stat}'
        total_attack_speed = get_stat_magnitude(self.total_stat_magnitudes, primary_stat) + get_stat_magnitude(self.total_stat_magnitudes, secondary_stat) + get_stat_magnitude(self.total_stat_magnitudes, tertiary_stat)

        return ceil(base_attack_time / (1 + total_attack_speed / 100) * 20) / 20

    def get_max_hp(self):
        base_hp = 25

        armour = self.equipment['armour']
        armour_implicit_hp = 0 if armour is None else armour.get_implicit_hp()

        total_percent_hp = get_stat_magnitude(self.total_stat_magnitudes, 'percent-hp')
        total_percent_armour_implicit_hp = get_stat_magnitude(self.total_stat_magnitudes, 'percent-implicit-hp')
        total_flat_hp = get_stat_magnitude(self.total_stat_magnitudes, 'flat-hp')

        return floor((base_hp + total_flat_hp + armour_implicit_hp * (total_percent_armour_implicit_hp / 100)) * (1 + total_percent_hp / 100))

    def get_player_stats_output(self, remaining_attack_time = None, remaining_hp = None):
        damage = self.get_damage()
        attack_time = self.get_attack_time()
        max_hp = self.get_max_hp()

        attack_time = 'N/A' if attack_time == 999 else f'{attack_time}s'
        remaining_attack_time = '' if remaining_attack_time is None else f'(Next attack: {remaining_attack_time:.2f}s)'
        remaining_hp = '' if remaining_hp is None else f'{remaining_hp}/'

        output_pad = curses.newpad(4, 50)
        output_pad.addstr(0, 0, 'You')
        output_pad.addstr(1, 0, f'HP: {remaining_hp}{max_hp}')
        output_pad.addstr(2, 0, f'Damage: {damage}')
        output_pad.addstr(3, 0, f'Attack time: {attack_time} {remaining_attack_time}')
        return output_pad

    def get_item_list_output(self, page, page_position, direction = None):
        max_page = max(2, (len(self.inventory) + 19) // 10)

        if direction == 'left' and page > 1:
            page -= 1
            page_position = 0

        if direction == 'right' and page < max_page:
            page += 1
            page_position = 0

        output_pad = curses.newpad(12, 65)

        if page == 1:
            output_pad.addstr(0, 0, 'Weapon:')
            output_pad.addstr(1, 0, get_item_output(self.equipment['weapon'], 'compact'))
            output_pad.addstr(3, 0, 'Shield:')
            output_pad.addstr(4, 0, get_item_output(self.equipment['shield'], 'compact'))
            output_pad.addstr(6, 0, 'Armour:')
            output_pad.addstr(7, 0, get_item_output(self.equipment['armour'], 'compact'))
            output_pad.addstr(9, 0, 'Gem:')
            output_pad.addstr(10, 0, get_item_output(self.equipment['gem'], 'compact'))

        else:
            output_pad.addstr(0, 0, 'Inventory:')
            output_pad.addstr(1, 0, 'None')

            for row, position in enumerate(range(get_inventory_position(page, 0), min(len(self.inventory), get_inventory_position(page + 1, 0))), 1):
                output_pad.addstr(row, 0, get_item_output(self.inventory[position], 'compact'))

        left_arrow = '  ' if page == 1 else '<-'
        right_arrow = '  ' if page == max_page else '->'

        output_pad.addstr(11, 24, f'{left_arrow} Page {page}/{max_page} {right_arrow}')
        return output_pad, page, page_position

    def get_item_details_output(self, page, page_position, variant, direction = None):
        max_page_position = min(9, len(self.inventory) - get_inventory_position(page, 0) - 1)
        page_position_shift = 3 if page == 1 else 1

        if direction == 'up' and page_position > 0:
            page_position -= page_position_shift

        if direction == 'down' and page_position < max_page_position:
            page_position += page_position_shift
            
        if page == 1:
            item = self.equipment[get_equipment_slot(page_position)]
        else:
            item = None if len(self.inventory) == 0 else self.inventory[get_inventory_position(page, page_position)]

        return get_item_output(item, variant), page_position

class Item():
    def __init__(self, name, tier, slot, style, weight, variant, total_stat_magnitudes, explicit_modifier_pool, modifiable):
        self.name = name
        self.tier = tier
        self.slot = slot
        self.style = style
        self.weight = weight
        self.variant = variant
        self.total_stat_magnitudes = total_stat_magnitudes
        self.explicit_modifier_pool = explicit_modifier_pool
        self.modifiable = modifiable
        self.explicit_modifiers = []
        self.identified = False

    def identify(self, knowledge):
        stat_changes = {}

        if not self.modifiable:
            return False, stat_changes, 'Item can not be modified'

        elif self.identified:
            return False, stat_changes, 'Item is already identified'

        else:
            self.identified = True

            if self.slot == 'gem':
                knowledge = min(knowledge, self.tier)

            while len(self.explicit_modifiers) < 5:
                modifier_name, modifier_function = random.choice(tuple(self.explicit_modifier_pool.items()))
                max = modifier_function(knowledge)
                magnitude = random.randint(0, max)

                self.explicit_modifiers.append({'name' : modifier_name, 'max' : max, 'magnitude' : magnitude})
                update_stat_tracker(stat_changes, modifier_name, magnitude)
                update_stat_tracker(self.total_stat_magnitudes, modifier_name, magnitude)

            return True, stat_changes, f'Identified {self.__str__()}'

    def reroll(self, knowledge):
        stat_changes = {}

        if not self.modifiable:
            return False, stat_changes, 'Item can not be modified'
        
        elif not self.identified:
            return False, stat_changes, 'Item needs to be identified first'

        else:
            if self.slot == 'gem':
                knowledge = min(knowledge, self.tier)

            for modifier_slot, old_modifier in enumerate(self.explicit_modifiers):
                old_modifier_name = old_modifier['name']
                old_magnitude = old_modifier['magnitude']

                new_modifier_name, new_modifier_function = random.choice(tuple(self.explicit_modifier_pool.items()))
                new_max = new_modifier_function(knowledge)
                new_magnitude = random.randint(0, new_max)

                self.explicit_modifiers[modifier_slot] = {'name' : new_modifier_name, 'max' : new_max, 'magnitude' : new_magnitude}
                update_stat_tracker(stat_changes, old_modifier_name, -old_magnitude)
                update_stat_tracker(stat_changes, new_modifier_name, new_magnitude)
                update_stat_tracker(self.total_stat_magnitudes, old_modifier_name, -old_magnitude)
                update_stat_tracker(self.total_stat_magnitudes, new_modifier_name, new_magnitude)
                                    
            return True, stat_changes, f'Rerolled {self.__str__()}'
        
    def get_tier(self):
        return self.tier

    def get_slot(self):
        return self.slot

    def get_total_stat_magnitudes(self):
        return self.total_stat_magnitudes
    
    def get_search_path(self):
        return self.style, self.weight, self.variant
    
    def get_sorting_priority(self):
        slot_priority = {'weapon' : 0, 'shield' : 1, 'armour' : 2, 'gem' : 3}[self.slot]
        style_priority = {'melee' : 0, 'ranged' : 1}[self.style]
        weight_priority = {'light' : 0, 'medium' : 1, 'heavy' : 2}[self.weight]
        variant_priority = self.variant if self.variant else 0
        return (- self.tier, slot_priority, style_priority, weight_priority, variant_priority)
        
    def __str__(self):
        if self.modifiable:
            return f'{self.name} (T{self.tier})'
        else:
            return f'{self.name} (UT)'

class Weapon(Item):
    def __init__(self, name, tier, style, weight, variant, stats, modifiable = True):
        self.two_handed = stats['two-handed']
        self.base_damage = stats['base-damage'](tier)
        self.base_attack_time = stats['base-attack-time']

        explicit_modifier_pool = {
            'percent-damage' : explicit_modifier_function_finder['percent-damage']('weapon'),
            'flat-damage' : explicit_modifier_function_finder['flat-damage']('weapon'),
            'attack-speed' : explicit_modifier_function_finder['attack-speed']('weapon'),
        }

        super().__init__(name, tier, 'weapon', style, weight, variant, {}, explicit_modifier_pool, modifiable)

    def is_two_handed(self):
        return self.two_handed

    def get_base_damage(self):
        return self.base_damage

    def get_base_attack_time(self):
        return self.base_attack_time
    
    def get_damage_type(self):
        return self.style, self.weight

    def get_output(self, variant):
        if variant == 'compact':
            return self.__str__()
        
        hands = 'Two handed' if self.two_handed else 'One handed'

        output_pad = curses.newpad(13, 65)
        output_pad.addstr(0, 0, self.__str__())
        output_pad.addstr(1, 0, f'{hands} {self.weight} {self.style} weapon')
        output_pad.addstr(2, 0, f'Base damage: {self.base_damage}')
        output_pad.addstr(3, 0, f'Base attack time: {self.base_attack_time}')

        explicit_modifier_row = 5

        if not self.identified:
            output_pad.addstr(explicit_modifier_row, 0, 'Unidentified')

        if not self.modifiable:
            output_pad.addstr(explicit_modifier_row, 0, 'Unmodifiable')

        for modifier in self.explicit_modifiers:
            modifier_name = modifier['name']
            magnitude = modifier['magnitude']
            max = modifier['max']

            if variant == 'basic':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude))

            if variant == 'detailed':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude, max))

            explicit_modifier_row += 1

        return output_pad

class Shield(Item):
    def __init__(self, name, tier, style, weight, stats):
        self.implicit_modifiers = {}
        for modifier_name, modifier_function in stats['implicit-modifiers'].items():
            self.implicit_modifiers[modifier_name] = modifier_function(tier)

        explicit_modifier_pool = {
            'percent-hp' : explicit_modifier_function_finder['percent-hp']('shield'),
            'flat-hp' : explicit_modifier_function_finder['flat-hp']('shield'),
        }

        if style == 'melee':
            explicit_modifier_pool['melee-percent-damage'] = explicit_modifier_function_finder['melee-percent-damage']('shield-melee')
            explicit_modifier_pool['melee-attack-speed'] = explicit_modifier_function_finder['melee-attack-speed']('shield-melee')

        if style == 'ranged':
            explicit_modifier_pool['ranged-percent-damage'] = explicit_modifier_function_finder['ranged-percent-damage']('shield-ranged')
            explicit_modifier_pool['ranged-attack-speed'] = explicit_modifier_function_finder['ranged-attack-speed']('shield-ranged')

        super().__init__(name, tier, 'shield', style, weight, None, self.implicit_modifiers.copy(), explicit_modifier_pool, True)

    def get_output(self, variant):
        if variant == 'compact':
            return self.__str__()
        
        output_pad = curses.newpad(13, 65)
        output_pad.addstr(0, 0, self.__str__())

        implicit_modifier_row = 1

        for modifier_name, magnitude in self.implicit_modifiers.items():
            output_pad.addstr(implicit_modifier_row, 0, modifier_output_finder[modifier_name]['basic'](magnitude))
            implicit_modifier_row += 1

        explicit_modifier_row = implicit_modifier_row + 1

        if not self.identified:
            output_pad.addstr(explicit_modifier_row, 0, 'Unidentified')

        if not self.modifiable:
            output_pad.addstr(explicit_modifier_row, 0, 'Unmodifiable')

        for modifier in self.explicit_modifiers:
            modifier_name = modifier['name']
            magnitude = modifier['magnitude']
            max = modifier['max']

            if variant == 'basic':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude))

            if variant == 'detailed':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude, max))

            explicit_modifier_row += 1

        return output_pad

class Armour(Item):
    def __init__(self, name, tier, style, weight, stats):
        self.implicit_modifiers = {}
        for modifier_name, modifier_function in stats['implicit-modifiers'].items():
            self.implicit_modifiers[modifier_name] = modifier_function(tier)

        explicit_modifier_pool = {
            'percent-hp' : explicit_modifier_function_finder['percent-hp']('armour'),
            'percent-implicit-hp' : explicit_modifier_function_finder['percent-implicit-hp'],
            'flat-hp' : explicit_modifier_function_finder['flat-hp']('armour'),
        }

        if style == 'ranged':
            explicit_modifier_pool['ranged-percent-damage'] = explicit_modifier_function_finder['ranged-percent-damage']('armour-ranged')

        super().__init__(name, tier, 'armour', style, weight, None, self.implicit_modifiers.copy(), explicit_modifier_pool, True)

    def get_implicit_hp(self):
        return self.implicit_modifiers['flat-hp']

    def get_output(self, variant):
        if variant == 'compact':
            return self.__str__()
        
        output_pad = curses.newpad(13, 65)
        output_pad.addstr(0, 0, self.__str__())

        implicit_modifier_row = 1

        for modifier_name, magnitude in self.implicit_modifiers.items():
            output_pad.addstr(implicit_modifier_row, 0, modifier_output_finder[modifier_name]['basic'](magnitude))
            implicit_modifier_row += 1

        explicit_modifier_row = implicit_modifier_row + 1

        if not self.identified:
            output_pad.addstr(explicit_modifier_row, 0, 'Unidentified')

        if not self.modifiable:
            output_pad.addstr(explicit_modifier_row, 0, 'Unmodifiable')

        for modifier in self.explicit_modifiers:
            modifier_name = modifier['name']
            magnitude = modifier['magnitude']
            max = modifier['max']

            if variant == 'basic':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude))

            if variant == 'detailed':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude, max))

            explicit_modifier_row += 1

        return output_pad

class Gem(Item):
    def __init__(self, name, tier, style, weight, stats):
        explicit_modifier_pool = {
            'percent-damage' : explicit_modifier_function_finder['percent-damage']('gem'),
            'melee-percent-damage' : explicit_modifier_function_finder['melee-percent-damage']('gem'),
            'ranged-percent-damage' : explicit_modifier_function_finder['ranged-percent-damage']('gem'),
            'flat-damage' : explicit_modifier_function_finder['flat-damage']('gem'),
            'melee-flat-damage' : explicit_modifier_function_finder['melee-flat-damage'],
            'ranged-flat-damage' : explicit_modifier_function_finder['ranged-flat-damage'],
            'attack-speed' : explicit_modifier_function_finder['attack-speed']('gem'),
            'melee-attack-speed' : explicit_modifier_function_finder['melee-attack-speed']('gem'),
            'ranged-attack-speed' : explicit_modifier_function_finder['ranged-attack-speed']('gem'),
            'percent-hp' : explicit_modifier_function_finder['percent-hp']('gem'),
            'flat-hp' : explicit_modifier_function_finder['flat-hp']('gem'),
        }

        unique_modifiers = stats['unique-modifiers']
        for modifier in unique_modifiers:
            explicit_modifier_pool[modifier] = explicit_modifier_function_finder[modifier]

        super().__init__(name, tier, 'gem', style, weight, None, {}, explicit_modifier_pool, True)

    def get_output(self, variant):
        if variant == 'compact':
            return self.__str__()
        
        output_pad = curses.newpad(13, 65)
        output_pad.addstr(0, 0, self.__str__())
        output_pad.addstr(1, 0, f'Can roll powerful {self.weight} {self.style} mods')
        output_pad.addstr(2, 0, f"Knowledge past level {self.tier} will not further improve this item's mods")
        
        explicit_modifier_row = 4

        if not self.identified:
            output_pad.addstr(explicit_modifier_row, 0, 'Unidentified')

        if not self.modifiable:
            output_pad.addstr(explicit_modifier_row, 0, 'Unmodifiable')

        for modifier in self.explicit_modifiers:
            modifier_name = modifier['name']
            magnitude = modifier['magnitude']
            max = modifier['max']

            if variant == 'basic':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude))

            if variant == 'detailed':
                output_pad.addstr(explicit_modifier_row, 0, modifier_output_finder[modifier_name][variant](magnitude, max))

            explicit_modifier_row += 1

        return output_pad

# Functions

def generate_item(item_name, tier, item_slot, attribute_list, item_stats):
    if item_slot == 'weapon':
        return Weapon(item_name, tier, attribute_list[0], attribute_list[1], attribute_list[2], item_stats)

    if item_slot == 'shield':
        return Shield(item_name, tier, attribute_list[0], attribute_list[1], item_stats)
    
    if item_slot == 'armour':
        return Armour(item_name, tier, attribute_list[0], attribute_list[1], item_stats)
    
    if item_slot == 'gem':
        return Gem(item_name, tier, attribute_list[0], attribute_list[1], item_stats)

def generate_starter_item():
    item_name = 'Starter Stick'
    item_stats = item_stat_finder[item_name]
    return Weapon(item_name, 0, 'melee', 'light', None, item_stats, False)

def generate_chest_item(tier):
    item_slot = random.choices(('weapon', 'shield', 'armour', 'gem'), (9, 3, 6, 1))[0]
    search_scope = item_searcher[item_slot]
    search_path = []

    while type(search_scope) is dict:
        item_attribute, search_scope = random.choice(tuple(search_scope.items()))
        search_path.append(item_attribute)

    item_name = search_scope
    item_stats = item_stat_finder[item_name]
    return generate_item(item_name, tier, item_slot, search_path, item_stats)
    
def generate_recycle_item(tier, first_item, second_item):
    first_slot, first_search_path = first_item.get_slot(), first_item.get_search_path()
    second_slot, second_search_path = second_item.get_slot(), second_item.get_search_path()

    if random.randint(0, 1) == 0:
        item_slot = first_slot
        primary_search_path = first_search_path
        secondary_search_path = second_search_path
    else:
        item_slot = second_slot
        primary_search_path = second_search_path
        secondary_search_path = first_search_path

    search_scope = item_searcher[item_slot]
    search_path = []

    for primary_item_attribute, secondary_item_attribute in zip(primary_search_path, secondary_search_path):
        if primary_item_attribute:
            if secondary_item_attribute:
                search_path.append(random.choice((primary_item_attribute, secondary_item_attribute)))
            else:
                search_path.append(primary_item_attribute)

    for item_attribute in search_path:
        search_scope = search_scope[item_attribute]

    item_name = search_scope
    item_stats = item_stat_finder[item_name]
    return generate_item(item_name, tier, item_slot, search_path, item_stats)

def update_stat_tracker(stat_tracker, stat_name, magnitude):
    if stat_name in stat_tracker:
        stat_tracker[stat_name] += magnitude
    else:
        stat_tracker[stat_name] = magnitude

def get_stat_magnitude(stat_tracker, stat_name):
    if stat_name in stat_tracker:
        return stat_tracker[stat_name]
    else:
        return 0
    
def get_equipment_slot(page_position):
    return {0 : 'weapon', 3 : 'shield', 6 : 'armour', 9 : 'gem'}[page_position]
    
def get_inventory_position(page, page_position):
    return (page - 2) * 10 + page_position

def get_item_tier(item):
    if item is None:
        return 0
    else:
        return item.get_tier()

def get_item_output(item, variant):
    if item is None and variant == 'compact':
        return 'None'
    
    if item is None and variant in ('basic', 'detailed'):
        output_pad = curses.newpad(13, 65)
        output_pad.addstr(0, 0, 'There is nothing here.')
        return output_pad
    
    return item.get_output(variant)

def get_wave_stats(wave):
    hp_drain_magnitude = 2 ** max(0, wave - 10)
    hp_drain_time = round(1 - 0.1 * min(9, wave - 1), 1)
    starting_chest_hp = round(100 * hp_drain_magnitude / hp_drain_time)
    return hp_drain_magnitude, hp_drain_time, starting_chest_hp

def get_chest_hp(tier):
    multiplier = tier ** (2 + 0.125 * min(6, tier - 2) + 0.025 * max(0, tier - 8))
    return round(multiplier * 100)

def get_endpoints(pad, top, left):
    height, width = pad.getmaxyx()
    return top + height, left + width
    
# Main Program

def main_menu(stdscr, game_top, game_left):
    stdscr.clear()

    main_menu_window = curses.newwin(6, 116, game_top, game_left)
    pb_waves_cleared, pb_additional_damage = get_personal_best()
    write_main_menu(main_menu_window, pb_waves_cleared, pb_additional_damage)

    while True:
        input = stdscr.getch()
        if input == 10: 
            return True
        if input == 27:
            return False
        
        main_menu_window.refresh()

def game(stdscr, game_top, game_left):
    stdscr.clear()

    item_manager = Item_Manager()
    item_manager.add_item(generate_starter_item())

    mode = 'crafting'
    wave = 1
    chest_tier = 1
    remaining_actions = 0
    hp_drain_magnitude, hp_drain_time, chest_max_hp = get_wave_stats(wave)
    page, cursor_row = 1, 0
    cursor_character = '>'
    fast_forward, combat_update_period = 'off', 0.05
    modifier_ranges, item_details_variant = 'off', 'basic'

    player_stats_top, player_stats_left = game_top + 6, game_left
    item_list_top, item_list_left = game_top, game_left + 52
    item_details_top, item_details_left = game_top + 13, game_left + 52
    cursor_window = curses.newwin(10, 2, game_top + 1, game_left + 50)
    wave_info_window = curses.newwin(2, 50, game_top, game_left)
    actions_and_knowledge_window = curses.newwin(2, 50, game_top + 3, game_left)
    chest_info_window = curses.newwin(2, 50, game_top + 11, game_left)
    messages_window = curses.newwin(12, 50, game_top + 14, game_left)
    controls_window = curses.newwin(2, 118, game_top + 28, game_left)

    player_stats_pad = item_manager.get_player_stats_output()
    player_stats_bottom, player_stats_right = get_endpoints(player_stats_pad, player_stats_top, player_stats_left)

    item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
    item_list_bottom, item_list_right = get_endpoints(item_list_pad, item_list_top, item_list_left)

    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, 'detailed')
    item_details_bottom, item_details_right = get_endpoints(item_details_pad, item_details_top, item_details_left)

    write_cursor(cursor_window, cursor_character, cursor_row)
    write_wave_info(wave_info_window, wave, hp_drain_magnitude, hp_drain_time, False)
    write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())
    write_chest_info(chest_info_window, chest_tier, chest_max_hp)
    write_controls(controls_window, fast_forward, modifier_ranges)

    messages = deque(maxlen = 12)
    message_duration = 10

    key_timestamps = {}
    key_cooldown_duration = 0.1

    recent_movement = False

    while True:
        input = stdscr.getch()

        if input in (ord('w'), ord('s'), ord('a'), ord('d'), ord('e'), ord('z'), ord('x'), ord('c'), ord('v'), ord('b'), ord('1'), ord('2'), ord(' '), 8, 10, 27):
            if perf_counter() - key_cooldown_duration > get_stat_magnitude(key_timestamps, input):
                key_timestamps[input] = perf_counter()

                if input in (ord('w'), ord('s'), ord('a'), ord('d')):
                    recent_movement = True

                if input == ord('w'): # Move up
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant, 'up')
                    write_cursor(cursor_window, cursor_character, cursor_row)

                elif input == ord('s'): # Move down
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant, 'down')
                    write_cursor(cursor_window, cursor_character, cursor_row)

                elif input == ord('a'): # Move left
                    item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row, 'left')
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                    write_cursor(cursor_window, cursor_character, cursor_row)

                elif input == ord('d'): # Move right
                    item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row, 'right')
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                    write_cursor(cursor_window, cursor_character, cursor_row)

                elif input == ord('1'): # Toggle fast forward
                    fast_forward = 'on' if fast_forward == 'off' else 'off'
                    combat_update_period = 0.05 if fast_forward == 'off' else 0.01
                    write_controls(controls_window, fast_forward, modifier_ranges)

                elif input == ord('2'): # Toggle modifier ranges
                    modifier_ranges = 'on' if modifier_ranges == 'off' else 'off'
                    item_details_variant = 'basic' if modifier_ranges == 'off' else 'detailed'
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                    write_controls(controls_window, fast_forward, modifier_ranges)

                elif input == 8: # Go back (Backspace)
                    if mode == 'exit-confirmation':
                        mode = original_mode
                        messages.appendleft({'text' : 'Cancelled exit', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                        if mode == 'combat':
                            last_update_time = perf_counter()

                    elif mode == 'combat-confirmation':
                        mode = 'crafting'
                        messages.appendleft({'text' : 'Cancelled combat', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                    elif mode == 'recycle-selection-1':
                        mode = 'crafting'
                        cursor_character = '>'
                        messages.appendleft({'text' : 'Cancelled recycle', 'timestamp' : perf_counter()})
                        write_cursor(cursor_window, cursor_character, cursor_row)
                        write_messages(messages_window, messages)

                    elif mode == 'recycle-selection-2':
                        mode = 'recycle-selection-1'
                        cursor_character = '1'
                        messages.appendleft({'text' : 'Select item 1 (Enter: Select, Backspace: Go back)', 'timestamp' : perf_counter()})
                        write_cursor(cursor_window, cursor_character, cursor_row)
                        write_messages(messages_window, messages)

                elif input == 10: # Go forward (Enter)
                    if mode == 'crafting':
                        mode = 'combat-confirmation'
                        messages.appendleft({'text' : 'Begin combat? (Enter: Yes, Backspace: No)', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                    elif mode == 'exit-confirmation':
                        break

                    elif mode == 'combat-confirmation':
                        mode = 'combat-initialization'

                    elif mode == 'recycle-selection-1':
                        success, page, cursor_row, message = item_manager.recycle_item(page, cursor_row)

                        if success:
                            mode = 'recycle-selection-2'
                            cursor_character = '2'
                            marker_character = '1'
                            marker_page, marker_row = page, cursor_row
                            write_cursor(cursor_window, cursor_character, cursor_row)

                        if message:
                            messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                            write_messages(messages_window, messages)

                    elif mode == 'recycle-selection-2':
                        success, page, cursor_row, message = item_manager.recycle_item(page, cursor_row, marker_page, marker_row)

                        if success:
                            mode = 'crafting'
                            player_stats_pad = item_manager.get_player_stats_output()
                            item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                            item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                            cursor_character = '>'
                            remaining_actions -= 1
                            write_cursor(cursor_window, cursor_character, cursor_row)
                            write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())

                        if message:
                            messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                            write_messages(messages_window, messages)

                elif input == 27: # Exit game (Escape)
                    if mode != 'exit-confirmation':
                        original_mode = mode
                        mode = 'exit-confirmation'
                        messages.appendleft({'text' : 'Exit to main menu? (Enter: Yes, Backspace: No)', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                elif mode == 'crafting':
                    if input == ord('e'): # Equip / Unequip
                        success, page, cursor_row, message = item_manager.equip_or_unequip_item(page, cursor_row)

                        if success:
                            player_stats_pad = item_manager.get_player_stats_output()
                            item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                            item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                            write_cursor(cursor_window, cursor_character, cursor_row)

                        if message:
                            messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                            write_messages(messages_window, messages)   

                    elif input == ord('b'): # Delete
                        success, page, cursor_row, message = item_manager.delete_item(page, cursor_row)

                        if success:
                            player_stats_pad = item_manager.get_player_stats_output()
                            item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                            item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                            write_cursor(cursor_window, cursor_character, cursor_row)

                        if message:
                            messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                            write_messages(messages_window, messages)

                    elif input == ord(' '): # Spacebar
                        item_manager.sort_inventory()
                        item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                        item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                        messages.appendleft({'text' : 'Sorted inventory', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                    elif remaining_actions > 0:
                        if input == ord('z'): # Identify
                            success, message = item_manager.identify_item(page, cursor_row)

                            if success:
                                player_stats_pad = item_manager.get_player_stats_output()
                                item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                                remaining_actions -= 1
                                write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())

                            if message:
                                messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                                write_messages(messages_window, messages)

                        if input == ord('x'): # Reroll
                            success, message = item_manager.reroll_item(page, cursor_row)

                            if success:
                                player_stats_pad = item_manager.get_player_stats_output()
                                item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                                remaining_actions -= 1
                                write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())

                            if message:
                                messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                                write_messages(messages_window, messages)

                        if input == ord('c'): # Recycle
                            mode = 'recycle-selection-1'
                            cursor_character = '1'
                            messages.appendleft({'text' : 'Select item 1 (Enter: Select, Backspace: Go back)', 'timestamp' : perf_counter()})
                            write_cursor(cursor_window, cursor_character, cursor_row)
                            write_messages(messages_window, messages)

                        if input == ord('v'): # Scrap
                            success, page, cursor_row, message = item_manager.scrap_item(page, cursor_row)

                            if success:
                                player_stats_pad = item_manager.get_player_stats_output()
                                item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                                item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                                remaining_actions -= 1
                                write_cursor(cursor_window, cursor_character, cursor_row)
                                write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())

                            if message:
                                messages.appendleft({'text' : message, 'timestamp' : perf_counter()})
                                write_messages(messages_window, messages)

                    else:
                        messages.appendleft({'text' : 'You can not do this while you are out of actions', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                else:
                    messages.appendleft({'text' : 'You can not do that right now', 'timestamp' : perf_counter()})
                    write_messages(messages_window, messages)
        
        if mode == 'recycle-selection-2' and page == marker_page and recent_movement:
            recent_movement = False
            write_cursor_and_marker(cursor_window, cursor_character, cursor_row, marker_character, marker_row)

        if mode == 'combat-initialization':
            mode = 'combat'

            player_max_hp = item_manager.get_max_hp()
            damage = item_manager.get_damage()
            attack_time = item_manager.get_attack_time()

            player_remaining_hp = player_max_hp
            remaining_attack_time = attack_time
            player_stats_pad = item_manager.get_player_stats_output(remaining_attack_time, player_remaining_hp)
            
            chest_remaining_hp = chest_max_hp
            remaining_hp_drain_time = hp_drain_time
            write_wave_info(wave_info_window, wave, hp_drain_magnitude, hp_drain_time, True)
            write_chest_info(chest_info_window, chest_tier, chest_max_hp, chest_remaining_hp)

            death_type = 'dangerous'
            milestones_reached = 0
            milestone_hp = round(chest_max_hp * 0.75)

            last_update_time = perf_counter()

        if mode == 'combat':
            if perf_counter() - combat_update_period > last_update_time:
                last_update_time += combat_update_period

                remaining_attack_time = round(remaining_attack_time - 0.05, 2)
                remaining_hp_drain_time = round(remaining_hp_drain_time - 0.05, 2)

                if remaining_attack_time == 0:
                    remaining_attack_time = attack_time
                    chest_remaining_hp = max(0, chest_remaining_hp - damage)
                    write_chest_info(chest_info_window, chest_tier, chest_max_hp, chest_remaining_hp)

                if remaining_hp_drain_time == 0:
                    remaining_hp_drain_time = hp_drain_time
                    player_remaining_hp = max(0, player_remaining_hp - hp_drain_magnitude)

                player_stats_pad = item_manager.get_player_stats_output(remaining_attack_time, player_remaining_hp)

                while milestones_reached < 3 and chest_remaining_hp <= milestone_hp:
                    milestones_reached += 1
                    milestone_hp = round(chest_max_hp * (0.75 - 0.25 * milestones_reached))

                    messages.appendleft({'text' : item_manager.add_item(generate_chest_item(chest_tier)), 'timestamp' : perf_counter()})
                    item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                    write_messages(messages_window, messages)

                if chest_remaining_hp == 0:
                    for i in range(2):
                        messages.appendleft({'text' : item_manager.add_item(generate_chest_item(chest_tier)), 'timestamp' : perf_counter()})
                    item_list_pad, page, cursor_row = item_manager.get_item_list_output(page, cursor_row)
                    item_details_pad, cursor_row = item_manager.get_item_details_output(page, cursor_row, item_details_variant)
                    write_messages(messages_window, messages)

                    chest_tier += 1
                    chest_max_hp = get_chest_hp(chest_tier)
                    chest_remaining_hp = chest_max_hp
                    write_chest_info(chest_info_window, chest_tier, chest_max_hp, chest_remaining_hp)

                    death_type = 'safe'
                    milestones_reached = 0
                    milestone_hp = round(chest_max_hp * 0.75)

                if player_remaining_hp == 0:
                    if death_type == 'safe':
                        mode = 'crafting'
                        player_stats_pad = item_manager.get_player_stats_output()

                        wave += 1
                        chest_tier = 1
                        remaining_actions = 10 + item_manager.get_equipment_tier_total()
                        hp_drain_magnitude, hp_drain_time, chest_max_hp = get_wave_stats(wave)
                        write_wave_info(wave_info_window, wave, hp_drain_magnitude, hp_drain_time, False)
                        write_actions_and_knowledge(actions_and_knowledge_window, remaining_actions, item_manager.get_knowledge(), item_manager.get_knowledge_progress())
                        write_chest_info(chest_info_window, chest_tier, chest_max_hp)

                        messages.appendleft({'text' : 'You die, but are resurrected!', 'timestamp' : perf_counter()})
                        messages.appendleft({'text' : f'You made it to wave {wave}!', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

                    if death_type == 'dangerous':
                        mode = 'game-over'

                        waves_cleared, additional_damage = wave - 1, chest_max_hp - chest_remaining_hp
                        pb_waves_cleared, pb_additional_damage = get_personal_best()
                        if waves_cleared > pb_waves_cleared or (waves_cleared == pb_waves_cleared and additional_damage > pb_additional_damage):
                            save_personal_best(waves_cleared, additional_damage)

                        messages.appendleft({'text' : 'You have died!', 'timestamp' : perf_counter()})
                        messages.appendleft({'text' : f'Score: {waves_cleared} waves cleared + {additional_damage} damage', 'timestamp' : perf_counter()})
                        write_messages(messages_window, messages)

        while len(messages) > 0 and perf_counter() - message_duration > messages[-1]['timestamp']:
            messages.pop()
            write_messages(messages_window, messages)

        player_stats_pad.refresh(0, 0, player_stats_top, player_stats_left, player_stats_bottom, player_stats_right)
        item_list_pad.refresh(0, 0, item_list_top, item_list_left, item_list_bottom, item_list_right)
        item_details_pad.refresh(0, 0, item_details_top, item_details_left, item_details_bottom, item_details_right)
        cursor_window.refresh()
        wave_info_window.refresh()
        actions_and_knowledge_window.refresh()
        chest_info_window.refresh()
        messages_window.refresh()
        controls_window.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    game_height, game_width = 30, 118
    game_top, game_left = (curses.LINES - game_height) // 2, (curses.COLS - game_width) // 2

    while main_menu(stdscr, game_top, game_left):
        game(stdscr, game_top, game_left)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    curses.wrapper(main)
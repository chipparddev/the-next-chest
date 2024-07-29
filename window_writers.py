def write_main_menu(window, waves_cleared, additional_damage):
    window.clear()
    window.addstr(0, 0, 'The Next Chest')
    window.addstr(2, 0, f'Personal best: {waves_cleared} waves cleared + {additional_damage} damage')
    window.addstr(4, 0, 'Enter to start a new run')
    window.addstr(5, 0, 'ESC to close the game')

def write_cursor(window, character, row):
    window.clear()
    window.addstr(row, 0, f'{character}')

def write_cursor_and_marker(window, cursor_character, cursor_row, marker_character, marker_row):
    window.clear()
    window.addstr(marker_row, 0, f'{marker_character}')
    window.addstr(cursor_row, 0, f'{cursor_character}')

def write_wave_info(window, wave, hp_drain_magnitude, hp_drain_time, in_combat):
    enter_prompt = '' if in_combat else '(Press Enter to start)'
    window.clear()
    window.addstr(0, 0, f'You are on wave {wave} {enter_prompt}')
    window.addstr(1, 0, f'The HP drain rate is {hp_drain_magnitude} every {hp_drain_time}s')

def write_actions_and_knowledge(window, remaining_actions, knowledge, knowledge_progress):
    window.clear()
    window.addstr(0, 0, f'{remaining_actions} remaining actions')
    window.addstr(1, 0, f'Level {knowledge} knowledge (Next level: {knowledge_progress}/{knowledge * 15})')

def write_chest_info(window, tier, max_hp, remaining_hp = None):
    death_type = 'dangerous' if tier == 1 else 'safe'
    remaining_hp = '' if remaining_hp is None else f'{remaining_hp}/'
    window.clear()
    window.addstr(0, 0, f'Tier {tier} Chest ({death_type} death)')
    window.addstr(1, 0, f'HP: {remaining_hp}{max_hp}')

def write_messages(window, messages):
    window.clear()
    for row, message in zip(range(11, -1, -1), messages):
        text = message['text']
        window.addstr(row, 0, text)

def write_controls(window, fast_forward, modifier_ranges):
    window.addstr(0, 0, f'General controls  | ESC: Exit, WASD: Move, E: Equip/Unequip, Space: Sort inventory, 1: Toggle fast forward ({fast_forward}) ')
    window.addstr(1, 0, f'Crafting controls | Z: Identify, X: Reroll, C: Recycle, V: Scrap, B: Delete, 2: Toggle modifier ranges ({modifier_ranges}) ')
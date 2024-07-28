# The Next Chest - Setup and Gameplay Instructions

- If you experience any problems with the program (crashes, unintended gameplay, visual issues such as screen flickering), DM chip_idiot on Discord and I'll try to fix the problem.
- To keep crafting as fluid as possible, pressing the key to reroll, scrap, or delete an item will immediately alter/destroy the item you have selected, with no confirmation. Make sure you don't accidentally press the wrong key when hovering over important items.
- The game doesn't save your mid-run progress, so don't exit to the main menu or close the window unless you want to abandon your run. The only thing that gets saved is your personal best after you fully complete a run by dying to the Tier 1 Chest.

# Setup

- If you don't have Python already, install the latest version, found here: https://www.python.org/downloads/  
- If you're using Windows, you'll also need to install the curses module by typing ```pip install windows-curses``` into your command prompt.
- In your command prompt/terminal, navigate to the folder containing the game files, and type ```py main.py``` or ```python main.py``` or ```python3 main.py``` to start the game (depends on your operating system).

# How To Play

## Chest Waves

The main objective of the game is the clear as many waves of chests as possible. The condition for clearing a wave is simple - you just have to get past the first chest without dying to the HP drain. If you die on any subsequent chest, you'll be resurrected and will be able to continue to the next wave. 

Chests will drop one item upon reaching 75%, 50%, and 25% HP, and two items upon being defeated. 

## Crafting

After clearing a chest wave, you'll be given a certain amount of crafting actions. The amount that you're given is equal to 10 + the sum of your equipment tiers. This value is doubled for two handed weapons, to make up for the fact that they can't be equipped alongside a shield.

- With a T1 Dagger, T1 Light Kite Shield, and T1 Light Plate Armour equipped, you would get 13 (10 + 1 + 1 + 1) crafting actions after completion of the chest wave.
- With just a T5 Longbow equipped, you would get 20 (10 + 5 * 2) crafting actions after completion of the chest wave.

### Knowledge Levels

Knowledge levels can be earned through the identifying and scrapping actions, and serve two purposes:

1. The higher your knowledge level, the more powerful the modifiers you can roll through identifying/rerolling become.
2. In order to create a tier x item through recycling, you'll need a minimum of level x knowledge.

### Identifying

Rolls five different modifiers onto an unidentified item and grants you knowledge experience equal to the item's tier. Requires one action.

### Rerolling

Replaces the five existing modifiers on an identified item with five new ones. Requires one action.

### Recycling

You will be prompted to select two items of the same tier. These two items of tier x will then be consumed, creating a new item of tier x + 1. Requires one action.

Here's a detailed explanation of how this works:

*Every item has a slot (weapon, shield, armour, or gem), a style (melee or ranged), and a weight (light, medium, or heavy). In addition, every weapon has a hidden variant (1 or 2). When the new item is being created, each of its attributes will be randomly inherited from one of the two items that are being recycled.* 

- *If item 1 has the properties {shield, melee, light} and item 2 has the properties {shield, melee, light}, the new item will also have the properties {shield, melee, light}, and resultantly, will be guaranteed to be of the same base type.*
- *If item 1 has the properties {shield, melee, light} and item 2 has the properties {armour, ranged, heavy}, the new item will either be a shield or an armour, will be either melee-based or ranged-based, and will either be light or heavy.*

### Scrapping

Deletes an item and grants you knowledge experience equal to the item's tier. Requires one action.

*Note: Refrain from using this on the Starter Stick, as you will use an action but receive no knowledge experience.*

### Deleting

Deletes an item without using any actions.

## Calculation Rules

### Damage

- Increased damage modifiers from all sources, including your weapon, are additive with each other.
- Flat damage modifiers add to your base damage, which in turn, is multiplied by increased damage modifiers.
- Damage penalties are additive with each other but multiplicative with your total damage. A 20% damage penalty and a 10% damage penalty, for example, is equivalent to a 0.7x damage multiplier.
- After your total damage is calculated and all penalties are applied, the amount is rounded **down** to the nearest integer.

### Attack Time

- Increased attack speed modifiers from all sources, including your weapon, are additive with each other.
- After your total attack time is calculated, the amount is rounded **up** to the nearest 0.05.

### Hitpoints

- Increased total HP modifiers from all sources are additive with each other.
- Increased effect of implicit HP modifiers, which can be rolled on armour pieces, are additive with each other.
- Flat HP *and* increased effect of implicit HP modifiers add to your base HP, which in turn, is multiplied by increased total HP modifiers.
- After your total HP is calculated, the amount is rounded **down** to the nearest integer.

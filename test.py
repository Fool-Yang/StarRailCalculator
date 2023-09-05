from rail_operating_system import *
from light_cones import *
from relics import *
from time import time

ALL_WEAKNESSES = {"Physical", "Fire", "Ice", "Lightning", "Wind", "Quantum", "Imaginary"}


trial = 1
battle_length = 850
auto_heal_mode = True
show = trial == 1
records = {}
t0 = time()
for _ in range(trial):
    E1 = Boss("Boss1", weaknesses=ALL_WEAKNESSES)
    E2 = Enemy("Enemy2", weaknesses=ALL_WEAKNESSES)
    E3 = Enemy("Enemy3", weaknesses=ALL_WEAKNESSES)
    E4 = Enemy("Enemy4", weaknesses=ALL_WEAKNESSES)
    E5 = Enemy("Enemy5", weaknesses=ALL_WEAKNESSES)
    # enemies = [E1]
    enemies = [E2, E1, E3]
    # enemies = [E4, E2, E1, E3, E5]
    B = Blade()
    B = TheUnreachableSide(B)
    B = Disciple(B, main_stats=("HP Percentage", "CRIT DMG"), sub_stats=(("CRIT Rate", 0.25), ("CRIT DMG", 0.5)))
    B = Salsotto(B, main_stats=("HP Percentage", "DMG Boost"), sub_stats=(("HP Percentage", 0.4),))
    D1 = Dummy("Dummy1")
    D2 = Dummy("Dummy2")
    D3 = Dummy("Dummy3")
    players = [B, D1, D2, D3]
    Game = RailOperatingSystem(enemies, players, battle_length, auto_heal_mode, show)
    Game.run()
    for char in players:
        if char.name in records:
            for tag in char.dmg_dealt_record:
                if tag in records[char.name]:
                    records[char.name][tag] += char.dmg_dealt_record[tag]
                else:
                    records[char.name][tag] = char.dmg_dealt_record[tag]
        else:
            records[char.name] = char.dmg_dealt_record
stdout.write("Testing finished. Time taken: " + str(round(time() - t0, 3)) + " seconds\n")
stdout.write("Average Results Over " + str(trial) + " trials:\n")
for char in players:
    name = char.name
    total_dmg = sum([records[name][tag] for tag in records[name]])
    average = total_dmg / trial
    stdout.write(name + " did " + str(round(average)) + " DMG\n")
    if total_dmg > 0:
        distribution = [tag + ": " + str(round(records[name][tag] / total_dmg * 100, 1)) + "%" for tag in records[name]]
        stdout.write("; ".join(distribution) + "\n")
"""
print("\nBase Stats-----------------------")
for stat in B.stats:
    print(stat, B.stats[stat])
print("\nBuffs----------------------------")
for buff in B.buffs:
    print(buff)
print("\nDebuffs--------------------------")
for debuff in B.debuffs:
    print(debuff)
print("\nRuntime Stats--------------------")
for stat in B.runtime_stats:
    print(stat, B.runtime_stats[stat])
"""

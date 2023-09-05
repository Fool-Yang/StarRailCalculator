from light_cones.light_cone import *


class BrighterThanTheSun(LightConeDecorator):

    def __init__(self, decorated_character, hp=1058, atk=635, def_=396, stack=1):
        self.__dict__ = decorated_character.__dict__
        self.__decorated_character = decorated_character
        self.decorated_self = self
        self.stats["HP"] += hp
        self.stats["ATK"] += atk
        self.stats["DEF"] += def_
        stack_minus_1 = stack - 1
        self.stats["CRIT Rate"] += 0.18 + 0.03 * stack_minus_1
        self.__atk = (0.18 + 0.03 * stack_minus_1) * self.stats["ATK"]
        self.__energy_regeneration_rate = 0.06 + 0.01 * stack_minus_1
        # initialize hp
        self.refresh_runtime_stats()
        self.hp = self.runtime_stats["HP"]

    def basic_atk(self, targets, step):
        buff1 = {
            "ID": "Dragon's Call ATK",
            "Type": "ATK",
            "DMG Type": None,
            "Value": self.__atk,
            "Value Type": "Flat",
            "Source": None,
            "Source Stats": None,
            "Max Stack": 2,
            "Stack": 1,
            "Decay": "End",
            "Turn": 2,
            "Unlock": "Action",
            "Locked": True
        }
        buff2 = {
            "ID": "Dragon's Call Energy Regeneration Rate",
            "Type": "Energy Regeneration Rate",
            "DMG Type": None,
            "Value": self.__energy_regeneration_rate,
            "Value Type": "Flat",
            "Source": None,
            "Source Stats": None,
            "Max Stack": 2,
            "Stack": 1,
            "Decay": "End",
            "Turn": 2,
            "Unlock": "Action",
            "Locked": True
        }
        self.add_buff(buff1)
        self.add_buff(buff2)
        return self.__decorated_character.basic_atk(targets, step)

    def choose_action(self, enemies, players, sp):
        return self.__decorated_character.choose_action(enemies, players, sp)

    def check_extra_commands(self, enemies, players, blackboard):
        return self.__decorated_character.check_extra_commands(enemies, players, blackboard)

    def check_extra_action(self, enemies, players, blackboard):
        return self.__decorated_character.check_extra_action(enemies, players, blackboard)

    def check_extra_turn(self, enemies, players, sp, blackboard):
        return self.__decorated_character.check_extra_turn(enemies, players, sp, blackboard)

    def start_turn(self):
        return self.__decorated_character.start_turn()

    def take_action(self, enemies, players, sp):
        return self.__decorated_character.take_action(enemies, players, sp)

    def end_turn(self):
        return self.__decorated_character.end_turn()

    def add_buff(self, new_buff):
        return self.__decorated_character.add_buff(new_buff)

    def add_debuff(self, new_debuff):
        return self.__decorated_character.add_debuff(new_debuff)

    def amend_outgoing_effect_chance(self, chance, target, enemies, players):
        return self.__decorated_character.amend_outgoing_effect_chance(chance, target, enemies, players)

    def amend_incoming_effect_chance(self, chance, debuff, source, enemies, players):
        return self.__decorated_character.amend_incoming_effect_chance(chance, debuff, source, enemies, players)

    def maybe_add_debuff(self, chance, new_debuff):
        return self.__decorated_character.maybe_add_debuff(chance, new_debuff)

    def dispel_buff(self, buff):
        return self.__decorated_character.dispel_buff(buff)

    def dispel_debuff(self, debuff):
        return self.__decorated_character.dispel_debuff(debuff)

    def unlock_buffs_debuffs(self, keyword):
        return self.__decorated_character.unlock_buffs_debuffs(keyword)

    def refresh_runtime_stats(self):
        return self.__decorated_character.refresh_runtime_stats()

    def start_atk(self, targets, enemies, players):
        return self.__decorated_character.start_atk(targets, enemies, players)

    def end_dmg(self, data, enemies, players):
        return self.__decorated_character.end_dmg(data, enemies, players)

    def end_atk(self, targets, enemies, players):
        return self.__decorated_character.end_atk(targets, enemies, players)

    def end_taking_atk(self, energy, enemies, players):
        return self.__decorated_character.end_taking_atk(energy, enemies, players)

    def amend_outgoing_dmg(self, dmg_and_break, target, tags, enemies, players):
        return self.__decorated_character.amend_outgoing_dmg(dmg_and_break, target, tags, enemies, players)

    def crit_dmg(self, dmg_and_break, target, tags, enemies, players, expected=True):
        return self.__decorated_character.crit_dmg(dmg_and_break, target, tags, enemies, players, expected)

    def reduce_incoming_dmg(self, dmg_and_break, source, tags, enemies, players):
        return self.__decorated_character.reduce_incoming_dmg(dmg_and_break, source, tags, enemies, players)

    def take_dmg(self, dmg_and_break, source, tags, enemies, players):
        return self.__decorated_character.take_dmg(dmg_and_break, source, tags, enemies, players)

    def consume_hp(self, hp, source, enemies, players):
        return self.__decorated_character.consume_hp(hp, source, enemies, players)

    def amend_outgoing_healing(self, hp, target, enemies, players):
        return self.__decorated_character.amend_outgoing_healing(hp, target, enemies, players)

    def amend_incoming_healing(self, hp, source, enemies, players):
        return self.__decorated_character.amend_incoming_healing(hp, source, enemies, players)

    def take_healing(self, hp, source, enemies, players):
        return self.__decorated_character.take_healing(hp, source, enemies, players)

    def try_activate_ult(self, enemies, players):
        return self.__decorated_character.try_activate_ult(enemies, players)

    def skill(self, targets, step):
        return self.__decorated_character.skill(targets, step)

    def ultimate(self, targets, step):
        return self.__decorated_character.ultimate(targets, step)

    def talent(self, targets, step):
        return self.__decorated_character.talent(targets, step)

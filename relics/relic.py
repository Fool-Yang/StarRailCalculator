from characters import *

# define constants
RELIC_MAIN_STATS = {
    "HP": 705.5,
    "HP Percentage": 0.432,
    "ATK": 352.7,
    "ATK Percentage": 0.432,
    "DEF Percentage": 0.54,
    "SPD": 25,
    "CRIT Rate": 0.324,
    "CRIT DMG": 0.648,
    "Outgoing Healing Boost": 0.3456,
    "Effect Hit Rate": 0.432,
    "Break Effect": 0.648,
    "Energy Regeneration Rate": 0.1944,
    "DMG Boost": 0.3888
}


class RelicDecorator(Character):
    # the following code is here as a template
    # do not call any of these methods with super() in child classes, but do copy and paste the following code instead
    # read light_cone.py for the reason

    @abstractmethod
    def __init__(self, decorated_character, main_stats, sub_stats):
        self.__dict__ = decorated_character.__dict__
        self.__decorated_character = decorated_character
        self.decorated_self = self
        for stats in main_stats:
            if stats in self.extra_stats:
                self.extra_stats[stats] += RELIC_MAIN_STATS[stats]
            elif stats == "DMG Boost":
                self.stats[stats][self.dmg_type] += RELIC_MAIN_STATS[stats]
            elif stats in self.stats["DMG Boost"]:
                self.stats["DMG Boost"][stats] += RELIC_MAIN_STATS["DMG Boost"]
            else:
                self.stats[stats] += RELIC_MAIN_STATS[stats]
        for sub_stats, value in sub_stats:
            if sub_stats in self.extra_stats:
                self.extra_stats[sub_stats] += value
            else:
                self.stats[sub_stats] += value
        self.refresh_runtime_stats()

    @abstractmethod
    def choose_action(self, enemies, players, sp):
        return self.__decorated_character.choose_action(enemies, players, sp)

    @abstractmethod
    def check_extra_commands(self, enemies, players, blackboard):
        return self.__decorated_character.check_extra_commands(enemies, players, blackboard)

    @abstractmethod
    def check_extra_action(self, enemies, players, blackboard):
        return self.__decorated_character.check_extra_action(enemies, players, blackboard)

    @abstractmethod
    def check_extra_turn(self, enemies, players, sp, blackboard):
        return self.__decorated_character.check_extra_turn(enemies, players, sp, blackboard)

    @abstractmethod
    def start_turn(self):
        return self.__decorated_character.start_turn()

    @abstractmethod
    def take_action(self, enemies, players, sp):
        return self.__decorated_character.take_action(enemies, players, sp)

    @abstractmethod
    def end_turn(self):
        return self.__decorated_character.end_turn()

    @abstractmethod
    def add_buff(self, new_buff):
        return self.__decorated_character.add_buff(new_buff)

    @abstractmethod
    def add_debuff(self, new_debuff):
        return self.__decorated_character.add_debuff(new_debuff)

    @abstractmethod
    def amend_outgoing_effect_chance(self, chance, target, enemies, players):
        return self.__decorated_character.amend_outgoing_effect_chance(chance, target, enemies, players)

    @abstractmethod
    def amend_incoming_effect_chance(self, chance, debuff, source, enemies, players):
        return self.__decorated_character.amend_incoming_effect_chance(chance, debuff, source, enemies, players)

    @abstractmethod
    def maybe_add_debuff(self, chance, new_debuff):
        return self.__decorated_character.maybe_add_debuff(chance, new_debuff)

    @abstractmethod
    def dispel_buff(self, buff):
        return self.__decorated_character.dispel_buff(buff)

    @abstractmethod
    def dispel_debuff(self, debuff):
        return self.__decorated_character.dispel_debuff(debuff)

    @abstractmethod
    def unlock_buffs_debuffs(self, keyword):
        return self.__decorated_character.unlock_buffs_debuffs(keyword)

    @abstractmethod
    def refresh_runtime_stats(self):
        return self.__decorated_character.refresh_runtime_stats()

    @abstractmethod
    def start_atk(self, targets, enemies, players):
        return self.__decorated_character.start_atk(targets, enemies, players)

    @abstractmethod
    def end_dmg(self, data, enemies, players):
        return self.__decorated_character.end_dmg(data, enemies, players)

    @abstractmethod
    def end_atk(self, targets, enemies, players):
        return self.__decorated_character.end_atk(targets, enemies, players)

    @abstractmethod
    def amend_outgoing_dmg(self, dmg_and_break, target, tags, enemies, players):
        return self.__decorated_character.amend_outgoing_dmg(dmg_and_break, target, tags, enemies, players)

    @abstractmethod
    def crit_dmg(self, dmg_and_break, target, tags, enemies, players, expected=True):
        return self.__decorated_character.crit_dmg(dmg_and_break, target, tags, enemies, players, expected)

    @abstractmethod
    def reduce_incoming_dmg(self, dmg_and_break, source, tags, enemies, players):
        return self.__decorated_character.reduce_incoming_dmg(dmg_and_break, source, tags, enemies, players)

    @abstractmethod
    def take_dmg(self, dmg_and_break, source, tags, enemies, players):
        return self.__decorated_character.take_dmg(dmg_and_break, source, tags, enemies, players)

    @abstractmethod
    def consume_hp(self, hp, source, enemies, players):
        return self.__decorated_character.consume_hp(hp, source, enemies, players)

    @abstractmethod
    def amend_outgoing_healing(self, hp, target, enemies, players):
        return self.__decorated_character.amend_outgoing_healing(hp, target, enemies, players)

    @abstractmethod
    def amend_incoming_healing(self, hp, source, enemies, players):
        return self.__decorated_character.amend_incoming_healing(hp, source, enemies, players)

    @abstractmethod
    def take_healing(self, hp, source, enemies, players):
        return self.__decorated_character.take_healing(hp, source, enemies, players)

    @abstractmethod
    def try_activate_ult(self, enemies, players):
        return self.__decorated_character.try_activate_ult(enemies, players)

    @abstractmethod
    def basic_atk(self, targets, step):
        return self.__decorated_character.basic_atk(targets, step)

    @abstractmethod
    def skill(self, targets, step):
        return self.__decorated_character.skill(targets, step)

    @abstractmethod
    def ultimate(self, targets, step):
        return self.__decorated_character.ultimate(targets, step)

    @abstractmethod
    def talent(self, targets, step):
        return self.__decorated_character.talent(targets, step)

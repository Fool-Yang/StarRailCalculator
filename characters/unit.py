from abc import ABC, abstractmethod
from random import random


class Unit(ABC):
    """
    The units in the battle. Units answer calls from the operating system in battle and generate actions/commands.\n
    Although, the way the system deals with extra command is already enough to handle any effects that triggers at
    any time, effects that triggers with attacks are very common. To improve both running and coding efficiency,
    three methods for that purpose is defined in the Unit class, start_attack(.), end_dmg(.) and end_attack(.).
    Effects that triggers at those phases can be directly defined in those methods or they can be defined in the
    Unit.check_extra_commands(.) method which will have to read the blackboard.

    Attributes:
    ----------
    decorated_self: Unit
        A reference to itself or the outermost decorator when the unit is decorated with decorator objects
    name: str
        The name of the unit
    dmg_type: str
        The unit's damage type
    path: str
        The unit's path
    level: int
        The unit's level
    max_energy: int
        The unit's max energy
    stats: dict
        The base stats of the unit\n
        The stats names are directly copied from the game (HP actually means Max HP)
    runtime_stats: dict
        The runtime stats of the unit in battle
    weaknesses: set
        The weaknesses of the unit (empty for player players)
    max_toughness: int
        The max toughness of the unit (it is a dummy variable for player players)
    toughness: float
        The current toughness of the unit (it is a dummy variable for player players)
    low_extra_turn_priority: bool
        Whether ultimate can be used during the unit's extra turn
    in_extra_turn: bool
        A flag indicating whether the unit is running an extra turn
    buffs: list
        The list of buffs on the unit
    debuffs: list
        The list of debuffs on the unit
    hp: float
        The unit's current HP
    energy: float
        The unit's current energy
    dmg_dealt_record: dict
        A record of the damage the unit dealt classified into different sources
    break_dmg_dealt_record: dict
        A record of the break damage the unit dealt classified into different sources
    """

    # initialize stats
    def __init__(
            self, name,
            dmg_type,
            path,
            taunt,
            hp, atk,
            def_, spd,
            crit_rate, crit_dmg,
            break_effect,
            outgoing_healing_boost, incoming_healing_boost,
            max_energy, energy_regen,
            effect_hit_rate, effect_res, crowd_control_res,
            physical_dmg_boost,
            fire_dmg_boost,
            ice_dmg_boost,
            lightning_dmg_boost,
            wind_dmg_boost,
            quantum_dmg_boost,
            imaginary_dmg_boost,
            physical_res_boost,
            fire_res_boost,
            ice_res_boost,
            lightning_res_boost,
            wind_res_boost,
            quantum_res_boost,
            imaginary_res_boost
    ):

        self.name = name
        self.dmg_type = dmg_type
        self.path = path
        self.level = 80
        self.max_energy = max_energy
        # character's base stats (only the ones that can be affected by buffs/debuffs should be here)
        # the whole point of using dict is for buffs can be implemented easily
        self.stats = {
            "Taunt": taunt,
            "HP": hp,
            "ATK": atk,
            "DEF": def_,
            "SPD": spd,
            "CRIT Rate": crit_rate,
            "CRIT DMG": crit_dmg,
            "Break Effect": break_effect,
            "Outgoing Healing Boost": outgoing_healing_boost,
            "Incoming Healing Boost": incoming_healing_boost,
            "Energy Regeneration Rate": energy_regen,
            "Effect Hit Rate": effect_hit_rate,
            "Effect RES": effect_res,
            "Crowd Control RES": crowd_control_res,
            # DMG Boost types can be added dynamically, so I have to use a dict
            # like they may boost fire dmg, dot, skill dmg, and more in the future
            # these works well with the implemented dmg tags
            "DMG Boost": {
                "All": 0,
                "Physical": physical_dmg_boost,
                "Fire": fire_dmg_boost,
                "Ice": ice_dmg_boost,
                "Lightning": lightning_dmg_boost,
                "Wind": wind_dmg_boost,
                "Quantum": quantum_dmg_boost,
                "Imaginary": imaginary_dmg_boost
            },
            "RES Boost": {
                "Physical": physical_res_boost,
                "Fire": fire_res_boost,
                "Ice": ice_res_boost,
                "Lightning": lightning_res_boost,
                "Wind": wind_res_boost,
                "Quantum": quantum_res_boost,
                "Imaginary": imaginary_res_boost
            },
            # DMG Taken Increase types can be dynamically added, like Sampo's ultimate applies dot taken increase
            "DMG Taken Increase": {"All": 0},
            "DMG Taken Decrease": 0,
            "DEF Ignore": 0,
            "RES PEN": {
                "Physical": 0,
                "Fire": 0,
                "Ice": 0,
                "Lightning": 0,
                "Wind": 0,
                "Quantum": 0,
                "Imaginary": 0
            },
            "Weaken": 0
        }
        # sometimes the unit returns a reference to itself
        # but when it's decorated, self should be the outer most decorator
        # this will be overwritten by every decorator
        self.decorated_self = self
        # run time stats are used in calculations
        # they can be affected by buffs/debuffs
        self.runtime_stats = {stats_type: self.stats[stats_type] for stats_type in self.stats}
        stats_dict = self.stats["DMG Boost"]
        self.runtime_stats["DMG Boost"] = {key: stats_dict[key] for key in stats_dict}
        stats_dict = self.stats["RES Boost"]
        self.runtime_stats["RES Boost"] = {key: stats_dict[key] for key in stats_dict}
        stats_dict = self.stats["DMG Taken Increase"]
        self.runtime_stats["DMG Taken Increase"] = {key: stats_dict[key] for key in stats_dict}
        stats_dict = self.stats["RES PEN"]
        self.runtime_stats["RES PEN"] = {key: stats_dict[key] for key in stats_dict}
        # enemy units will redefine weaknesses and toughness
        # these are dummy attributes for player players so all units can share the same dmg process
        # also in case they add toughness for players in the future
        self.weaknesses = set()
        self.max_toughness = 100
        self.toughness = self.max_toughness
        # we can't insert ultimate in Seele's extra turn before she takes action
        # but we can do that for some other players which has low priority
        self.low_extra_turn_priority = True
        self.in_extra_turn = False
        self.buffs = []
        self.debuffs = []
        self.crowd_control = set()
        # initialize hp and energy
        self.refresh_runtime_stats()
        self.hp = self.runtime_stats["HP"]
        self.energy = max_energy / 2

        self.dmg_dealt_record = {}
        self.break_dmg_dealt_record = {}

    @abstractmethod
    def choose_action(self, enemies, players, sp):
        """
        Choose an action given the current state of the game.

        Parameters:
        ----------
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        sp: int
            The number of skill points available

        Returns:
        -------
        A tuple representing the action
        """
        pass

    def take_action(self, enemies, players, sp):
        """
        Unlocks buffs and debuffs that unlock at the action phase, then calls choose_action().
        (De)buffs are locked when applied. Locked buffs can't decay. Most buffs unlock at the start of the action phase.
        In unit U's turn, if you buff U after U take an action, the buff usually don't decay at turn end,
        but if you buff U with other units' ultimate first, then let U take action, the buff will decay at turn end.
        This explains why Sleep Like the Dead's buff don't decay after the turn it's triggered.
        """
        self.unlock_buffs_debuffs("Action")
        self.toughness = self.max_toughness
        return self.choose_action(enemies, players, sp)

    def check_extra_commands(self, enemies, players, blackboard):
        """
        Checks if the unit wants to run any extra command. If so, return a batch of commands.

        Parameters:
        ----------
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        blackboard: list
            A list of all actions/commands executed this turn

        Returns:
        -------
        A tuple of commands
        """
        return tuple()

    def check_extra_action(self, enemies, players, blackboard):
        """
        Checks if the unit wants to run any extra action. If so, return an action.

        Parameters:
        ----------
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        blackboard: list
            A list of all actions/commands executed this turn

        Returns:
        -------
        An action or None
        """
        return

    def check_extra_turn(self, enemies, players, sp, blackboard):
        """
        Checks if the unit wants to run any extra turn. If so, return an action.

        Parameters:
        ----------
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        sp:
            The number of skill points available
        blackboard: list
            A list of all actions/commands executed this turn

        Returns:
        -------
        An action or None
        """
        return

    def start_turn(self):
        """
        Starts the turn and deal with buffs/debuffs that take effects at the turn-start phase.
        Returns a batch of commands (may be empty). These are typically DMG commands from DoT or Heal commands.

        Returns:
        -------
        A tuple of commands
        """
        self.unlock_buffs_debuffs("Start")
        # might produce commands for DoT or healing, etc.
        commands = []
        removed_ones = []
        removed_any = False
        for buff in self.buffs:
            if buff["Decay"] == "Start" and not buff["Locked"]:
                buff["Turn"] -= 1
                if buff["Turn"] <= 0:
                    removed_ones.append(buff)
                    removed_any = True
            if buff["Type"] == "Heal":
                hp = buff["Stack"] * buff["Value"]
                if buff["Value Type"] == "Percentage":
                    hp *= buff["Source"].runtime_stats[buff["Source Stats"]]
                data = ((self.decorated_self, hp),)
                commands.append(("Heal", buff["Source"], data))
        for buff in removed_ones:
            self.buffs.remove(buff)
        removed_ones = []
        for debuff in self.debuffs:
            if debuff["Decay"] == "Start" and not debuff["Locked"]:
                debuff["Turn"] -= 1
                if debuff["Turn"] <= 0:
                    removed_ones.append(debuff)
                    removed_any = True
            if debuff["Type"] == "DoT":
                dmg = debuff["Stack"] * debuff["Value"]
                if debuff["Value Type"] == "Percentage":
                    dmg *= debuff["Source"].runtime_stats[debuff["Source Stats"]]
                tags = (debuff["ID"], "DoT", debuff["DMG Type"])
                data = ((self.decorated_self, (dmg, 0), tags),)
                commands.append(("DMG", debuff["Source"], data))
        for debuff in removed_ones:
            self.debuffs.remove(debuff)
        if removed_any:
            self.refresh_runtime_stats()
        return tuple(commands)

    def end_turn(self):
        """
        Ends the turn and deal with buffs/debuffs that take effects at the turn-end phase.
        Returns a batch of commands (may be empty).

        Returns:
        -------
        A tuple of commands
        """
        commands = []
        self.unlock_buffs_debuffs("End")
        removed_ones = []
        removed_any = False
        for buff in self.buffs:
            if buff["Decay"] == "End" and not buff["Locked"]:
                buff["Turn"] -= 1
                if buff["Turn"] <= 0:
                    removed_ones.append(buff)
                    removed_any = True
        for buff in removed_ones:
            self.buffs.remove(buff)
        removed_ones = []
        for debuff in self.debuffs:
            if debuff["Decay"] == "End" and not debuff["Lock"]:
                debuff["Turn"] -= 1
                if debuff["Turn"] <= 0:
                    removed_ones.append(debuff)
                    removed_any = True
        for debuff in removed_ones:
            self.debuffs.remove(debuff)
        if "Frozen" in self.crowd_control:
            data = ((self.decorated_self, 0.5),)
            commands.append(("Advance", self.decorated_self, data))
        if removed_any:
            self.refresh_runtime_stats()
        return tuple(commands)

    def add_buff(self, new_buff):
        """
        Adds a buff to this unit and automatically refreshes runtime stats. Adding an existing one stacks/renews it.

        Parameters:
        ----------
        new_buff: dict
            The buff to be added\n
            An template buff = {
                "ID": "Example Buff",\n
                "Type": "DMG Boost",\n
                "DMG Type": "Fire",\n
                "Value Type": "Flat"\n
                "Value": 0.2,\n
                "Source": None,\n
                "Source Stats": None,\n
                "Max Stack": 1,\n
                "Stack": 1,\n
                "Decay": "End",\n
                "Turn": 3,\n
                "Unlock": "Action",\n
                "Locked": True\n
            }
        """
        for buff in self.buffs:
            if buff["ID"] == new_buff["ID"]:
                new_stack = buff["Stack"] + new_buff["Stack"]
                if new_stack > buff["Max Stack"]:
                    new_stack = buff["Max Stack"]
                buff["Value"] = new_buff["Value"]
                buff["Stack"] = new_stack
                buff["Turn"] = new_buff["Turn"]
                buff["Locked"] = new_buff["Locked"]
                break
        else:
            self.buffs.append(new_buff)
        self.refresh_runtime_stats()

    def add_debuff(self, new_debuff):
        """
        Adds a debuff to this unit and automatically refreshes runtime stats. Adding an existing one stacks/renews it.

        Parameters:
        ----------
        new_debuff: dict
            The debuff to be added\n
            An template debuff = {
                "ID": "Example Debuff",\n
                "Type": "DoT",\n
                "DMG Type": "Physical",\n
                "Value Type": "Percentage"\n
                "Value": 0.6,\n
                "Source": applier_unit,\n
                "Source Stats": "ATK",\n
                "Max Stack": 5,\n
                "Stack": 2,\n
                "Decay": "Start",\n
                "Turn": 2,\n
                "Unlock": "Start",\n
                "Locked": True\n
            }
        """
        for debuff in self.debuffs:
            if debuff["ID"] == new_debuff["ID"]:
                new_stack = debuff["Stack"] + new_debuff["Stack"]
                if new_stack > debuff["Max Stack"]:
                    new_stack = debuff["Max Stack"]
                debuff["Value"] = new_debuff["Value"]
                debuff["Stack"] = new_stack
                debuff["Turn"] = new_debuff["Turn"]
                debuff["Locked"] = new_debuff["Locked"]
                break
        else:
            self.debuffs.append(new_debuff)
        self.refresh_runtime_stats()

    def amend_outgoing_effect_chance(self, chance, target, enemies, players):
        """
        Calculates the chance to apply debuff affected by the Effect Hit Rate stats

        Parameters:
        ----------
        chance: float
            The chance to apply debuff (can be more than 1)
        target: Unit
            The target of the debuff
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified chance (can be more than 1)
        """
        return (1 + self.runtime_stats["Effect Hit Rate"]) * chance

    def amend_incoming_effect_chance(self, chance, source, enemies, players):
        """
        Calculates the chance to apply debuff affected by the Effect RES stats

        Parameters:
        ----------
        chance: float
            The chance to apply debuff (can be more than 1)
        source: Unit
            The source unit of the debuff
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified chance restricted to the range [0, 1]
        """
        chance = (1 - self.runtime_stats["Effect RES"]) * chance
        if chance < 0:
            chance = 0
        elif chance > 1:
            chance = 1
        return chance

    def maybe_add_debuff(self, chance, new_debuff):
        """
        Applies debuff probabilistically.

        Parameters:
        ----------
        chance: float
            The chance to apply debuff (can be more than 1)
        new_debuff: dict
            The debuff to be added

        Returns:
        -------
        True if the debuff is successfully applied
        """
        if random() < chance:
            self.add_debuff(new_debuff)
            return True
        return False

    def dispel_buff(self, buff):
        """
        Removes a buff.

        Parameters:
        ----------
        buff: dict
            The buff to be removed from this unit
        """
        self.buffs.remove(buff)
        self.refresh_runtime_stats()

    def dispel_debuff(self, debuff):
        """
        Removes a debuff.

        Parameters:
        ----------
        debuff: dict
            The debuff to be removed from this unit
        """
        self.debuffs.remove(debuff)
        self.refresh_runtime_stats()

    def unlock_buffs_debuffs(self, keyword):
        """
        Unlocks buffs and debuffs that unlock at the specified phase.

        Parameters:
        ----------
        keyword: str
            The keyword to search for when unlocking buffs/debuffs
        """
        for buff in self.buffs:
            if buff["Unlock"] == keyword:
                buff["Locked"] = False
        for debuff in self.debuffs:
            if debuff["Unlock"] == keyword:
                debuff["Locked"] = False

    def refresh_runtime_stats(self):
        """
        Updates runtime stats according to the buffs/debuffs on this unit. It rebuilds runtime_stats from base stats and
        buffs/debuffs.
        """
        stats_with_dmg_type = ("DMG Boost", "RES Boost", "DMG Taken Increase", "RES PEN")
        # make a deep copy
        for key in self.stats:
            stats = self.stats[key]
            if type(stats) is dict:
                for sub_key in stats:
                    self.runtime_stats[key][sub_key] = stats[sub_key]
            else:
                self.runtime_stats[key] = stats
        self.crowd_control = set()
        # count buffs/debuffs
        for buff in self.buffs:
            type_name = buff["Type"]
            dmg_type = buff["DMG Type"]
            value = buff["Stack"] * buff["Value"]
            if type_name == "DMG Taken Decrease":
                self.runtime_stats[type_name] = 1 - (1 - self.runtime_stats[type_name]) * (1 - value)
            elif type_name in stats_with_dmg_type:
                if dmg_type in self.runtime_stats[type_name]:
                    self.runtime_stats[type_name][dmg_type] += value
                else:
                    self.runtime_stats[type_name][dmg_type] = value
            elif type_name in self.runtime_stats:
                self.runtime_stats[type_name] += value
        for debuff in self.debuffs:
            type_name = debuff["Type"]
            dmg_type = debuff["DMG type"]
            value = debuff["Stack"] * debuff["Value"]
            if type_name in stats_with_dmg_type:
                if dmg_type in self.runtime_stats[type_name]:
                    self.runtime_stats[type_name][dmg_type] -= value
                else:
                    self.runtime_stats[type_name][dmg_type] = -value
            elif type_name in self.runtime_stats:
                self.runtime_stats[type_name] -= value
            elif type_name == "Crowd Control":
                debuff_id = debuff["ID"]
                self.crowd_control.add(debuff_id)
                if debuff_id == "Imprisoned":
                    self.runtime_stats["SPD"] -= value
        # avoid non-positive speed
        if self.runtime_stats["SPD"] < 0.01:
            self.runtime_stats["SPD"] = 0.01

    def start_atk(self, data, enemies, players):
        """
        Starts an attack process. Normally does nothing but on-attack effects might trigger.

        Parameters:
        ----------
        data: tuple
            The same data a DMG command uses
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        A tuple of commands
        """
        return tuple()

    def end_dmg(self, data, enemies, players):
        """
        Ends a damage process. Normally does nothing but after-damage effects might trigger.

        Parameters:
        ----------
        data: tuple
            The same data a DMG command message on the blackboard, which is normal DMG command plus crit information
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        A tuple of commands
        """
        return tuple()

    def end_atk(self, data, enemies, players):
        """
        Ends an attack process. Normally does nothing but after-attack effects might trigger.

        Parameters:
        ----------
        data: tuple
            The same data a DMG command uses
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        A tuple of commands
        """
        return tuple()

    def amend_outgoing_dmg(self, dmg_and_break, target, tags, enemies, players):
        """
        Calculates the amended outgoing damage affected by the DMG Boost stats and Weaken effects.

        Parameters:
        ----------
        dmg_and_break: tuple
            The damage and break damage pair
        target: Unit
            The target of the damage
        tags: tuple
            The list of all the tags attached to a damage\n
            The first one is defined by the code that generated the DMG command ("Skill", "Basic ATK", etc.).
            The last one is always the damage type ("Physical", "Fire", etc.).
            Tags like "Follow-Up Attack" goes in the middle.
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified (damage, break_damage)
        """
        dmg, break_dmg = dmg_and_break
        dmg_boost = self.runtime_stats["DMG Boost"]
        multiplier1 = 1 + dmg_boost["All"]
        for tag in tags:
            if tag in dmg_boost:
                multiplier1 += dmg_boost[tag]
        multiplier2 = 1 - self.runtime_stats["Weaken"]
        return multiplier1 * multiplier2 * dmg, break_dmg

    def crit_dmg(self, dmg_and_break, target, tags, enemies, players, expected=True):
        """
        Calculates the critical outgoing damage. Calculates the expected damage by default.

        Parameters:
        ----------
        dmg_and_break: tuple
            The damage and break damage pair
        target: Unit
            The target of the damage
        tags: tuple
            The list of all the tags attached to a damage\n
            The first one is defined by the code that generated the DMG command ("Skill", "Basic ATK", etc.).
            The last one is always the damage type ("Physical", "Fire", etc.).
            Tags like "Follow-Up Attack" goes in the middle.
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        expected: bool
            Whether to calculate the expected damage or do an rng check for crit

        Returns:
        -------
        The modified (damage, break_damage) and whether it critically hits
        """
        dmg, break_dmg = dmg_and_break
        crit = False
        multiplier = 1
        # only non-DoT can crit
        if "DoT" not in tags:
            # in most cases just calculate the expected dmg
            # for effects that play with crit like Sleep Like the Dead, do crit rng check
            if expected:
                effective_crit_rate = self.runtime_stats["CRIT Rate"]
                if effective_crit_rate < 0:
                    effective_crit_rate = 0
                elif effective_crit_rate > 1:
                    effective_crit_rate = 1
                multiplier += effective_crit_rate * self.runtime_stats["CRIT DMG"]
            elif random() < self.runtime_stats["CRIT Rate"]:
                crit = True
                multiplier += self.runtime_stats["CRIT DMG"]
        return (multiplier * dmg, break_dmg), crit

    def reduce_incoming_dmg(self, dmg_and_break, source, tags, enemies, players):
        """
        Calculates the reduced incoming damage affected by the the DEF, DEF Ignore, RES Boost, RES PEN
        and DMG Taken Increase stats.

        Parameters:
        ----------
        dmg_and_break: tuple
            The damage and break damage pair
        source: Unit
            The source unit of the damage
        tags: tuple
            The list of all the tags attached to a damage\n
            The first one is defined by the code that generated the DMG command ("Skill", "Basic ATK", etc.).
            The last one is always the damage type ("Physical", "Fire", etc.).
            Tags like "Follow-Up Attack" goes in the middle.
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified (damage, break_damage)
        """
        dmg, break_dmg = dmg_and_break
        effective_def = self.runtime_stats["DEF"] - source.runtime_stats["DEF Ignore"] * self.runtime_stats["DEF"]
        if effective_def < 0:
            effective_def = 0
        multiplier1 = (source.level * 10 + 200) / (source.level * 10 + 200 + effective_def)
        dmg_type = tags[-1]
        effective_res = self.runtime_stats["RES Boost"][dmg_type] - source.runtime_stats["RES PEN"][dmg_type]
        if effective_res < -1:
            effective_res = -1
        elif effective_res > 0.9:
            effective_res = 0.9
        multiplier2 = 1 - effective_res
        dmg_taken_increase = self.runtime_stats["DMG Taken Increase"]
        multiplier3 = 1 + dmg_taken_increase["All"]
        for tag in tags:
            if tag in dmg_taken_increase:
                multiplier3 += dmg_taken_increase[tag]
        if multiplier3 > 3.5:
            multiplier3 = 3.5
        multiplier4 = 1 - self.runtime_stats["DMG Taken Decrease"]
        return multiplier1 * multiplier2 * multiplier3 * multiplier4 * dmg, break_dmg

    def take_dmg(self, dmg_and_break, source, tags, enemies, players):
        """
        Takes damage.

        Parameters:
        ----------
        dmg_and_break: tuple
            The damage and break damage pair
        source: Unit
            The source unit of the damage
        tags: tuple
            The list of all the tags attached to a damage\n
            The first one is defined by the code that generated the DMG command ("Skill", "Basic ATK", etc.).
            The last one is always the damage type ("Physical", "Fire", etc.).
            Tags like "Follow-Up Attack" goes in the middle.
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units
        """
        dmg, break_dmg = dmg_and_break
        if tags[-1] not in self.weaknesses:
            break_dmg = 0
        self.hp -= dmg
        self.toughness -= break_dmg

    def consume_hp(self, hp, source, enemies, players):
        """
        Consumes HP.

        Parameters:
        ----------
        hp: float
            The amount of HP to be consumed
        source: Unit
            The source unit who consumes this unit's HP
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The actual consumed HP (can't go below 1 HP)
        """
        original_hp = self.hp
        self.hp -= hp
        if self.hp < 1:
            self.hp = 1
        return original_hp - self.hp

    def amend_outgoing_healing(self, hp, target, enemies, players):
        """
        Calculates the amended outgoing healing affected by the Outgoing Healing Boost stats.

        Parameters:
        ----------
        hp: float
            The amount of HP to be restored
        target: Unit
            The target of the healing
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified healing amount
        """
        return (1 + self.runtime_stats["Outgoing Healing Boost"]) * hp

    def amend_incoming_healing(self, hp, source, enemies, players):
        """
        Calculates the amended incoming healing affected by the Incoming Healing Boost stats.

        Parameters:
        ----------
        hp: float
            The amount of HP to be restored
        source: Unit
            The source unit of the healing
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The modified healing amount
        """
        return (1 + self.runtime_stats["Incoming Healing Boost"]) * hp

    def take_healing(self, hp, source, enemies, players):
        """
        Restores HP.

        Parameters:
        ----------
        hp: float
            The amount of HP to be restored
        source: Unit
            The source unit who heals this unit
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        The actual healed amount (not counting excess healing)
        """
        original_hp = self.hp
        self.hp += hp
        if self.hp > self.runtime_stats["HP"]:
            self.hp = self.runtime_stats["HP"]
        return self.hp - original_hp

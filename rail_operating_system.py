from characters import *
from sys import stdout


class RailOperatingSystem:
    """
    A class used to run the HSR battle.\n
    The operating system is in charge of all the battle units.
    It decides whose turn it is, and keeps track of who does damage to whom, etc.
    All behaviours of units need to be reported to the system. The system then executes the commands.
    Try to avoid direct communication between units.
    i.e. if A wants to do damage to B, it needs to tell the system A deals damage to B rather than modifying B's HP.

    Attributes:
    ----------
    enemies: list
        A list of enemy units
    players: list
        A list of player units
    battle_length: float
        The length of battle measured in time units
    auto_heal_mode: bool
        Whether the units will restore to full health after taking damage
    show_action: bool
        Whether to show the units' actions on the screen
    battle_log: str
        The transcript of the battle
    sp: int
        How many skill points the player has
    sp_cap: int
        The max skill points the player can have
    time_passed: float
        Keeps track of how much time has passed in the battle
    distances: dict
        A dictionary that records the distance from each unit to the endpoint
    queue: list
        A sorted list of (time: float, unit: Unit) representing the time left for the unit to start its next turn
    blackboard: list
        A list of all the events happened this turn\n
        Used as a broadcasting tool for action information.
        e.g. if a unit does follow-up attacks after a teammate, it needs to know if someone took the attack action.
        A set where units can sign to indicate they have read the message is also added to each entry.
    """

    def __init__(self, enemies, players, battle_length=850, auto_heal_mode=False, show_action=False):
        self.enemies = enemies
        self.players = players
        self.battle_length = battle_length
        self.auto_heal_mode = auto_heal_mode
        self.show_action = show_action
        self.battle_log = ""
        self.sp = 3
        self.sp_cap = 5
        self.time_passed = 0
        units = enemies + players
        self.queue = []
        self.distances = {unit: 10000 for unit in units}
        self.blackboard = []
        # put all the units into the queue and assign time and distance
        for unit in units:
            # basic math, time = distance/speed
            time = self.distances[unit] / unit.runtime_stats["SPD"]
            self.queue.append([time, unit])
        # sort them by time so the first in the queue is the unit that moves next
        self.queue.sort(key=lambda x: x[0])

    def tic(self):
        """
        Proceeds with the game. Pick up the next unit and resolve its turn, then update the queue.

        Returns:
        -------
        True if the game is still running or False if it ends
        """
        # find the first unit in the queue and how much time it takes to start its next turn, then pass that much time
        time, next_unit = self.queue[0]
        self.time_passed += time
        if self.time_passed > self.battle_length:
            return False
        # pass that much time for every unit in the queue and compute the new distance for them
        for time_and_unit in self.queue:
            time_and_unit[0] -= time
            unit = time_and_unit[1]
            # basic math, distance = speed*time
            self.distances[unit] -= unit.runtime_stats["SPD"] * time
        # resolve the turn
        self.run_turn(next_unit)
        # update the time in the queue since there are potential speed changes then sort the queue by time
        for time_and_unit in self.queue:
            unit = time_and_unit[1]
            # basic math, time = distance/speed
            time_and_unit[0] = self.distances[unit] / unit.runtime_stats["SPD"]
        self.queue.sort(key=lambda x: x[0])
        return True

    def run_turn(self, unit):
        """
        Resolve the next unit's turn, then resolve extra turns if any.
        """
        if self.show_action:
            self.battle_log += "At time step " + str(round(self.time_passed, 1)) + ": SP = " + str(self.sp) + "\n"
        # resolve the turn and put the unit back to the starting position (10,000 away)
        self.run_commands(unit.start_turn())
        # different units have different ways to resolve turns
        # bosses can run several turns in a row
        # according to reverse engineering, they aren't extra turns
        # because they can be interrupted and some debuffs can decay (Pela's ice res decrease)
        # they are not action advance because most debuffs don't decay
        # they are really their own things and we call them mini turns
        if isinstance(unit, Boss):
            while unit.turns_left > 0:
                action = unit.take_action(self.enemies, self.players, self.sp)
                self.run_action(action)
                self.check_extra_turn()
                self.check_ult()
        else:
            # no ultimate is allowed in NPCs' turn before they take actions like enemies or Jing Yuan's Lord
            # in player players' turns, we can insert ultimate both before and after the character takes an action
            if isinstance(unit, Character):
                self.check_ult()
            action = unit.take_action(self.enemies, self.players, self.sp)
            self.run_action(action)
            self.check_extra_turn()
            self.check_ult()
        # put the unit back to the starting position
        self.distances[unit] = 10000
        self.run_commands(unit.end_turn())
        # erase blackboard
        self.blackboard = []
        if self.show_action:
            self.battle_log += "\n"

    def run_action(self, action):
        """
        Orders the unit to take the action and runs the proposed commands.

        Parameters:
        ----------
        action: tuple
            The action to be run\n
            An action is a requirement of some unit to perform an action such as basic attack on some targets.
            It is a tuple in the form (action_type: str, unit: Unit, targets: tuple).
            e.g. ("Skill", character, (enemy1, enemy2, enemy3)).
            The first one in the targets tuple is always the main target.
            The operating system orders the unit to take action on the targets and receive a batch of commands.
            The commands returned by the unit tell the system what it truly does, such as dealing dmg or healing.
            The system then executes the commands.
            (use tuples for immutability and safety).
        """
        self.blackboard.append((action, set()))
        # check for the action type and targets then order the unit to perform the action on the targets
        # the unit then returns a bunch of commands to be executed
        action_type, unit, targets = action
        if self.show_action:
            self.battle_log += unit.name + " uses " + action_type + " on " + " ".join([t.name for t in targets]) + "\n"
        done = False
        step = 0
        # types are ordered roughly from most frequent to least frequent for better efficiency
        if action_type == "Basic ATK":
            # some actions take many steps such as Welt's skill inflicting 3 hits
            # can't just merge them into one because later steps might depend on the results from the previous steps
            # so the system has to go back and forth and call the unit's method in a loop until the unit says it's done
            # pass the step count to the unit so the unit knows where they are
            while not done:
                step += 1
                commands, done = unit.basic_atk(targets, step)
                self.run_commands(commands)
        elif action_type == "Skill":
            while not done:
                step += 1
                commands, done = unit.skill(targets, step)
                self.run_commands(commands)
        elif action_type == "Ultimate":
            while not done:
                step += 1
                commands, done = unit.ultimate(targets, step)
                self.run_commands(commands)
        elif action_type == "Talent":
            while not done:
                step += 1
                commands, done = unit.talent(targets, step)
                self.run_commands(commands)
        # skips a turn (frozen, etc.)
        elif action_type == "Pass":
            pass
        # most units won't have this action
        elif action_type == "Extra Move":
            while not done:
                step += 1
                commands, done = unit.extra_move(targets, step)
                self.run_commands(commands)
        else:
            raise TypeError("unknown action type " + action_type)
        # check if anyone needs to take extra action
        # e.g.Clara's counterattack is an action ("Talent", targets)
        # recursively resolve all extra actions, because extra actions may cause more extra actions
        for time_and_unit in self.queue:
            unit = time_and_unit[1]
            if not unit.crowd_control:
                action = unit.check_extra_action(self.enemies, self.players, self.blackboard)
                if action:
                    self.run_action(action)
                    break
                    # break here because the recursion already resolves all units' extra actions

    def run_commands(self, commands):
        """
        Executes the commands proposed by the unit.

        Parameters:
        ----------
        commands: tuple
            A batch of commands where each command is a tuple in the form (command_type: str, unit: Unit, data: Any)\n
            data is a tuple or some value depending on command_type.
            A command is something that needs to be done by the operating system, such as dealing dmg, healing, etc.
        """
        for command in commands:
            command_type, unit, data = command
            # types are ordered roughly from most frequent to least frequent for better efficiency
            if command_type == "DMG":
                # DMG messages record final damage and have an additional entry indicating whether it critically hits
                message_data = []
                # a dmg command looks like ("DMG", unit, data)
                # where data is ((target1, (dmg1, break_dmg1), tags1), (target2, (dmg2, break_dmg2), tags2), ...)
                # it can apply dmg to many targets each with different dmg
                for target, dmg_and_break, tags in data:
                    # it's divided into many steps so special effects can be applied at each step
                    # calculate amended dmg with the attacker's dmg increase, crit, etc.
                    dmg_and_break = unit.amend_outgoing_dmg(dmg_and_break, target, tags, self.enemies, self.players)
                    # calculate crit dmg (expected dmg by default)
                    dmg_and_break, crit = unit.crit_dmg(dmg_and_break, target, tags, self.enemies, self.players)
                    # calculate final dmg with the target's defence, resistance, etc.
                    dmg_and_break = target.reduce_incoming_dmg(dmg_and_break, unit, tags, self.enemies, self.players)
                    # record the dmg
                    dmg, break_dmg = dmg_and_break
                    tag_str = " ".join(tags)
                    if tag_str in unit.dmg_dealt_record:
                        unit.dmg_dealt_record[tag_str] += dmg
                        unit.break_dmg_dealt_record[tag_str] += break_dmg
                    else:
                        unit.dmg_dealt_record[tag_str] = dmg
                        unit.break_dmg_dealt_record[tag_str] = break_dmg
                    message_data.append((target, dmg_and_break, tags, crit))
                    if self.show_action:
                        self.battle_log += "  " + target.name + " takes " + str(round(dmg)) + " DMG"
                    # take the dmg
                    self.run_commands(target.take_dmg(dmg_and_break, unit, tags, self.enemies, self.players))
                    if self.auto_heal_mode:
                        target.hp = target.runtime_stats["HP"]
                if self.show_action:
                    self.battle_log += "\n"
                message_data = tuple(message_data)
                message = (command_type, unit, message_data)
                self.blackboard.append(message)
                self.run_commands(unit.end_dmg(message_data, self.players, self.enemies))
            elif command_type == "Start ATK":
                self.blackboard.append((command, set()))
                self.run_commands(unit.start_atk(data, self.enemies, self.players))
            elif command_type == "End ATK":
                self.blackboard.append((command, set()))
                self.run_commands(unit.end_atk(data, self.enemies, self.players))
            elif command_type == "Lose SP":
                self.blackboard.append((command, set()))
                self.sp -= data
                if self.sp < 0:
                    raise ValueError("skill points less than 0")
            elif command_type == "Gain SP":
                original_sp = self.sp
                self.sp += data
                if self.sp > self.sp_cap:
                    self.sp = self.sp_cap
                actual_sp_gained = self.sp - original_sp
                if actual_sp_gained:
                    message = (command_type, unit, actual_sp_gained)
                    self.blackboard.append((message, set()))
            elif command_type == "Break":
                self.blackboard.append((command, set()))
                for target, dmg_type in data:
                    self.run_commands(target.weakness_break(dmg_type, unit, self.enemies, self.players))
            elif command_type == "Heal":
                # the messages record actual healing (not counting excess healing)
                message_data = []
                for target, hp, in data:
                    hp = unit.amend_outgoing_healing(hp, target, self.enemies, self.players)
                    hp = unit.amend_incoming_healing(hp, target, self.enemies, self.players)
                    hp = target.take_healing(hp, unit, self.enemies, self.players)
                    message_data.append((target, hp))
                    if self.show_action:
                        self.battle_log += "  " + target.name + " restores " + str(round(hp)) + " HP"
                if self.show_action:
                    self.battle_log += "\n"
                message_data = tuple(message_data)
                message = (command_type, unit, message_data)
                self.blackboard.append(message)
            elif command_type == "Consume HP":
                # the messages record actual consumption (can't go below 1 HP)
                message_data = []
                for target, hp, in data:
                    hp = target.consume_hp(hp, unit, self.enemies, self.players)
                    if self.auto_heal_mode:
                        target.hp = target.runtime_stats["HP"]
                    if self.show_action:
                        self.battle_log += "  " + target.name + " consumes " + str(round(hp)) + " HP"
                    message_data.append((target, hp))
                if self.show_action:
                    self.battle_log += "\n"
                message_data = tuple(message_data)
                message = (command_type, unit, message_data)
                self.blackboard.append(message)
            elif command_type == "Buff":
                self.blackboard.append((command, set()))
                for target, buff in data:
                    target.add_buff(buff)
            elif command_type == "Debuff":
                # the messages record successfully applied debuffs
                message_data = []
                for target, chance, debuff in data:
                    chance = unit.amend_outgoing_effect_chance(chance, target, self.enemies, self.players)
                    chance = target.amend_incoming_effect_chance(chance, debuff, unit, self.enemies, self.players)
                    if target.maybe_add_debuff(chance, debuff):
                        message_data.append((target, debuff))
                message_data = tuple(message_data)
                message = (command_type, unit, message_data)
                self.blackboard.append(message)
            elif command_type == "Advance":
                self.blackboard.append((command, set()))
                for target, percentage, in data:
                    self.distances[target] -= percentage * 10000
                    if self.distances[target] < 0:
                        self.distances[target] = 0
            elif command_type == "Delay":
                self.blackboard.append((command, set()))
                for target, percentage, in data:
                    self.distances[target] += percentage * 10000
            elif command_type == "Regenerate Energy":
                self.blackboard.append((command, set()))
                for target, energy, in data:
                    target.energy += energy
            else:
                raise TypeError("unknown command type " + command_type)
        # check if any character wants to run extra commands and executes them
        # e.g. Luocha's passive healing from his trace "Sanctified" is an extra command
        # recursively resolve all extra commands, because extra commands may cause more extra commands
        for time_and_unit in self.queue:
            unit = time_and_unit[1]
            commands = unit.check_extra_commands(self.enemies, self.players, self.blackboard)
            if commands:
                self.run_commands(commands)
                break
                # break here because the recursion already resolves all units' extra commands

    def check_ult(self):
        """
        Checks if any character wants to use ultimate and executes the ultimate actions.
        Keeps scanning until no one ults.
        If anyone ults, resolve any resulting extra turns.
        """
        ult_found_ever = False
        # if someone uses ultimate like Tingyun's charge, it might cause other players to want to use ultimate
        # we need to keep scanning until we can't find any ultimate
        ult_found_this_round = True
        while ult_found_this_round:
            ult_found_this_round = False
            # scan every player character
            for unit in self.players:
                # if they can and want to use ultimate, they will return an action
                action = unit.try_activate_ult(self.enemies, self.players)
                if action:
                    ult_found_ever = True
                    ult_found_this_round = True
                    # let the character use ultimate
                    self.run_action(action)
        # ultimates can cause someone to take an extra turn (like Seele's ultimate kills an enemy)
        if ult_found_ever:
            self.check_extra_turn()
            # if the extra turn enables any ultimate it will check them automatically

    def check_extra_turn(self):
        """
        Checks if any character wants to take extra turns and executes them
        """
        for time_and_unit in self.queue:
            unit = time_and_unit[1]
            action = unit.check_extra_turn(self.enemies, self.players, self.sp, self.blackboard)
            if action:
                # extra turns don't have turn start/end phases so they consume no buffs/debuffs
                unit.in_extra_turn = True
                # somehow, in Seele's extra turn, no one can use ultimate before she chooses an action
                # maybe extra turns have different priority levels
                if unit.low_extra_turn_priority:
                    self.check_ult()
                self.run_action(action)
                self.check_ult()
                unit.in_extra_turn = False
                # check if any character wants to take extra turns and executes them
                # recursively resolve all extra turns, because extra turns may cause more extra turns
                self.check_extra_turn()
                break
                # break here because the recursion already resolves all units' extra turns

    def run(self):
        while self.tic():
            pass
        if self.show_action:
            stdout.write(self.battle_log)

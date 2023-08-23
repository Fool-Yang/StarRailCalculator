from characters.character import *


class Blade(Character):

    def __init__(self):
        super(Blade, self).__init__(
            name="Blade",
            dmg_type="Wind",
            path="Destruction",
            taunt=125,
            hp=1358, atk=543,
            def_=485, spd=97,
            crit_rate=0.05 + 0.12, crit_dmg=0.5,
            break_effect=0,
            outgoing_healing_boost=0, incoming_healing_boost=0,
            max_energy=130, energy_regen=0,
            effect_hit_rate=0, effect_res=0.1,
            physical_dmg_boost=0,
            fire_dmg_boost=0,
            ice_dmg_boost=0,
            lightning_dmg_boost=0,
            wind_dmg_boost=0,
            quantum_dmg_boost=0,
            imaginary_dmg_boost=0,
            physical_res_boost=0,
            fire_res_boost=0,
            ice_res_boost=0,
            lightning_res_boost=0,
            wind_res_boost=0,
            quantum_res_boost=0,
            imaginary_res_boost=0
        )

        self.extra_stats["HP Percentage"] += 0.28
        self.stats["DMG Boost"]["Talent"] = 0.2
        self.skill_active = False
        # constant buffs (never decay) can be defined as attributes
        self.trace_buff = {
            "ID": "Vita Infinita",
            "Type": "Incoming Healing Boost",
            "DMG Type": None,
            "Value": 0.2,
            "Value Type": "Flat",
            "Source": None,
            "Source Stats": None,
            "Max Stack": 1,
            "Stack": 1,
            "Decay": None,
            "Turn": None,
            "Unlock": None,
            "Locked": True
        }
        self.need_to_take_extra_turn = False
        self.talent_stack = 0
        self.max_talent_stack = 5
        self.lost_hp = 0
        self.dmg_dealt_Record = {
            "Basic ATK Wind": 0,
            "Ultimate Wind": 0,
            "Talent Wind": 0,
        }

    def choose_action(self, enemies, players, sp):
        if self.skill_active:
            center = len(enemies) // 2
            targets = [enemies[center]]
            left = center - 1
            right = center + 1
            if left >= 0:
                targets.append(enemies[left])
            if right < len(enemies):
                targets.append(enemies[right])
            return "Basic ATK", self.decorated_self, tuple(targets)
        elif sp > 0:
            return "Skill", self.decorated_self, (self.decorated_self,)
        else:
            center = len(enemies) // 2
            targets = (enemies[center],)
            return "Basic ATK", self.decorated_self, targets

    def check_extra_turn(self, enemies, players, sp, blackboard):
        if self.need_to_take_extra_turn:
            self.need_to_take_extra_turn = False
            return self.choose_action(enemies, players, sp)

    def check_extra_action(self, enemies, players, blackboard):
        if self.talent_stack >= self.max_talent_stack:
            return "Talent", self.decorated_self, enemies

    def try_activate_ult(self, enemies, players):
        if self.energy >= self.max_energy:
            center = len(enemies) // 2
            targets = [enemies[center]]
            left = center - 1
            right = center + 1
            if left >= 0:
                targets.append(enemies[left])
            if right < len(enemies):
                targets.append(enemies[right])
            return "Ultimate", self.decorated_self, tuple(targets)

    def basic_atk(self, targets, step):
        commands = []
        atk = self.runtime_stats["ATK"]
        max_hp = self.runtime_stats["HP"]
        energy_regen = self.runtime_stats["Energy Regeneration Rate"]
        if step == 1:
            if self.skill_active:
                tags = ("Basic ATK", "Enhanced", self.dmg_type)
                self.energy += 30 * (1 + energy_regen)
                dmg_break = ((0.4 * atk + 1 * max_hp) / 2, 30)
                commands.append(("Consume HP", self.decorated_self, ((self.decorated_self, 0.1 * max_hp),)))
            else:
                tags = ("Basic ATK", self.dmg_type)
                self.energy += 20 * (1 + energy_regen)
                dmg_break = (1 * atk / 2, 30)
                commands.append(("Gain SP", self.decorated_self, 1))
            data = ((targets[0], dmg_break, tags),)
            commands.append(("Start ATK", self.decorated_self, targets))
            commands.append(("DMG", self.decorated_self, data))
            return tuple(commands), False
        else:
            if self.skill_active:
                tags = ("Basic ATK", "Enhanced", self.dmg_type)
                dmg_break1 = ((0.4 * atk + 1 * max_hp) / 2, 30)
                dmg_break2 = (0.16 * atk + 0.4 * max_hp, 30)
                data = [(targets[0], dmg_break1, tags)]
                for minor_target in targets[1:]:
                    data.append((minor_target, dmg_break2, tags))
                data = tuple(data)
            else:
                tags = ("Basic ATK", self.dmg_type)
                dmg_break = (1 * atk / 2, 30)
                data = ((targets[0], dmg_break, tags),)
            commands.append(("DMG", self.decorated_self, data))
            commands.append(("End ATK", self.decorated_self, targets))
            # restores hp if hitting a broken enemy
            # actually only need to check the second hit
            for target in targets:
                if target.toughness <= 0:
                    data = (self.decorated_self, 0.05 * self.stats["HP"] + 100)
                    commands.append(("Heal", self.decorated_self, data))
            return tuple(commands), True

    def skill(self, targets, step):
        commands = []
        if not self.skill_active:
            self.need_to_take_extra_turn = True
            self.skill_active = True
            buff = {
                "ID": "Hellscape",
                "Type": "DMG Boost",
                "DMG Type": "All",
                "Value Type": "Flat",
                "Source": None,
                "Source Stats": None,
                "Value": 0.4,
                "Max Stack": 1,
                "Stack": 1,
                "Decay": "End",
                "Turn": 3,
                "Unlock": "Action",
                "Locked": True
            }
            self.add_buff(buff)
            data = ((self.decorated_self, 0.3 * self.runtime_stats["HP"]),)
            commands.append(("Lose SP", self.decorated_self, 1))
            commands.append(("Consume HP", self.decorated_self, data))
            return tuple(commands), True
        else:
            raise RuntimeError("Blade's skill is already skill_active")

    def ultimate(self, targets, step):
        commands = []
        if step == 1:
            self.energy = 5 * (1 + self.runtime_stats["Energy Regeneration Rate"])
            half_hp = self.runtime_stats["HP"] / 2
            consume = self.hp - half_hp
            if consume > 0:
                commands.append(("Consume HP", self.decorated_self, ((self.decorated_self, consume),)))
                return tuple(commands), False
            else:
                # this is not healing
                self.hp = half_hp
        tags = ("Ultimate", self.dmg_type)
        atk = self.runtime_stats["ATK"]
        max_hp = self.runtime_stats["HP"]
        dmg_break1 = (0.4 * atk + 1 * max_hp + 1 * self.lost_hp, 60)
        dmg_break2 = (0.16 * atk + 0.4 * max_hp + 0.4 * self.lost_hp, 60)
        data = [(targets[0], dmg_break1, tags)]
        for minor_target in targets[1:]:
            data.append((minor_target, dmg_break2, tags))
        data = tuple(data)
        commands.append(("Start ATK", self.decorated_self, targets))
        commands.append(("DMG", self.decorated_self, tuple(data)))
        commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), True

    def talent(self, targets, step):
        commands = []
        self.energy += 10 * (1 + self.runtime_stats["Energy Regeneration Rate"])
        self.talent_stack = 0
        tags = ("Talent", "Follow-Up", self.dmg_type)
        dmg_break = (0.44 * self.runtime_stats["ATK"] + 1.1 * self.runtime_stats["HP"], 30)
        data = []
        for target in targets:
            data.append((target, dmg_break, tags))
        data = tuple(data)
        commands.append(("Start ATK", self.decorated_self, targets))
        commands.append(("DMG", self.decorated_self, tuple(data)))
        commands.append(("End ATK", self.decorated_self, targets))
        commands.append(("Heal", self.decorated_self, ((self.decorated_self, 0.25 * self.runtime_stats["HP"]),)))
        return tuple(commands), True

    def end_turn(self):
        result = super(Blade, self).end_turn()
        for buff in self.buffs:
            if buff["ID"] == "Hellscape":
                break
        else:
            self.skill_active = False
        return result

    def take_dmg(self, dmg_and_break, source, tags, enemies, players):
        result = super(Blade, self).take_dmg(dmg_and_break, source, tags, enemies, players)
        self.talent_stack += 1
        self.lost_hp += dmg_and_break[0]
        max_lost_hp = 0.9 * self.runtime_stats["HP"]
        if self.lost_hp > max_lost_hp:
            self.lost_hp = max_lost_hp
        if self.hp <= 0.5 * self.runtime_stats["HP"]:
            self.add_buff(self.trace_buff)
        return result

    def consume_hp(self, hp, source, enemies, players):
        hp = super(Blade, self).consume_hp(hp, source, enemies, players)
        self.talent_stack += 1
        self.lost_hp += hp
        max_lost_hp = 0.9 * self.runtime_stats["HP"]
        if self.lost_hp > max_lost_hp:
            self.lost_hp = max_lost_hp
        if self.hp <= 0.5 * self.runtime_stats["HP"]:
            self.add_buff(self.trace_buff)
        return hp

    def take_healing(self, hp, source, enemies, players):
        hp = super(Blade, self).take_healing(hp, source, enemies, players)
        if self.hp > 0.5 * self.runtime_stats["HP"] and self.trace_buff in self.buffs:
            self.dispel_buff(self.trace_buff)
        return hp

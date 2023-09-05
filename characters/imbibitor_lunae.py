from characters.character import *


class ImbibitorLunae(Character):

    def __init__(self):
        super(ImbibitorLunae, self).__init__(
            name="Imbibitor Lunae",
            dmg_type="Imaginary",
            path="Destruction",
            taunt=125,
            hp=1241, atk=698,
            def_=363, spd=102,
            crit_rate=0.05 + 0.12, crit_dmg=0.5,
            break_effect=0,
            outgoing_healing_boost=0, incoming_healing_boost=0,
            max_energy=140, energy_regen=0,
            effect_hit_rate=0, effect_res=0, crowd_control_res=0,
            physical_dmg_boost=0,
            fire_dmg_boost=0,
            ice_dmg_boost=0,
            lightning_dmg_boost=0,
            wind_dmg_boost=0,
            quantum_dmg_boost=0,
            imaginary_dmg_boost=0.224,
            physical_res_boost=0,
            fire_res_boost=0,
            ice_res_boost=0,
            lightning_res_boost=0,
            wind_res_boost=0,
            quantum_res_boost=0,
            imaginary_res_boost=0
        )

        self.energy = self.max_energy / 2 + 15
        self.extra_stats["HP Percentage"] += 0.1
        self.basic_attack_enhancement_level = 0
        self.squama_sacrosancta = 0
        self.dmg_dealt_Record = {
            "Basic ATK Imaginary": 0,
            "Ultimate Imaginary": 0
        }

    def choose_action(self, enemies, players, sp):
        resource = sp + self.squama_sacrosancta
        if resource < 3:
            self.basic_attack_enhancement_level = resource
        else:
            self.basic_attack_enhancement_level = 3
        center = len(enemies) // 2
        targets = [enemies[center]]
        left = center - 1
        right = center + 1
        if left >= 0:
            targets.append(enemies[left])
        if right < len(enemies):
            targets.append(enemies[right])
        return "Basic ATK", self.decorated_self, tuple(targets)

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
        energy_regen = self.runtime_stats["Energy Regeneration Rate"]
        tags = ("Basic ATK", self.dmg_type)
        if self.basic_attack_enhancement_level == 0:
            done = step >= 2
            if step == 1:
                commands.append(("Start ATK", self.decorated_self, targets))
                commands.append(("Gain SP", self.decorated_self, 1))
                self.energy += 20 * (1 + energy_regen)
            dmg_break = (1 * atk / 2, 30 / 2)
            data = ((targets[0], dmg_break, tags),)
            commands.append(("DMG", self.decorated_self, data))
        else:
            if step == 1:
                commands.append(("Start ATK", self.decorated_self, targets))
                sp_consumption = 0
                self.squama_sacrosancta -= self.basic_attack_enhancement_level
                if self.squama_sacrosancta < 0:
                    sp_consumption = -self.squama_sacrosancta
                    self.squama_sacrosancta = 0
                commands.append(("Lose SP", self.decorated_self, sp_consumption))
                self.energy += (25 + 5 * self.basic_attack_enhancement_level) * (1 + energy_regen)
            if self.basic_attack_enhancement_level == 1:
                done = step >= 3
                dmg_break = (2.6 * atk / 3, 60 / 3)
                data = ((targets[0], dmg_break, tags),)
                commands.append(("DMG", self.decorated_self, data))
            elif self.basic_attack_enhancement_level == 2:
                done = step >= 5
                dmg_break1 = (3.8 * atk / 5, 90 / 5)
                data = [(targets[0], dmg_break1, tags)]
                if step >= 4:
                    self.skill(targets, step)
                    dmg_break2 = (0.6 * atk / 2, 30 / 2)
                    for minor_target in targets[1:]:
                        data.append((minor_target, dmg_break2, tags))
                data = tuple(data)
                commands.append(("DMG", self.decorated_self, data))
            else:  # self.basic_attack_enhancement_level == 3:
                done = step >= 7
                dmg_break1 = (5 * atk / 7, 120 / 7)
                data = [(targets[0], dmg_break1, tags)]
                if step >= 4:
                    self.skill(targets, step)
                    dmg_break2 = (1.8 * atk / 4, 60 / 4)
                    for minor_target in targets[1:]:
                        data.append((minor_target, dmg_break2, tags))
                data = tuple(data)
                commands.append(("DMG", self.decorated_self, data))
        if done:
            commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), done

    def skill(self, targets, step):
        # Imbibitor doesn't really have a skill that count as an action
        # this is only for internal usage for adding buffs
        if step >= 4:
            skill_buff = {
                "ID": "Outroar",
                "Type": "CRIT DMG",
                "DMG Type": None,
                "Value": 0.12,
                "Value Type": "Flat",
                "Source": None,
                "Source Stats": None,
                "Max Stack": 4,
                "Stack": 1,
                "Decay": "End",
                "Turn": 1,
                "Unlock": "End",
                "Locked": True
            }
            self.add_buff(skill_buff)

    def ultimate(self, targets, step):
        commands = []
        done = step >= 3
        if step == 1:
            commands.append(("Start ATK", self.decorated_self, targets))
            self.energy = 5 * (1 + self.runtime_stats["Energy Regeneration Rate"])
            self.squama_sacrosancta += 2
            if self.squama_sacrosancta > 3:
                self.squama_sacrosancta = 3
        tags = ("Ultimate", self.dmg_type)
        atk = self.runtime_stats["ATK"]
        dmg_break1 = (3 * atk / 3, 60 / 3)
        dmg_break2 = (1.4 * atk / 3, 60 / 3)
        data = [(targets[0], dmg_break1, tags)]
        for minor_target in targets[1:]:
            data.append((minor_target, dmg_break2, tags))
        data = tuple(data)
        commands.append(("DMG", self.decorated_self, tuple(data)))
        if done:
            commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), done

    def talent(self, targets, step):
        # Imbibitor doesn't really have a talent that count as an action
        # it triggers after each hit
        return tuple()

    def end_dmg(self, data, enemies, players):
        talent_buff = {
            "ID": "Righteous Heart",
            "Type": "DMG Boost",
            "DMG Type": "All",
            "Value": 0.1,
            "Value Type": "Flat",
            "Source": None,
            "Source Stats": None,
            "Max Stack": 6,
            "Stack": 1,
            "Decay": "End",
            "Turn": 1,
            "Unlock": "End",
            "Locked": True
        }
        self.add_buff(talent_buff)
        return tuple()

    def crit_dmg(self, dmg_and_break, target, tags, enemies, players, expected=True):
        activate = "Imaginary" in target.weaknesses
        if activate:
            self.runtime_stats["CRIT DMG"] += 0.24
        result = super(ImbibitorLunae, self).crit_dmg(dmg_and_break, target, tags, enemies, players, expected)
        if activate:
            self.runtime_stats["CRIT DMG"] -= 0.24
        return result

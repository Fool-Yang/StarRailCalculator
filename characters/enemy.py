from characters.unit import *

WEAKNESS_BREAK_DOT_NAMES = {
    "Physical": "Bleed",
    "Fire": "Burn",
    "Lightning": "Shock",
    "Wind": "Wind Shear"
}
WEAKNESS_BREAK_DEBUFF_NAMES = {
    "Ice": "Freeze",
    "Quantum": "Entanglement",
    "Imaginary": "Imprisonment"
}


def choose_target(players):
    """
    Randomly choose a player character based on their Taunt stats

    Parameters:
    ----------
    players: tuple
        The tuple of player units

    Returns:
    -------
    The selected target
    """
    for char in players:
        char.refresh_runtime_stats()
    taunts = [char.runtime_stats["Taunt"] for char in players]
    sigma = sum(taunts)
    for i in range(len(taunts)):
        taunts[i] /= sigma
    rand = random()
    cdf = 0
    target = None
    for i in range(len(taunts)):
        cdf += taunts[i]
        if rand <= cdf:
            target = players[i]
            break
    return target


class Enemy(Unit):

    def __init__(
            self, name,
            dmg_type="Physical",
            hp=20000, atk=1000,
            def_=1100, spd=100,
            effect_hit_rate=0, effect_res=0,
            physical_res_boost=0.2,
            fire_res_boost=0.2,
            ice_res_boost=0.2,
            lightning_res_boost=0.2,
            wind_res_boost=0.2,
            quantum_res_boost=0.2,
            imaginary_res_boost=0.2,
            weaknesses=set(),
            max_toughness=60
    ):

        super(Enemy, self).__init__(
            name=name,
            dmg_type=dmg_type,
            path=None,
            taunt=100,
            hp=hp, atk=atk,
            def_=def_, spd=spd,
            crit_rate=0, crit_dmg=0,
            break_effect=0,
            outgoing_healing_boost=0, incoming_healing_boost=0,
            max_energy=0, energy_regen=0,
            effect_hit_rate=effect_hit_rate, effect_res=effect_res, crowd_control_res=0,
            physical_dmg_boost=0,
            fire_dmg_boost=0,
            ice_dmg_boost=0,
            lightning_dmg_boost=0,
            wind_dmg_boost=0,
            quantum_dmg_boost=0,
            imaginary_dmg_boost=0,
            physical_res_boost=physical_res_boost,
            fire_res_boost=fire_res_boost,
            ice_res_boost=ice_res_boost,
            lightning_res_boost=lightning_res_boost,
            wind_res_boost=wind_res_boost,
            quantum_res_boost=quantum_res_boost,
            imaginary_res_boost=imaginary_res_boost
        )

        self.level = 90
        self.weaknesses = weaknesses
        for dmg_type in weaknesses:
            self.stats["RES Boost"][dmg_type] = 0
        self.decorated_self.refresh_runtime_stats()
        self.max_toughness = max_toughness
        self.toughness = max_toughness
        # define weakness break damage
        weakness_beak_dmg_level_multiplier = 3767.5533
        weakness_beak_dmg_toughness_multiplier = 0.5 + self.max_toughness / 120
        base_dmg_multiplier = weakness_beak_dmg_level_multiplier * weakness_beak_dmg_toughness_multiplier
        self.weakness_beak_base_dmg = {
            "Physical": 2 * base_dmg_multiplier,
            "Fire": 2 * base_dmg_multiplier,
            "Ice": 1 * base_dmg_multiplier,
            "Lightning": 1 * base_dmg_multiplier,
            "Wind": 1.5 * base_dmg_multiplier,
            "Quantum": 0.5 * base_dmg_multiplier,
            "Imaginary": 0.5 * base_dmg_multiplier
        }
        self.weakness_beak_debuff_dmg = {
            "Physical": (0.07 if isinstance(self, Boss) else 0.16) * self.runtime_stats["HP"],
            "Fire": 1 * weakness_beak_dmg_level_multiplier,
            "Ice": 1 * weakness_beak_dmg_level_multiplier,
            "Lightning": 2 * weakness_beak_dmg_level_multiplier,
            "Wind": 1 * weakness_beak_dmg_level_multiplier,
            "Quantum": 0.6 * base_dmg_multiplier,
            "Imaginary": 0
        }
        bleed_dmg_cap = 2 * base_dmg_multiplier
        if self.weakness_beak_debuff_dmg["Physical"] > bleed_dmg_cap:
            self.weakness_beak_debuff_dmg["Physical"] = bleed_dmg_cap

    def choose_action(self, enemies, players, sp):
        target = choose_target(players)
        return "Basic ATK", self.decorated_self, (target,)

    def weakness_break(self, dmg_type, source, enemies, players):
        """
        Suffers weakness break and returns the DMG and Debuff commands.

        Parameters:
        ----------
        dmg_type: str
            The damage type
        source: Unit
            The source unit of the break
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        A tuple of commands
        """
        commands = []
        # weakness break base damage
        dmg = self.weakness_beak_base_dmg[dmg_type]
        tags = ("Break", dmg_type)
        data = ((self.decorated_self, (dmg, 0), tags),)
        commands.append(("DMG", source, data))
        dmg = self.weakness_beak_debuff_dmg[dmg_type]
        if dmg_type in WEAKNESS_BREAK_DOT_NAMES:
            # weakness break action delay
            data = ((self.decorated_self, 0.25),)
            commands.append(("Delay", source, data))
            # weakness break debuff
            debuff_id = WEAKNESS_BREAK_DOT_NAMES[dmg_type]
            if dmg_type == "Wind":
                max_stack = 5
                if isinstance(self, Boss):
                    stack = 3
                else:
                    stack = 1
            else:
                max_stack = 1
                stack = 1
            debuff = {
                "ID": debuff_id,
                "Type": "DoT",
                "DMG Type": dmg_type,
                "Value Type": "Flat",
                "Value": dmg,
                "Source": source,
                "Source Stats": None,
                "Max Stack": max_stack,
                "Stack": stack,
                "Decay": "Start",
                "Turn": 2,
                "Unlock": "Start",
                "Locked": True
            }
        else:
            # weakness break action delay and debuff
            debuff_id = WEAKNESS_BREAK_DEBUFF_NAMES[dmg_type]
            if dmg_type == "Quantum":
                value = dmg
                max_stack = 5
                data = ((self.decorated_self, 0.25 + 0.2),)
            elif dmg_type == "Imaginary":
                # Imprisonment doesn't deal additional damage, but applies SPD reduction
                dmg_type = None
                value = 0.1 * self.stats["SPD"]
                max_stack = 1
                data = ((self.decorated_self, 0.25 + 0.3),)
            else:
                value = dmg
                max_stack = 1
                data = ((self.decorated_self, 0.25),)
            commands.append(("Delay", source, data))
            debuff = {
                "ID": debuff_id,
                "Type": "Crowd Control",
                "DMG Type": dmg_type,
                "Value Type": "Flat",
                "Value": value,
                "Source": source,
                "Source Stats": None,
                "Max Stack": max_stack,
                "Stack": 1,
                "Decay": "Start",
                "Turn": 1,
                "Unlock": "Start",
                "Locked": True
            }
        data = ((self.decorated_self, 1.5, debuff),)
        commands.append(("Debuff", source, data))
        return tuple(commands)

    def basic_atk(self, targets, step):
        commands = []
        dmg = 1 * self.runtime_stats["ATK"]
        tags = ("Basic ATK", self.dmg_type)
        data = ((targets[0], (dmg, 0), tags),)
        commands.append(("Start ATK", self.decorated_self, targets))
        commands.append(("DMG", self.decorated_self, data))
        commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), True


class Boss(Enemy):

    def __init__(self, *args, max_toughness=450, multiple_turns=2, **kwargs):
        super(Boss, self).__init__(*args, **kwargs, max_toughness=max_toughness)
        self.multiple_turns = multiple_turns
        self.turns_left = multiple_turns
        self.used_skill = False

    def choose_action(self, enemies, players, sp):
        # this basic boss's behaviour alternates between (Basic ATK, Basic ATK) and (Basic ATK, Skill)
        self.turns_left -= 1
        if self.turns_left == 1:
            return super(Boss, self).choose_action(enemies, players, sp)
        else:
            if self.used_skill:
                self.used_skill = False
                return super(Boss, self).choose_action(enemies, players, sp)
            else:
                self.used_skill = True
                return "Skill", self.decorated_self, tuple(players)

    def skill(self, targets, step):
        commands = []
        data = []
        for target in targets:
            dmg = 0.5 * self.runtime_stats["ATK"]
            tags = ("Skill", self.dmg_type)
            data.append((target, (dmg, 0), tags))
        data = tuple(data)
        commands.append(("Start ATK", self.decorated_self, targets))
        commands.append(("DMG", self.decorated_self, data))
        commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), True

    def end_turn(self):
        self.turns_left = self.multiple_turns
        return super(Boss, self).end_turn()

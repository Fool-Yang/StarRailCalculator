from characters.unit import *


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

    def choose_action(self, enemies, players, sp):
        target = choose_target(players)
        return "Basic ATK", self.decorated_self, (target,)

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

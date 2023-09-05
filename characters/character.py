from characters.unit import *


class Character(Unit):

    def __init__(self, *args, **kwargs):
        # these extra stats might come from the character's traces, relics or light cones
        # because these stats has a so-called "base value", they need to be separated from the base stats
        # if the stats from traces have no "base value" (e.g. crit rate), just add them to the base stats (self.stats)
        self.extra_stats = {
            "HP": 0,
            "HP Percentage": 0,
            "ATK": 0,
            "ATK Percentage": 0,
            "DEF": 0,
            "DEF Percentage": 0,
            "SPD": 0,
            "SPD Percentage": 0
        }
        super(Character, self).__init__(*args, **kwargs)

    def refresh_runtime_stats(self):
        super(Character, self).refresh_runtime_stats()
        self.runtime_stats["HP"] += self.extra_stats["HP"] + self.extra_stats["HP Percentage"] * self.stats["HP"]
        self.runtime_stats["ATK"] += self.extra_stats["ATK"] + self.extra_stats["ATK Percentage"] * self.stats["ATK"]
        self.runtime_stats["DEF"] += self.extra_stats["DEF"] + self.extra_stats["DEF Percentage"] * self.stats["DEF"]
        self.runtime_stats["SPD"] += self.extra_stats["SPD"] + self.extra_stats["SPD Percentage"] * self.stats["SPD"]

    @abstractmethod
    def try_activate_ult(self, enemies, players):
        """
        Checks if the unit can and will activate ultimate.

        Parameters:
        ----------
        enemies: tuple
            The tuple of enemy units
        players: tuple
            The tuple of player units

        Returns:
        -------
        Either None or ("Ult", targets)
        """
        pass

    @abstractmethod
    def basic_atk(self, targets, step):
        """
        Defines the unit's Basic ATK.

        Parameters:
        ----------
        targets: tuple
            The tuple of target units
        step: int
            The step of the Basic ATK\n
            Some Skills are divided into many steps such as Welt's skill inflicting 3 hits. The later results might
            depend on the previous ones, and effects may trigger in between. The commands has to be sent to the
            operating system in many steps. Usually one hit needs one step. The operating system will repeatedly call
            this method until it returns True for done.

        Returns:
        -------
        A tuple of commands and a bool indicating whether the process is done
        """
        pass

    @abstractmethod
    def skill(self, targets, step):
        """
        Defines the unit's Skill. See basic_atk(.) for more info.
        """
        pass

    @abstractmethod
    def ultimate(self, targets, step):
        """
        Defines the unit's Ultimate. See basic_atk(.) for more info.
        """
        pass

    @abstractmethod
    def talent(self, targets, step):
        """
        Defines the unit's Talent. See basic_atk(.) for more info.
        """
        pass


class Dummy(Character):

    def __init__(self, name):
        super(Dummy, self).__init__(
            name=name,
            dmg_type="Physical",
            path="Nihility",
            taunt=100,
            hp=3000, atk=2000,
            def_=1000, spd=100,
            crit_rate=0.05, crit_dmg=0.5,
            break_effect=0,
            outgoing_healing_boost=0, incoming_healing_boost=0,
            max_energy=100, energy_regen=0,
            effect_hit_rate=0, effect_res=0, crowd_control_res=0,
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

    def choose_action(self, enemies, players, sp):
        for enemy in enemies:
            enemy.refresh_runtime_stats()
        taunts = [enemy.runtime_stats["Taunt"] for enemy in enemies]
        sigma = sum(taunts)
        for i in range(len(taunts)):
            taunts[i] /= sigma
        rand = random()
        cdf = 0
        target = None
        for i in range(len(taunts)):
            cdf += taunts[i]
            if rand <= cdf:
                target = enemies[i]
                break
        return "Basic ATK", self.decorated_self, (target,)

    def try_activate_ult(self, enemies, players):
        return

    def basic_atk(self, targets, step):
        commands = []
        dmg = 1 * self.runtime_stats["ATK"]
        break_dmg = 30
        tags = ("Basic ATK", self.dmg_type)
        data = ((targets[0], (dmg, break_dmg), tags),)
        commands.append(("Start ATK", self.decorated_self, targets))
        commands.append(("Gain SP", self.decorated_self, 1))
        commands.append(("DMG", self.decorated_self, data))
        commands.append(("End ATK", self.decorated_self, targets))
        return tuple(commands), True

    def skill(self, targets, step):
        return

    def ultimate(self, targets, step):
        return

    def talent(self, targets, step):
        return

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import math


class Ability(str, Enum):
    STR = "Force"
    DEX = "Dextérité"
    CON = "Constitution"
    INT = "Intelligence"
    WIS = "Sagesse"
    CHA = "Charisme"


class ArmorType(str, Enum):
    LIGHT = "Légère"
    MEDIUM = "Intermédiaire"
    HEAVY = "Lourde"
    SHIELD = "Bouclier"
    NONE = "Aucune"


SKILL_ABILITY_MAP = {
    "Acrobaties": Ability.DEX,
    "Arcanes": Ability.INT,
    "Athlétisme": Ability.STR,
    "Discrétion": Ability.DEX,
    "Dressage": Ability.WIS,
    "Escamotage": Ability.DEX,
    "Histoire": Ability.INT,
    "Intimidation": Ability.CHA,
    "Intuition": Ability.WIS,
    "Investigation": Ability.INT,
    "Médecine": Ability.WIS,
    "Nature": Ability.INT,
    "Perception": Ability.WIS,
    "Persuasion": Ability.CHA,
    "Religion": Ability.INT,
    "Représentation": Ability.CHA,
    "Survie": Ability.WIS,
    "Tromperie": Ability.CHA,
}


@dataclass
class Item:
    name: str
    weight: float = 0.0
    quantity: int = 1
    description: str = ""
    is_custom: bool = False


@dataclass
class Armor(Item):
    armor_type: ArmorType = ArmorType.LIGHT
    base_ac: int = 11
    max_dex_bonus: Optional[int] = None
    magic_bonus: int = 0


@dataclass
class Weapon(Item):
    damage_dice: str = "1d6"
    damage_type: str = "tranchant"
    is_finesse: bool = False
    is_ranged: bool = False
    magic_bonus: int = 0
    attack_bonus_override: Optional[int] = None
    extra_damage_desc: str = ""


@dataclass
class Spell:
    name: str
    level: int
    school: str = "Évocation"
    casting_time: str = "1 action"
    range_area: str = "18m"
    components: str = "V, S"
    duration: str = "Instantanée"
    concentration: bool = False


@dataclass
class CharacterSheet:
    name: str
    race: str
    background: str
    alignment: str
    
    # Caractéristiques de base (stats brutes)
    raw_abilities: Dict[Ability, int]
    
    # Multiclassage : {"Rôdeur": 5, "Roublard": 2}
    classes: Dict[str, int] = field(default_factory=dict)
    
    # Maîtrises
    saving_throw_proficiencies: List[Ability] = field(default_factory=list)
    skill_proficiencies: List[str] = field(default_factory=list)
    skill_expertises: List[str] = field(default_factory=list)  # Ex: Roublard (x2 maîtrise)
    
    # Équipement & Armes
    equipped_armor: Optional[Armor] = None
    equipped_shield: Optional[Armor] = None
    weapons: List[Weapon] = field(default_factory=list)
    inventory: List[Item] = field(default_factory=list)
    
    # Sorts & Traits
    known_spells: List[Spell] = field(default_factory=list)
    traits_and_features: List[str] = field(default_factory=list)

    # ------------------ CALCULS DYNAMIQUES ------------------

    @property
    def total_level(self) -> int:
        return sum(self.classes.values())

    @property
    def proficiency_bonus(self) -> int:
        """Bonus de maîtrise officiel D&D 5e 2014."""
        return math.floor((self.total_level - 1) / 4) + 2

    def get_ability_modifier(self, ability: Ability) -> int:
        """Modificateur de carac : floor((score - 10) / 2)"""
        score = self.raw_abilities.get(ability, 10)
        return math.floor((score - 10) / 2)

    def get_saving_throw(self, ability: Ability) -> int:
        mod = self.get_ability_modifier(ability)
        if ability in self.saving_throw_proficiencies:
            mod += self.proficiency_bonus
        return mod

    def get_skill_modifier(self, skill_name: str) -> int:
        ability = SKILL_ABILITY_MAP.get(skill_name)
        if not ability:
            return 0
        mod = self.get_ability_modifier(ability)
        
        if skill_name in self.skill_expertises:
            mod += self.proficiency_bonus * 2
        elif skill_name in self.skill_proficiencies:
            mod += self.proficiency_bonus
        return mod

    @property
    def passive_perception(self) -> int:
        return 10 + self.get_skill_modifier("Perception")

    @property
    def armor_class(self) -> int:
        """Calcul dynamique de la CA selon armure, dex et bouclier."""
        dex_mod = self.get_ability_modifier(Ability.DEX)
        
        if not self.equipped_armor or self.equipped_armor.armor_type == ArmorType.NONE:
            ac = 10 + dex_mod
        elif self.equipped_armor.armor_type == ArmorType.LIGHT:
            ac = self.equipped_armor.base_ac + dex_mod + self.equipped_armor.magic_bonus
        elif self.equipped_armor.armor_type == ArmorType.MEDIUM:
            allowed_dex = min(dex_mod, 2) if self.equipped_armor.max_dex_bonus is None else min(dex_mod, self.equipped_armor.max_dex_bonus)
            ac = self.equipped_armor.base_ac + allowed_dex + self.equipped_armor.magic_bonus
        elif self.equipped_armor.armor_type == ArmorType.HEAVY:
            ac = self.equipped_armor.base_ac + self.equipped_armor.magic_bonus
        else:
            ac = 10 + dex_mod

        if self.equipped_shield and self.equipped_shield.armor_type == ArmorType.SHIELD:
            ac += self.equipped_shield.base_ac + self.equipped_shield.magic_bonus
            
        return ac

    def calculate_weapon_attack(self, weapon: Weapon) -> tuple[int, str]:
        """
        Calcule (Bonus d'attaque, Formule de dégâts).
        Prend automatiquement le meilleur modificateur si Finesse.
        """
        dex_mod = self.get_ability_modifier(Ability.DEX)
        str_mod = self.get_ability_modifier(Ability.STR)
        
        if weapon.is_ranged:
            stat_mod = dex_mod
        elif weapon.is_finesse:
            stat_mod = max(dex_mod, str_mod)
        else:
            stat_mod = str_mod

        # Bonus d'attaque = ModStat + Maîtrise + Magie
        attack_bonus = stat_mod + self.proficiency_bonus + weapon.magic_bonus
        if weapon.attack_bonus_override is not None:
            attack_bonus += weapon.attack_bonus_override

        # Dégâts = Dé + ModStat + Magie
        damage_bonus = stat_mod + weapon.magic_bonus
        sign = f"+{damage_bonus}" if damage_bonus >= 0 else f"{damage_bonus}"
        dmg_formula = f"{weapon.damage_dice}{sign} {weapon.damage_type}"
        
        if weapon.extra_damage_desc:
            dmg_formula += f" ({weapon.extra_damage_desc})"

        return attack_bonus, dmg_formula

    def get_spell_slots(self) -> Dict[int, int]:
        """
        Calcul multiclasse selon PHB 2014 :
        Rôdeur (1/2 caster) = niveau // 2
        Roublard = 0 (sauf si Mystificateur Arcanique / Arcane Trickster : 1/3)
        """
        caster_level = self.classes.get("Rôdeur", 0) // 2
        # Table simplifiée des demi-lanceurs de niveau 1 à 5
        slot_table = {
            1: {1: 2},
            2: {1: 2},
            3: {1: 3},
            4: {1: 3},
            5: {1: 4, 2: 2},
            6: {1: 4, 2: 2},
            7: {1: 4, 2: 3},
        }
        return slot_table.get(caster_level, {1: 0, 2: 0})


# ------------------ INITIALISATION AVEC HYTHUS ------------------

def init_hythus() -> CharacterSheet:
    hythus = CharacterSheet(
        name="Hythus Feuille d'Argent",
        race="Haut elfe",
        background="Grand Voyageur",
        alignment="Chaotique Neutre",
        raw_abilities={
            Ability.STR: 15,
            Ability.DEX: 17,  # Inclut le bonus du tatouage de préhension (+1)
            Ability.CON: 12,
            Ability.INT: 14,
            Ability.WIS: 18,
            Ability.CHA: 11,
        },
        classes={"Rôdeur": 5, "Roublard": 2},
        saving_throw_proficiencies=[Ability.STR, Ability.DEX],
        skill_proficiencies=[
            "Acrobaties",
            "Athlétisme",
            "Discrétion",
            "Histoire",
            "Intuition",
            "Investigation",
            "Nature",
            "Perception",
            "Survie",
        ],
        skill_expertises=["Discrétion", "Perception"],  # Exemples d'expertises
        traits_and_features=[
            "Ennemi Juré: Fiélon",
            "Vigilance primitive",
            "Sens du chasseur",
            "Proie du tueur (1d6)",
            "Attaque Sournoise (1d6)",
            "Ruse (Action bonus: Se désengager, Se cacher, Foncer)",
            "Transe & Ascendance féérique",
            "Vision dans le noir (18m)",
        ]
    )

    # Armure : Cuir clouté (12 + Dex)
    hythus.equipped_armor = Armor(
        name="Armure de cuir clouté",
        armor_type=ArmorType.LIGHT,
        base_ac=12,
        magic_bonus=0,
    )

    # Armes
    hythus.weapons.extend([
        Weapon(name="Arc long +1", damage_dice="1d8", damage_type="perforant", is_ranged=True, magic_bonus=1),
        Weapon(name="Cimeterre", damage_dice="1d6", damage_type="tranchant", is_finesse=True),
        Weapon(name="Coutille vicieuse", damage_dice="1d10", damage_type="tranchant", is_finesse=False, extra_damage_desc="+7 dégâts si critique"),
    ])

    # Sorts
    hythus.known_spells.extend([
        Spell(name="Marque du Chasseur", level=1, casting_time="1 action bonus", duration="1 heure", concentration=True),
        Spell(name="Baie nourricière", level=1, casting_time="1 action", duration="24 heures"),
        Spell(name="Grêle d'Épines", level=1, casting_time="1 action bonus", concentration=True),
        Spell(name="Esprit Guérisseur", level=2, casting_time="1 action bonus", concentration=True),
        Spell(name="Zone de vérité", level=2, casting_time="1 action"),
    ])

    return hythus


if __name__ == "__main__":
    char = init_hythus()
    print(f"=== {char.name} ===")
    print(f"Niveau total: {char.total_level} (Bonus Maîtrise: +{char.proficiency_bonus})")
    print(f"Classe d'Armure (CA): {char.armor_class}")
    print(f"Perception Passive: {char.passive_perception}")
    print("\n--- Jets de Sauvegarde ---")
    for ab in Ability:
        val = char.get_saving_throw(ab)
        print(f"{ab.value:12}: {'+' if val >= 0 else ''}{val}")

    print("\n--- Attaques & Armes ---")
    for w in char.weapons:
        att, dmg = char.calculate_weapon_attack(w)
        print(f"{w.name:18} | Attaque: +{att} | Dégâts: {dmg}")

    print("\n--- Test Passage au Niveau Supérieur ---")
    # Simulation passage niveau 8 (ex: Rôdeur 5 -> 6, ou Roublard 2 -> 3)
    char.classes["Rôdeur"] = 6
    print(f"Après montée au niveau total {char.total_level}:")
    print(f"Nouveau bonus de maîtrise: +{char.proficiency_bonus}")
    for w in char.weapons:
        att, dmg = char.calculate_weapon_attack(w)
        print(f"{w.name:18} | Nouvelle Attaque: +{att}")
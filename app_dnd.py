"""
Application Web D&D 5e - Fiche de Personnage Interactive & Grimoire de Maître
=============================================================================
Auteur : Hythus / Antigravity
Framework : Streamlit (Python 3.13)
Style : Parchemin médiéval fantastique, ornementations dorées, adaptabilité dynamique par classe.

Fonctionnalités majeures :
- Gestion complète des 13 classes officielles françaises (dont Occultiste, Artificier...)
- Sous-classes avec extensions (PHB, Xanathar, Tasha, Wildemount...)
- Aptitudes de classe interactives & cliquables avec descriptif complet officiel
- Gestion fine des points de vie (PV actuels, PV max, PV temporaires avec absorption)
- Jets de sauvegarde contre la mort (Death Saves) interactifs
- Repos Long (remise à zéro des PV, emplacements de sorts, moitié des dés de vie)
- Repos Court (dépense de dés de vie avec jet + CON, recharge Magie de Pacte / capacités)
- Suivi dynamique des emplacements de sorts consommés / disponibles
- Compendium / Base de données intégrée pour armes, armures, sorts et aptitudes
- Import PDF intelligent (AcroForm + analyse heuristique) & Import/Export JSON
"""

import streamlit as st
import pandas as pd
import random
import json
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

import importlib
import dnd_database as db
importlib.reload(db)
import dnd_importer
importlib.reload(dnd_importer)
from dnd_importer import parse_pdf_character, parse_json_character

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Chronique du Héros - Fiche D&D 5e",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. MODÈLES DE DONNÉES & RÈGLES OFFICIELLES D&D 5e
# ==============================================================================

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
class Weapon:
    name: str
    damage_dice: str
    damage_type: str
    is_finesse: bool = False
    is_ranged: bool = False
    magic_bonus: int = 0
    attack_bonus_override: Optional[int] = None
    extra_damage_desc: str = ""

@dataclass
class Armor:
    name: str
    armor_type: ArmorType
    base_ac: int
    max_dex_bonus: Optional[int] = None
    magic_bonus: int = 0

@dataclass
class Spell:
    name: str
    level: int
    school: str = "Évocation"
    casting_time: str = "1 action"
    range_area: str = "18 m"
    duration: str = "Instantanée"
    concentration: bool = False
    description: str = ""

@dataclass
class Item:
    name: str
    quantity: int = 1
    category: str = "Aventurier"
    weight: float = 0.0
    description: str = ""
    is_equipped: bool = False

@dataclass
class CharacterSheet:
    name: str
    race: str
    background: str
    alignment: str
    raw_abilities: Dict[Ability, int]
    classes: Dict[str, int] = field(default_factory=dict)
    subclasses: Dict[str, str] = field(default_factory=dict)
    saving_throw_proficiencies: List[Ability] = field(default_factory=list)
    skill_proficiencies: List[str] = field(default_factory=list)
    skill_expertises: List[str] = field(default_factory=list)
    equipped_armor: Optional[Armor] = None
    equipped_shield: Optional[Armor] = None
    weapons: List[Weapon] = field(default_factory=list)
    known_spells: List[Spell] = field(default_factory=list)
    traits_and_features: List[str] = field(default_factory=list)
    
    # Points de vie & survie
    pv_max: int = 52
    pv_current: int = 52
    pv_temp: int = 0
    exhaustion: int = 0
    speed: int = 9
    player_name: str = ""
    xp: int = 0
    
    # Bourse et Inventaire
    currency: Dict[str, int] = field(default_factory=lambda: {"po": 0, "pa": 0, "pc": 0, "pe": 0, "pp": 0})
    inventory: List[Item] = field(default_factory=list)
    
    # Profil, Roleplay, Apparence & Histoire (Pages 1 & 2 du PDF)
    languages_and_proficiencies: str = ""
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""
    age: str = ""
    height: str = ""
    weight: str = ""
    eyes: str = ""
    skin: str = ""
    hair: str = ""
    appearance: str = ""
    allies: str = ""
    backstory: str = ""
    treasure_notes: str = ""
    additional_features_notes: str = ""

    # Gestion des ressources (Consommables)
    death_saves: Dict[str, int] = field(default_factory=lambda: {"successes": 0, "failures": 0})
    spell_slots_used: Dict[int, int] = field(default_factory=dict)
    pact_slots_used: int = 0
    hit_dice_used: Dict[str, int] = field(default_factory=dict)

    @property
    def total_inventory_weight(self) -> float:
        """Poids total de l'équipement dans l'inventaire en kg."""
        return round(sum(item.weight * item.quantity for item in self.inventory), 1)

    @property
    def total_currency_po(self) -> float:
        """Valeur totale estimée de la bourse convertie en Pièces d'Or (PO)."""
        return db.calculate_currency_total_po(self.currency)

    @property
    def total_level(self) -> int:
        return sum(self.classes.values()) if self.classes else 1

    @property
    def proficiency_bonus(self) -> int:
        return math.floor((self.total_level - 1) / 4) + 2

    def get_ability_score(self, ability: Ability) -> int:
        if ability in self.raw_abilities:
            return self.raw_abilities[ability]
        for k, v in self.raw_abilities.items():
            k_name = k.name if hasattr(k, "name") else str(k)
            if k_name == ability.name or str(k) == ability.value:
                return v
        return 10

    def get_ability_modifier(self, ability: Ability) -> int:
        score = self.get_ability_score(ability)
        return math.floor((score - 10) / 2)

    def get_saving_throw(self, ability: Ability) -> int:
        mod = self.get_ability_modifier(ability)
        is_prof = any(
            (p == ability or (hasattr(p, "name") and p.name == ability.name))
            for p in self.saving_throw_proficiencies
        )
        if is_prof:
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
        dex_mod = self.get_ability_modifier(Ability.DEX)
        str_mod = self.get_ability_modifier(Ability.STR)
        if weapon.is_ranged:
            stat_mod = dex_mod
        elif weapon.is_finesse:
            stat_mod = max(dex_mod, str_mod)
        else:
            stat_mod = str_mod

        attack_bonus = stat_mod + self.proficiency_bonus + weapon.magic_bonus
        if weapon.attack_bonus_override is not None:
            attack_bonus += weapon.attack_bonus_override

        damage_bonus = stat_mod + weapon.magic_bonus
        sign = f"+{damage_bonus}" if damage_bonus >= 0 else f"{damage_bonus}"
        dmg_formula = f"{weapon.damage_dice}{sign} {weapon.damage_type}"
        if weapon.extra_damage_desc:
            dmg_formula += f" ({weapon.extra_damage_desc})"
        return attack_bonus, dmg_formula

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la fiche complète en dictionnaire sérialisable JSON."""
        return {
            "name": self.name,
            "player_name": self.player_name,
            "xp": self.xp,
            "race": self.race,
            "background": self.background,
            "alignment": self.alignment,
            "raw_abilities": {ab.name: val for ab, val in self.raw_abilities.items()},
            "classes": self.classes,
            "subclasses": self.subclasses,
            "saving_throw_proficiencies": [ab.name for ab in self.saving_throw_proficiencies],
            "skill_proficiencies": self.skill_proficiencies,
            "skill_expertises": self.skill_expertises,
            "pv_max": self.pv_max,
            "pv_current": self.pv_current,
            "pv_temp": self.pv_temp,
            "exhaustion": self.exhaustion,
            "speed": self.speed,
            "death_saves": self.death_saves,
            "spell_slots_used": {str(k): v for k, v in self.spell_slots_used.items()},
            "pact_slots_used": self.pact_slots_used,
            "hit_dice_used": self.hit_dice_used,
            "traits_and_features": self.traits_and_features,
            "equipped_armor": {
                "name": self.equipped_armor.name,
                "armor_type": self.equipped_armor.armor_type.value,
                "base_ac": self.equipped_armor.base_ac,
                "magic_bonus": self.equipped_armor.magic_bonus,
            } if self.equipped_armor else None,
            "equipped_shield": {
                "name": self.equipped_shield.name,
                "base_ac": self.equipped_shield.base_ac,
            } if self.equipped_shield else None,
            "weapons": [asdict(w) for w in self.weapons],
            "known_spells": [asdict(s) for s in self.known_spells],
            "currency": self.currency,
            "inventory": [asdict(i) for i in self.inventory],
            "languages_and_proficiencies": self.languages_and_proficiencies,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "eyes": self.eyes,
            "skin": self.skin,
            "hair": self.hair,
            "appearance": self.appearance,
            "allies": self.allies,
            "backstory": self.backstory,
            "treasure_notes": self.treasure_notes,
            "additional_features_notes": self.additional_features_notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterSheet":
        """Reconstruit un objet CharacterSheet à partir d'un dictionnaire sérialisé."""
        abilities = {}
        for k, v in data.get("raw_abilities", {}).items():
            try:
                abilities[Ability[k]] = int(v)
            except KeyError:
                pass
        for ab in Ability:
            if ab not in abilities:
                abilities[ab] = 10

        saving_throws = []
        for ab_code in data.get("saving_throw_proficiencies", []):
            try:
                saving_throws.append(Ability[ab_code])
            except KeyError:
                pass

        weapons = [
            Weapon(
                name=w.get("name", "Arme"),
                damage_dice=w.get("damage_dice", "1d6"),
                damage_type=w.get("damage_type", "tranchant"),
                is_finesse=w.get("is_finesse", False),
                is_ranged=w.get("is_ranged", False),
                magic_bonus=w.get("magic_bonus", 0),
                attack_bonus_override=w.get("attack_bonus_override"),
                extra_damage_desc=w.get("extra_damage_desc", "")
            )
            for w in data.get("weapons", [])
        ]

        spells = [
            Spell(
                name=s.get("name", "Sort"),
                level=int(s.get("level", 0)),
                school=s.get("school", "Évocation"),
                casting_time=s.get("casting_time", "1 action"),
                range_area=s.get("range_area", "18 m"),
                duration=s.get("duration", "Instantanée"),
                concentration=s.get("concentration", False),
                description=s.get("description", "")
            )
            for s in data.get("known_spells", [])
        ]

        armor_data = data.get("equipped_armor")
        equipped_armor = None
        if armor_data:
            a_type = ArmorType.LIGHT
            for t in ArmorType:
                if t.value == armor_data.get("armor_type"):
                    a_type = t
                    break
            equipped_armor = Armor(
                name=armor_data.get("name", "Armure"),
                armor_type=a_type,
                base_ac=armor_data.get("base_ac", 11),
                magic_bonus=armor_data.get("magic_bonus", 0)
            )

        shield_data = data.get("equipped_shield")
        equipped_shield = Armor(name="Bouclier", armor_type=ArmorType.SHIELD, base_ac=2) if shield_data else None

        # Conversion emplacements de sorts
        slots_used = {}
        for k, v in data.get("spell_slots_used", {}).items():
            try:
                slots_used[int(k)] = int(v)
            except ValueError:
                pass

        # Devises et Bourse
        curr_raw = data.get("currency", {})
        currency = {
            "po": int(curr_raw.get("po", 0)),
            "pa": int(curr_raw.get("pa", 0)),
            "pc": int(curr_raw.get("pc", 0)),
            "pe": int(curr_raw.get("pe", 0)),
            "pp": int(curr_raw.get("pp", 0)),
        }

        # Inventaire d'objets (avec enrichissement LIKE automatique si description absente)
        inventory = []
        tr_notes = data.get("treasure_notes", "")
        app_notes = data.get("appearance", "")
        for it in data.get("inventory", []):
            it_name = it.get("name", "Objet")
            it_w = float(it.get("weight", 0.0))
            it_d = it.get("description", "")
            it_c = it.get("category", "Aventurier")
            if not it_d or it_w == 0.0:
                db_w, db_d, db_c = db.match_item_in_db(it_name, tr_notes, app_notes)
                if not it_d and db_d:
                    it_d = db_d
                if it_w == 0.0 and db_w > 0.0:
                    it_w = db_w
                if it_c == "Aventurier" and db_c:
                    it_c = db_c
            inventory.append(Item(
                name=it_name,
                quantity=int(it.get("quantity", 1)),
                category=it_c,
                weight=it_w,
                description=it_d,
                is_equipped=bool(it.get("is_equipped", False))
            ))

        return cls(
            name=data.get("name", "Héros Sans Nom"),
            player_name=data.get("player_name", ""),
            xp=int(data.get("xp", 0)),
            race=data.get("race", "Humain"),
            background=data.get("background", "Aventurier"),
            alignment=data.get("alignment", "Neutre Pur"),
            raw_abilities=abilities,
            classes=data.get("classes", {"Guerrier": 1}),
            subclasses=data.get("subclasses", {}),
            saving_throw_proficiencies=saving_throws,
            skill_proficiencies=data.get("skill_proficiencies", []),
            skill_expertises=data.get("skill_expertises", []),
            equipped_armor=equipped_armor,
            equipped_shield=equipped_shield,
            weapons=weapons,
            known_spells=spells,
            traits_and_features=data.get("traits_and_features", []),
            pv_max=int(data.get("pv_max", 50)),
            pv_current=int(data.get("pv_current", 50)),
            pv_temp=int(data.get("pv_temp", 0)),
            exhaustion=int(data.get("exhaustion", 0)),
            speed=int(data.get("speed", 9)),
            currency=currency,
            inventory=inventory,
            languages_and_proficiencies=data.get("languages_and_proficiencies", ""),
            personality_traits=data.get("personality_traits", ""),
            ideals=data.get("ideals", ""),
            bonds=data.get("bonds", ""),
            flaws=data.get("flaws", ""),
            age=data.get("age", ""),
            height=data.get("height", ""),
            weight=data.get("weight", ""),
            eyes=data.get("eyes", ""),
            skin=data.get("skin", ""),
            hair=data.get("hair", ""),
            appearance=data.get("appearance", ""),
            allies=data.get("allies", ""),
            backstory=data.get("backstory", ""),
            treasure_notes=data.get("treasure_notes", ""),
            additional_features_notes=data.get("additional_features_notes", ""),
            death_saves=data.get("death_saves", {"successes": 0, "failures": 0}),
            spell_slots_used=slots_used,
            pact_slots_used=int(data.get("pact_slots_used", 0)),
            hit_dice_used=data.get("hit_dice_used", {})
        )

# ==============================================================================
# 3. INITIALISATION DU PERSONNAGE PAR DÉFAUT (FICHE VIERGE)
# ==============================================================================

def get_default_character() -> CharacterSheet:
    """Retourne une fiche de personnage vierge prête pour une nouvelle création."""
    char = CharacterSheet(
        name="Nouvel Aventurier",
        race="Humain",
        background="Aventurier",
        alignment="Neutre Pur",
        raw_abilities={
            Ability.STR: 10,
            Ability.DEX: 10,
            Ability.CON: 10,
            Ability.INT: 10,
            Ability.WIS: 10,
            Ability.CHA: 10,
        },
        classes={"Guerrier": 1},
        subclasses={},
        saving_throw_proficiencies=[Ability.STR, Ability.CON],
        skill_proficiencies=[],
        skill_expertises=[],
        traits_and_features=[
            "Second Souffle (Second Wind)",
            "Style de Combat"
        ],
        pv_max=10,
        pv_current=10,
        pv_temp=0,
        speed=9,
        currency={"po": 15, "pa": 0, "pc": 0, "pe": 0, "pp": 0},
        inventory=[
            Item(name="Sac à dos d'aventurier", quantity=1, category="Aventurier", weight=2.5, description="Contient tout le nécessaire de voyage."),
            Item(name="Paillasse (sac de couchage)", quantity=1, category="Aventurier", weight=3.0, description="Pour le repos long au bivouac."),
            Item(name="Corde en chanvre (15 m)", quantity=1, category="Aventurier", weight=5.0, description="Solide et fiable."),
            Item(name="Lanterne sourde", quantity=1, category="Aventurier", weight=1.0, description="Lumière vive sur 18m avec volet occultant."),
            Item(name="Rations de voyage (1 jour)", quantity=5, category="Aventurier", weight=1.0, description="Vivres de route compactes."),
            Item(name="Outre d'eau", quantity=1, category="Aventurier", weight=2.5, description="2 litres d'eau fraîche."),
            Item(name="Potion de soins (2d4+2)", quantity=1, category="Potion", weight=0.2, description="Restaure 2d4+2 PV."),
        ]
    )
    char.equipped_armor = Armor(
        name="Tissu / Vêtements",
        armor_type=ArmorType.NONE,
        base_ac=10,
        magic_bonus=0,
    )
    char.weapons = [
        Weapon(name="Épée longue", damage_dice="1d8", damage_type="tranchant", is_finesse=False, is_ranged=False),
    ]
    char.known_spells = []
    return char

def sync_session_state_from_char(c: CharacterSheet):
    """
    Incrémente le compteur de version des widgets afin que tous les curseurs de caractéristiques,
    champs de monnaies, niveaux et armures prennent immédiatement les nouvelles valeurs du personnage
    sans jamais être écrasés par l'ancien état du navigateur ni lever d'exception Streamlit.
    """
    st.session_state["widget_version"] = st.session_state.get("widget_version", 0) + 1


def apply_imported_pdf_to_char(char: CharacterSheet, extracted_data: dict):
    """Applique l'ensemble des données extraites d'un PDF D&D 5e à une instance CharacterSheet."""
    char.name = extracted_data["name"]
    char.race = extracted_data["race"]
    char.player_name = extracted_data.get("player_name", "")
    char.xp = extracted_data.get("xp", 0)
    if extracted_data.get("background"):
        char.background = extracted_data["background"]
    if extracted_data.get("alignment"):
        char.alignment = extracted_data["alignment"]
    if extracted_data.get("classes"):
        char.classes = extracted_data["classes"]
    if extracted_data.get("subclasses"):
        char.subclasses = extracted_data["subclasses"]
    char.raw_abilities = {}
    for ab_code, val in extracted_data.get("raw_abilities", {}).items():
        try:
            char.raw_abilities[Ability[ab_code]] = int(val)
        except KeyError:
            pass
    char.pv_max = extracted_data["pv_max"]
    char.pv_current = extracted_data["pv_current"]
    char.pv_temp = extracted_data.get("pv_temp", 0)
    char.exhaustion = extracted_data.get("exhaustion", 0)
    char.speed = extracted_data["speed"]
    if extracted_data.get("equipped_armor_name") and extracted_data["equipped_armor_name"] in db.ARMORS_DB:
        arm_n = extracted_data["equipped_armor_name"]
        arm_d = db.ARMORS_DB[arm_n]
        t_map = {
            "Légère": ArmorType.LIGHT,
            "Intermédiaire": ArmorType.MEDIUM,
            "Lourde": ArmorType.HEAVY,
            "Aucune": ArmorType.NONE
        }
        char.equipped_armor = Armor(
            name=arm_n,
            armor_type=t_map.get(arm_d["type"], ArmorType.NONE),
            base_ac=arm_d["base_ac"],
            max_dex_bonus=arm_d["max_dex"]
        )
    if extracted_data.get("currency"):
        char.currency = dict(extracted_data["currency"])
    if extracted_data.get("inventory"):
        char.inventory = [
            Item(
                name=it["name"],
                quantity=it.get("quantity", 1),
                category=it.get("category", "Aventurier"),
                weight=it.get("weight", 0.0),
                description=it.get("description", ""),
                is_equipped=it.get("is_equipped", False)
            )
            for it in extracted_data["inventory"]
        ]
    if extracted_data.get("saving_throw_proficiencies"):
        st_profs = []
        for st_code in extracted_data["saving_throw_proficiencies"]:
            try:
                st_profs.append(Ability[st_code])
            except KeyError:
                pass
        if st_profs:
            char.saving_throw_proficiencies = st_profs
    if extracted_data.get("skill_proficiencies"):
        char.skill_proficiencies = list(dict.fromkeys(extracted_data["skill_proficiencies"]))
    if extracted_data.get("skill_expertises"):
        char.skill_expertises = list(dict.fromkeys(extracted_data["skill_expertises"]))
    if extracted_data.get("weapons"):
        char.weapons = [
            Weapon(
                name=w["name"],
                damage_dice=w.get("damage_dice", "1d8"),
                damage_type=w.get("damage_type", "tranchant"),
                is_finesse=w.get("is_finesse", False),
                is_ranged=w.get("is_ranged", False),
                magic_bonus=w.get("magic_bonus", 0),
                attack_bonus_override=w.get("attack_bonus_override"),
                extra_damage_desc=w.get("extra_damage_desc", "")
            )
            for w in extracted_data["weapons"]
        ]
    if extracted_data.get("known_spells"):
        char.known_spells = [
            Spell(
                name=s["name"],
                level=s.get("level", 1),
                school=s.get("school", "Évocation"),
                casting_time=s.get("casting_time", "1 action"),
                range_area=s.get("range_area", "18 m"),
                duration=s.get("duration", "Instantanée"),
                concentration=s.get("concentration", False),
                description=s.get("description", "")
            )
            for s in extracted_data["known_spells"]
        ]
    if "spell_slots_used" in extracted_data:
        char.spell_slots_used = extracted_data["spell_slots_used"]

    # Champs RP, Histoire & Apparence (Pages 1 & 2)
    for rp_key in [
        "languages_and_proficiencies", "personality_traits", "ideals", "bonds", "flaws",
        "age", "height", "weight", "eyes", "skin", "hair", "appearance",
        "allies", "backstory", "treasure_notes", "additional_features_notes"
    ]:
        if extracted_data.get(rp_key):
            setattr(char, rp_key, extracted_data[rp_key])

    # Synchronisation automatique des aptitudes officielles + aptitudes spéciales du PDF
    base_traits = list(extracted_data.get("traits", []))
    updated_f, _ = db.sync_character_features(char.classes, char.subclasses, base_traits)
    char.traits_and_features = updated_f

if "char" not in st.session_state:
    st.session_state.char = get_default_character()
    st.session_state["widget_version"] = 0

w_ver: int = st.session_state.get("widget_version", 0)
char: CharacterSheet = st.session_state.char

# Thème actif selon la classe principale
primary_class = max(char.classes.items(), key=lambda x: x[1])[0] if char.classes else "Rôdeur"
class_meta = db.CLASSES_DND.get(primary_class, db.CLASSES_DND["Rôdeur"])
theme = class_meta["theme"]
theme_icon = class_meta["icon"]

# ==============================================================================
# 4. INJECTION CSS - THÈME GRIMOIRE MÉDIÉVAL FANTASTIQUE D&D
# ==============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@600;700&family=Alegreya:ital,wght@0,400;0,700;1,400&display=swap');

    .stApp {{
        background: radial-gradient(circle at 50% 10%, #202328 0%, #131518 100%);
        color: #e8dcc6;
        font-family: 'Alegreya', Georgia, serif;
        font-size: 1.08rem;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #17191d !important;
        border-right: 2px solid {theme['primary']};
        box-shadow: 4px 0px 20px rgba(0,0,0,0.7);
    }}

    h1, h2, h3, h4 {{
        font-family: 'Cinzel', serif !important;
        color: {theme['accent']} !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        letter-spacing: 0.8px;
    }}

    /* Cadre héroïque façon parchemin officiel */
    .hero-banner {{
        background: linear-gradient(135deg, rgba(32,36,42,0.95), rgba(18,20,24,0.95));
        border: 2px solid {theme['primary']};
        border-radius: 8px;
        padding: 22px 26px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.6);
        margin-bottom: 22px;
    }}
    .hero-title {{
        font-family: 'Cinzel Decorative', serif;
        font-size: 2.3rem;
        color: {theme['accent']};
        margin: 0;
    }}
    .hero-sub {{
        color: #b3a693;
        font-size: 1.15rem;
        font-style: italic;
    }}

    /* Blasons de caractéristiques (FOR, DEX, CON...) */
    .stat-badge {{
        background: linear-gradient(180deg, #282c33 0%, #191c20 100%);
        border: 2px solid {theme['secondary']};
        border-radius: 8px;
        text-align: center;
        padding: 10px 4px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .stat-badge:hover {{
        transform: translateY(-3px);
        border-color: {theme['accent']};
    }}
    .stat-name {{
        font-family: 'Cinzel', serif;
        font-size: 0.82rem;
        color: #d1c5b0;
        text-transform: uppercase;
        font-weight: 700;
    }}
    .stat-mod {{
        font-family: 'Cinzel', serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: {theme['accent']};
        line-height: 1.15;
    }}
    .stat-score {{
        font-size: 0.9rem;
        color: #8c8273;
        border-top: 1px solid rgba(255,255,255,0.1);
        display: inline-block;
        padding-top: 2px;
        width: 60%;
    }}

    /* Cartes de métriques clés */
    .metric-shield {{
        background: rgba(28, 31, 36, 0.92);
        border: 1px solid {theme['primary']};
        border-radius: 6px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    .metric-value {{
        font-family: 'Cinzel', serif;
        font-size: 1.8rem;
        color: {theme['accent']};
        font-weight: bold;
    }}
    .metric-label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #baa992;
    }}

    /* Boîte de gestion des points de vie */
    .hp-container {{
        background: rgba(22, 25, 30, 0.95);
        border: 2px solid {theme['primary']};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }}

    /* Cartes d'armes et de sorts */
    .card-combat {{
        background: #1c1f24;
        border-left: 4px solid {theme['primary']};
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}

    /* Pastilles d'emplacements de sorts */
    .slot-pill {{
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 4px;
    }}
    .slot-available {{
        background-color: #2ecc71;
        box-shadow: 0 0 6px #2ecc71;
    }}
    .slot-used {{
        background-color: #555;
        border: 1px solid #777;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. SIDEBAR : LE GRIMOIRE D'ÉDITION, IMPORT & EXPORT
# ==============================================================================

with st.sidebar:
    st.markdown(f"### {theme_icon} Grimoire du Héros")
    st.caption(f"Classe majeure active : **{primary_class}**")

    tab_bio, tab_stats, tab_import = st.tabs(["Identité", "Caractéristiques", "Fichiers & Import"])

    with tab_bio:
        st.subheader("État Civil")
        char.name = st.text_input("Nom du Héros", value=char.name)
        char.race = st.text_input("Peuple / Race", value=char.race)
        char.background = st.text_input("Historique", value=char.background)
        col_pl, col_xp = st.columns(2)
        with col_pl:
            char.player_name = st.text_input("Nom du Joueur", value=char.player_name)
        with col_xp:
            char.xp = st.number_input("Points d'XP", min_value=0, max_value=1000000, value=char.xp, step=100)
        
        aligns = ["Loyal Bon", "Neutre Bon", "Chaotique Bon", "Loyal Neutre", "Neutre Pur", "Chaotique Neutre", "Loyal Mauvais", "Neutre Mauvais", "Chaotique Mauvais"]
        char.alignment = st.selectbox("Alignement", aligns, index=aligns.index(char.alignment) if char.alignment in aligns else 5)

        st.divider()
        st.subheader("Classes & Sous-Classes")
        level_changed = False
        for cls_name in list(char.classes.keys()):
            col_c1, col_c2, col_c3 = st.columns([3, 2, 1])
            with col_c1:
                st.write(f"**{cls_name}**")
            with col_c2:
                old_lvl = char.classes[cls_name]
                new_lvl = st.number_input(f"Niv {cls_name}", min_value=1, max_value=20, value=old_lvl, key=f"lvl_{cls_name}_{w_ver}", label_visibility="collapsed")
                if new_lvl != old_lvl:
                    char.classes[cls_name] = new_lvl
                    level_changed = True
            with col_c3:
                if len(char.classes) > 1:
                    if st.button("❌", key=f"del_{cls_name}_{w_ver}", help=f"Retirer la classe {cls_name}"):
                        del char.classes[cls_name]
                        if cls_name in char.subclasses:
                            del char.subclasses[cls_name]
                        level_changed = True
                        st.rerun()

            # Règle officielle D&D 5e : Sous-classe débloquée au niveau 3
            cls_level = char.classes.get(cls_name, 1)
            available_subs = db.CLASSES_DND.get(cls_name, {}).get("subclasses", [])
            if cls_level < 3:
                st.info(f"🔒 **Sous-classe {cls_name}** : Accessible au **Niveau 3** (Actuel: Niv {cls_level})")
                if cls_name in char.subclasses:
                    del char.subclasses[cls_name]
            else:
                current_sub = char.subclasses.get(cls_name, available_subs[0] if available_subs else "Aucune")
                sub_idx = available_subs.index(current_sub) if current_sub in available_subs else 0
                selected_sub = st.selectbox(f"Sous-classe ({cls_name})", available_subs, index=sub_idx, key=f"sub_{cls_name}_{w_ver}")
                if selected_sub != current_sub:
                    char.subclasses[cls_name] = selected_sub
                    level_changed = True

        # Synchronisation automatique des aptitudes lors de gains de niveau ou changement de sous-classe
        if level_changed:
            updated_feats, added_feats = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
            char.traits_and_features = updated_feats
            max_exp_now = db.get_max_expertises_count(char.classes)
            exp_notice = f" | ⭐ Vous avez droit à {max_exp_now} Expertises de compétences !" if max_exp_now > len(char.skill_expertises) else ""
            if added_feats or exp_notice:
                st.session_state["toast_msg"] = f"🎉 Niveau mis à jour ! {('Nouvelles aptitudes : ' + ', '.join(added_feats)) if added_feats else ''}{exp_notice}"
            st.rerun()

        # Affichage de la notification si présente
        if "toast_msg" in st.session_state:
            st.toast(st.session_state.pop("toast_msg"))

        # Sélecteur direct des Expertises de Classe (Roublard Niv 1/6, Barde Niv 3/10)
        max_exp_allowed = db.get_max_expertises_count(char.classes)
        if max_exp_allowed > 0:
            st.markdown(f"**⭐ Expertises de Classe ({len(char.skill_expertises)} / {max_exp_allowed})**")
            st.caption(f"Double votre bonus de maîtrise (+{char.proficiency_bonus * 2} au lieu de +{char.proficiency_bonus}) sur {max_exp_allowed} compétences :")
            candidate_skills = char.skill_proficiencies if char.skill_proficiencies else list(SKILL_ABILITY_MAP.keys())
            all_opts = list(dict.fromkeys(candidate_skills + char.skill_expertises + list(SKILL_ABILITY_MAP.keys())))
            chosen_exps = st.multiselect(
                "Compétences avec Expertise (x2)",
                options=all_opts,
                default=[s for s in char.skill_expertises if s in all_opts],
                max_selections=max(max_exp_allowed, len(char.skill_expertises), 4),
                key=f"sidebar_exp_{w_ver}"
            )
            if chosen_exps != char.skill_expertises:
                char.skill_expertises = chosen_exps
                for sk_e in chosen_exps:
                    if sk_e not in char.skill_proficiencies:
                        char.skill_proficiencies.append(sk_e)
                st.rerun()

        # Ajouter une nouvelle classe
        new_classes_avail = [c for c in db.CLASSES_DND.keys() if c not in char.classes]
        if new_classes_avail:
            new_cls = st.selectbox("Ajouter une classe", ["-- Sélectionner --"] + new_classes_avail, key=f"new_cls_{w_ver}")
            if new_cls != "-- Sélectionner --":
                if st.button(f"Emprunter la voie du {new_cls}"):
                    char.classes[new_cls] = 1
                    # Au niveau 1, pas de sous-classe (débloquée au niveau 3)
                    if new_cls in char.subclasses:
                        del char.subclasses[new_cls]
                    updated_feats, _ = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
                    char.traits_and_features = updated_feats
                    st.rerun()

        st.write("")
        col_rst1, col_rst2 = st.columns(2)
        with col_rst1:
            if st.button("📄 Fiche Vierge", use_container_width=True, help="Réinitialiser avec un modèle de fiche vierge"):
                st.session_state.char = get_default_character()
                sync_session_state_from_char(st.session_state.char)
                st.rerun()
        with col_rst2:
            import os
            if os.path.exists("hythus_feuille_d_argent.json"):
                if st.button("🧝 Hythus (Exemple)", use_container_width=True, help="Charger la fiche d'exemple préremplie de Hythus"):
                    with open("hythus_feuille_d_argent.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        st.session_state.char = CharacterSheet.from_dict(data)
                        sync_session_state_from_char(st.session_state.char)
                    st.rerun()

    with tab_stats:
        st.subheader("Caractéristiques Brutes")
        for ab in Ability:
            current_ab_score = char.get_ability_score(ab)
            new_ab_score = st.slider(
                f"{ab.value} ({ab.name})",
                min_value=1,
                max_value=30,
                value=current_ab_score,
                key=f"slider_{ab.name}_{w_ver}"
            )
            char.raw_abilities[ab] = new_ab_score
        st.divider()
        st.subheader("Vitesse & Équipement")
        char.speed = st.number_input("Vitesse (mètres)", min_value=1, max_value=30, value=char.speed, key=f"speed_in_{w_ver}")
        
        # Armure équipée
        armors_keys = list(db.ARMORS_DB.keys())
        current_armor_name = char.equipped_armor.name if char.equipped_armor else armors_keys[0]
        arm_idx = armors_keys.index(current_armor_name) if current_armor_name in armors_keys else 0
        chosen_armor_name = st.selectbox("Armure équipée", armors_keys, index=arm_idx, key=f"armor_sel_{w_ver}")
        arm_info = db.ARMORS_DB[chosen_armor_name]
        
        # Mapping ArmorType
        type_mapping = {
            "Légère": ArmorType.LIGHT,
            "Intermédiaire": ArmorType.MEDIUM,
            "Lourde": ArmorType.HEAVY,
            "Aucune": ArmorType.NONE
        }
        char.equipped_armor = Armor(
            name=chosen_armor_name,
            armor_type=type_mapping.get(arm_info["type"], ArmorType.NONE),
            base_ac=arm_info["base_ac"],
            max_dex_bonus=arm_info["max_dex"]
        )

        porte_bouclier = st.checkbox("Porter un Bouclier (+2 CA)", value=(char.equipped_shield is not None), key=f"shield_chk_{w_ver}")
        char.equipped_shield = Armor(name="Bouclier", armor_type=ArmorType.SHIELD, base_ac=2) if porte_bouclier else None

    with tab_import:
        st.subheader("📜 Importer une Feuille")
        st.caption("Chargez un PDF (feuille D&D officielle) ou un fichier JSON sauvegardé.")
        
        uploaded_file = st.file_uploader("Fichier PDF ou JSON", type=["pdf", "json"])
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            if uploaded_file.name.endswith(".json"):
                try:
                    data = parse_json_character(bytes_data)
                    st.success("Fichier JSON valide !")
                    if st.button("Restaurer ce Héros depuis JSON"):
                        st.session_state.char = CharacterSheet.from_dict(data)
                        sync_session_state_from_char(st.session_state.char)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur de lecture du JSON : {e}")
            elif uploaded_file.name.endswith(".pdf"):
                try:
                    extracted_data, summary = parse_pdf_character(bytes_data)
                    st.info(summary)
                    if st.button("Appliquer les données du PDF à la fiche"):
                        apply_imported_pdf_to_char(char, extracted_data)
                        sync_session_state_from_char(char)
                        st.success("Données du PDF injectées avec succès !")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur d'analyse du PDF : {e}")

        st.divider()
        st.subheader("💾 Exporter la Fiche")
        json_export = json.dumps(char.to_dict(), indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger la Fiche (JSON)",
            data=json_export,
            file_name=f"{char.name.replace(' ', '_')}_DnD5e.json",
            mime="application/json"
        )

# ==============================================================================
# 6. BANNIÈRE PRINCIPALE HÉROÏQUE
# ==============================================================================

class_items = []
for cls, lvl in char.classes.items():
    if lvl >= 3 and cls in char.subclasses and char.subclasses[cls]:
        class_items.append(f"{cls} ({char.subclasses[cls]}) Niv {lvl}")
    else:
        class_items.append(f"{cls} Niv {lvl}")
class_summary_str = " / ".join(class_items)
player_badge = f" • Joueur : <b>{char.player_name}</b>" if char.player_name else ""
xp_badge = f" • XP : <b>{char.xp:,}</b>".replace(",", " ") if char.xp > 0 else ""
exh_banner = f" <span style='background:#c0392b; color:#fff; padding:3px 10px; border-radius:4px; font-size:0.9rem;'>⚠️ Épuisement Niv {char.exhaustion}</span>" if char.exhaustion > 0 else ""

st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 class="hero-title">{theme_icon} {char.name}{exh_banner}</h1>
            <div class="hero-sub">{char.race} ({char.background}) • {class_summary_str} • {char.alignment} (Niveau Total {char.total_level}){player_badge}{xp_badge}</div>
        </div>
        <div style="text-align: right; margin-top: 10px;">
            <span style="font-size: 1.1rem; color: {theme['accent']}; font-style: italic;">{class_meta.get('theme', {}).get('quote', '« Que les dés soient favorables à ton destin. »')}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. LES 6 CARACTÉRISTIQUES D&D (BADGES BLASONS)
# ==============================================================================

cols_stats = st.columns(6)
for i, ab in enumerate(Ability):
    score = char.get_ability_score(ab)
    mod = char.get_ability_modifier(ab)
    sign = f"+{mod}" if mod >= 0 else f"{mod}"
    with cols_stats[i]:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-name">{ab.value[:4]}</div>
            <div class="stat-mod">{sign}</div>
            <div class="stat-score">{score}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 8. STATISTIQUES COMBAT & GESTION DES POINTS DE VIE, REPOS & MORTS
# ==============================================================================

# Métriques rapides
col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
dex_mod = char.get_ability_modifier(Ability.DEX)
init_sign = f"+{dex_mod}" if dex_mod >= 0 else f"{dex_mod}"

with col_m1:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">🛡️ {char.armor_class}</div><div class="metric-label">Classe d'Armure</div></div>""", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">⚡ {init_sign}</div><div class="metric-label">Initiative</div></div>""", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">👣 {char.speed} m</div><div class="metric-label">Vitesse</div></div>""", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">🎯 +{char.proficiency_bonus}</div><div class="metric-label">Bonus Maîtrise</div></div>""", unsafe_allow_html=True)
with col_m5:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">👁️ {char.passive_perception}</div><div class="metric-label">Perception Pass.</div></div>""", unsafe_allow_html=True)
with col_m6:
    pv_ratio = max(0.0, min(1.0, char.pv_current / max(1, char.pv_max)))
    pv_color = "#4caf50" if pv_ratio > 0.5 else ("#ff9800" if pv_ratio > 0.25 else "#f44336")
    temp_badge = f" (+{char.pv_temp} Temp)" if char.pv_temp > 0 else ""
    st.markdown(f"""<div class="metric-shield"><div class="metric-value" style="color: {pv_color};">❤️ {char.pv_current}/{char.pv_max}</div><div class="metric-label">PV{temp_badge}</div></div>""", unsafe_allow_html=True)

st.write("")

# Panneau Vital : PV, Dégâts, Soins, Repos Long & Court
with st.container(border=True):
    col_hp_actions, col_rests, col_death = st.columns([4, 4, 3])

    # 1. Action sur les PV (Dégâts / Soins / PV Temporaires)
    with col_hp_actions:
        st.markdown("#### ❤️ Gestion des Points de Vie")
        
        # Barre de progression de vie
        progress_val = max(0.0, min(1.0, char.pv_current / max(1, char.pv_max)))
        st.progress(progress_val)
        
        col_dmg, col_heal = st.columns(2)
        with col_dmg:
            dmg_amount = st.number_input("Subir Dégâts", min_value=1, max_value=200, value=5, key="input_dmg")
            if st.button("💥 Appliquer Dégâts", use_container_width=True):
                # Absorption des PV temporaires d'abord
                remaining_dmg = dmg_amount
                if char.pv_temp > 0:
                    if remaining_dmg <= char.pv_temp:
                        char.pv_temp -= remaining_dmg
                        remaining_dmg = 0
                    else:
                        remaining_dmg -= char.pv_temp
                        char.pv_temp = 0
                
                char.pv_current = max(0, char.pv_current - remaining_dmg)
                st.rerun()

        with col_heal:
            heal_amount = st.number_input("Soigner", min_value=1, max_value=200, value=5, key="input_heal")
            if st.button("✨ Appliquer Soins", use_container_width=True):
                char.pv_current = min(char.pv_max, char.pv_current + heal_amount)
                # Si on est soigné au-dessus de 0, réinitialise les jets de mort
                if char.pv_current > 0:
                    char.death_saves = {"successes": 0, "failures": 0}
                st.rerun()

        # PV Temporaires
        col_t1, col_t2 = st.columns([3, 2])
        with col_t1:
            temp_in = st.number_input("Ajouter PV Temporaires", min_value=1, max_value=100, value=5, key="input_temp")
        with col_t2:
            st.write("")
            st.write("")
            if st.button("🛡️ Définir Temp", use_container_width=True):
                # Règle D&D 5e : les PV temporaires ne se cumulent pas, on prend le plus haut
                char.pv_temp = max(char.pv_temp, temp_in)
                st.rerun()

    # 2. Gestion des Repos (Court & Long)
    with col_rests:
        st.markdown("#### ⛺ Repos & Récupération")
        
        # Affichage des dés de vie
        total_hit_dice = db.get_total_hit_dice(char.classes)
        hd_display = []
        for hd_type, total_cnt in total_hit_dice.items():
            used = char.hit_dice_used.get(hd_type, 0)
            avail = max(0, total_cnt - used)
            hd_display.append(f"**{hd_type}** : {avail}/{total_cnt} dispo")
        st.caption("Dés de vie : " + " | ".join(hd_display))

        # Repos Long
        if st.button("🌙 Repos Long (8 heures)", use_container_width=True):
            char.pv_current = char.pv_max
            char.pv_temp = 0
            char.death_saves = {"successes": 0, "failures": 0}
            char.spell_slots_used = {}
            char.pact_slots_used = 0
            if char.exhaustion > 0:
                char.exhaustion = max(0, char.exhaustion - 1)
            
            # Récupère la moitié des dés de vie totaux
            total_dice_count = sum(total_hit_dice.values())
            recovered_allowance = max(1, math.ceil(total_dice_count / 2))
            
            for hd_type in char.hit_dice_used:
                used = char.hit_dice_used[hd_type]
                to_recover = min(used, recovered_allowance)
                char.hit_dice_used[hd_type] -= to_recover
                recovered_allowance -= to_recover
                if recovered_allowance <= 0:
                    break
            
            st.success("Repos long achevé ! PV restaurés au maximum, emplacements de sorts rechargés, dés de vie récupérés (et -1 niveau d'épuisement).")
            st.rerun()

        # Niveau d'Épuisement (Règles officielles D&D 5e)
        new_exh = st.selectbox(
            "🥵 Niveau d'Épuisement (0 à 6)",
            options=[0, 1, 2, 3, 4, 5, 6],
            index=min(6, max(0, char.exhaustion)),
            format_func=lambda x: db.EXHAUSTION_EFFECTS.get(x, f"Niveau {x}") if x > 0 else "Niveau 0 : Aucun effet d'épuisement",
            key=f"exh_sel_{w_ver}"
        )
        if new_exh != char.exhaustion:
            char.exhaustion = new_exh
            st.rerun()
        if char.exhaustion > 0:
            st.warning(f"⚠️ **{db.EXHAUSTION_EFFECTS.get(char.exhaustion, '')}**")

        # Repos Court avec dépense de dés de vie
        with st.expander("⏳ Prendre un Repos Court (1 heure)"):
            con_mod = char.get_ability_modifier(Ability.CON)
            avail_dice = {}
            for hd_t, total_c in total_hit_dice.items():
                u = char.hit_dice_used.get(hd_t, 0)
                if total_c - u > 0:
                    avail_dice[hd_t] = total_c - u

            if avail_dice:
                chosen_hd = st.selectbox("Type de dé à dépenser", list(avail_dice.keys()), key="rest_hd_type")
                max_rollable = avail_dice[chosen_hd]
                num_dice = st.number_input("Nombre de dés", min_value=1, max_value=max_rollable, value=1, key="rest_hd_count")
                
                if st.button("🎲 Dépenser ces dés et récupérer des PV"):
                    sides = int(chosen_hd.replace("d", ""))
                    total_healed = 0
                    rolls = []
                    for _ in range(num_dice):
                        r = random.randint(1, sides)
                        rolls.append(r)
                        total_healed += max(0, r + con_mod)
                    
                    char.hit_dice_used[chosen_hd] = char.hit_dice_used.get(chosen_hd, 0) + num_dice
                    char.pv_current = min(char.pv_max, char.pv_current + total_healed)
                    
                    # Récupération spécifique Occultiste (Magie de Pacte)
                    if "Occultiste" in char.classes:
                        char.pact_slots_used = 0
                        st.info("👁️ Occultiste : Tous vos emplacements de Magie de Pacte ont été réinitialisés !")

                    st.success(f"Repos court : Jets de {chosen_hd} = {rolls} + {con_mod} CON. Vous récupérez **{total_healed} PV** !")
                    st.rerun()
            else:
                st.warning("Aucun dé de vie disponible pour se soigner pendant ce repos court.")
                if "Occultiste" in char.classes and st.button("Recharger la Magie de Pacte sans dés"):
                    char.pact_slots_used = 0
                    st.success("Magie de Pacte rechargée !")
                    st.rerun()

    # 3. Jets de Sauvegarde contre la mort
    with col_death:
        st.markdown("#### 💀 Sauvegardes contre la Mort")
        if char.pv_current == 0:
            st.error("⚠️ LE HÉROS EST À TERRE ET INCONSCIENT !")
        
        suc = char.death_saves.get("successes", 0)
        fai = char.death_saves.get("failures", 0)

        # Affichage visuel des succès et échecs
        st.write(f"**Succès** ({suc}/3) : {'🟢 ' * suc}{'⚪ ' * (3 - suc)}")
        st.write(f"**Échecs** ({fai}/3) : {'🔴 ' * fai}{'⚪ ' * (3 - fai)}")

        if st.button("🎲 Lancer un Jet contre la Mort", disabled=(char.pv_current > 0 or suc >= 3 or fai >= 3)):
            roll = random.randint(1, 20)
            if roll == 20:
                char.pv_current = 1
                char.death_saves = {"successes": 0, "failures": 0}
                st.balloons()
                st.success("🔥 20 NATUREL ! Le héros reprend conscience avec 1 PV !")
            elif roll >= 10:
                char.death_saves["successes"] = suc + 1
                st.success(f"Succès ({roll}) !")
            elif roll == 1:
                char.death_saves["failures"] = min(3, fai + 2)
                st.error("💀 1 NATUREL ! 2 Échecs critiques !")
            else:
                char.death_saves["failures"] = fai + 1
                st.warning(f"Échec ({roll}) !")
            st.rerun()

        if suc >= 3:
            st.info("🛡️ Stabilisé ! Le héros est inconscient mais hors de danger mortel.")
        elif fai >= 3:
            st.error("⚰️ Mort... Que son âme repose dans les Terres Extérieures.")

        if st.button("Réinitialiser les jets de mort", key="reset_death"):
            char.death_saves = {"successes": 0, "failures": 0}
            st.rerun()

st.divider()

# ==============================================================================
# 9. CORPS PRINCIPAL : ONGLETS DÉDIÉS EN PLEINE LARGEUR
# ==============================================================================

tab_arsenal, tab_inv, tab_grimoire, tab_traits, tab_skills, tab_lore = st.tabs([
    "⚔️ Arsenal & Combat",
    "🎒 Inventaire & Bourse",
    "🔮 Grimoire & Sorts",
    "✨ Aptitudes de Classe & Dons",
    "📜 Compétences & Sauvegardes",
    "📖 Histoire, RP & Détails"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : ARSENAL & COMBAT
# ------------------------------------------------------------------------------
with tab_arsenal:
    st.markdown("### ⚔️ Arsenal & Attaques Équipées")
    
    if char.weapons:
        for idx_w, w in enumerate(char.weapons):
            att_bonus, dmg_formula = char.calculate_weapon_attack(w)
            att_str = f"+{att_bonus}" if att_bonus >= 0 else f"{att_bonus}"
            
            col_w_card, col_w_del = st.columns([8, 1])
            with col_w_card:
                st.markdown(f"""
                <div class="card-combat">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: bold; color: #fff;">{w.name}</span>
                        <span style="background: {theme['primary']}; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #fff;">Toucher : {att_str}</span>
                    </div>
                    <div style="color: #c9baa2; margin-top: 6px; font-size: 1rem;">
                        🎲 <b>Dégâts :</b> {dmg_formula} | <i>{'Distance' if w.is_ranged else ('Finesse' if w.is_finesse else 'Corps-à-corps')}</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_w_del:
                st.write("")
                if st.button("🗑️", key=f"del_w_{idx_w}", help="Retirer cette arme"):
                    char.weapons.pop(idx_w)
                    st.rerun()
    else:
        st.info("Aucune arme équipée pour le moment.")

    st.divider()
    st.markdown("#### ➕ Ajouter une Arme depuis la Base Officielle")
    col_aw1, col_aw2, col_aw3 = st.columns([3, 2, 3])
    with col_aw1:
        weapon_keys = list(db.WEAPONS_DB.keys())
        chosen_w_name = st.selectbox("Choisir l'arme de base", weapon_keys, key="add_weapon_select")
        w_data = db.WEAPONS_DB[chosen_w_name]
        st.caption(f"Dégâts : {w_data['damage']} {w_data['type']} | Finesse : {w_data['finesse']} | Distance : {w_data['ranged']}")
    with col_aw2:
        magic_mod = st.number_input("Bonus magique (+1, +2...)", min_value=0, max_value=5, value=0, key="add_w_magic")
    with col_aw3:
        custom_suffix = st.text_input("Effet spécial additionnel", value="", placeholder="ex: +1d6 feu si critique", key="add_w_desc")

    if st.button("⚔️ Équiper cette arme", use_container_width=False):
        final_name = f"{chosen_w_name} +{magic_mod}" if magic_mod > 0 else chosen_w_name
        char.weapons.append(Weapon(
            name=final_name,
            damage_dice=w_data["damage"],
            damage_type=w_data["type"],
            is_finesse=w_data["finesse"],
            is_ranged=w_data["ranged"],
            magic_bonus=magic_mod,
            extra_damage_desc=custom_suffix
        ))
        st.success(f"{final_name} ajoutée à votre arsenal !")
        st.rerun()

# ------------------------------------------------------------------------------
# ONGLET 2 : INVENTAIRE & BOURSE DE MONNAIES
# ------------------------------------------------------------------------------
with tab_inv:
    st.markdown("### 🎒 Inventaire & Bourse de Monnaies")
    
    # 1. Bourse (Les 5 monnaies officielles D&D 5e)
    st.markdown("#### 🪙 Bourse & Trésor")
    st.caption("Règles officielles de change : 1 PP = 10 PO | 1 PO = 2 PE = 10 PA = 100 PC")
    
    col_v1, col_v2, col_v3 = st.columns([2, 2, 3])
    with col_v1:
        st.metric("💰 Solde Monnaies (en PO)", f"{char.total_currency_po:,.2f} PO".replace(",", " "))
    with col_v2:
        # Calcul de la valeur estimée des gemmes dans l'inventaire (ex: '10 Gemmes (150PO/gemme)')
        import re as _re
        gems_po = 0
        for it_g in char.inventory:
            m_g = _re.search(r"(\d+)\s*po", it_g.name, _re.IGNORECASE)
            if m_g and ("gemme" in it_g.name.lower() or it_g.category == "Trésor / Gemme"):
                gems_po += int(m_g.group(1)) * it_g.quantity
        st.metric("💎 Gemmes & Joyaux en Sac", f"{gems_po:,.0f} PO".replace(",", " ") if gems_po > 0 else "0 PO")
    with col_v3:
        st.caption("Patrimoine total (Pièces + Gemmes) & Poids :")
        st.write(f"👑 **Total : {(char.total_currency_po + gems_po):,.2f} PO** | ⚖️ **{char.total_inventory_weight} kg** transportés".replace(",", " "))

    col_pc, col_pa, col_pe, col_po, col_pp = st.columns(5)
    with col_pc:
        new_pc = st.number_input("🪙 Cuivre (PC)", min_value=0, max_value=100000, value=char.currency.get("pc", 0), step=1, key=f"curr_pc_{w_ver}")
        if new_pc != char.currency.get("pc", 0):
            char.currency["pc"] = new_pc
            st.rerun()
    with col_pa:
        new_pa = st.number_input("🥈 Argent (PA)", min_value=0, max_value=100000, value=char.currency.get("pa", 0), step=1, key=f"curr_pa_{w_ver}")
        if new_pa != char.currency.get("pa", 0):
            char.currency["pa"] = new_pa
            st.rerun()
    with col_pe:
        new_pe = st.number_input("⚡ Électrum (PE)", min_value=0, max_value=100000, value=char.currency.get("pe", 0), step=1, key=f"curr_pe_{w_ver}")
        if new_pe != char.currency.get("pe", 0):
            char.currency["pe"] = new_pe
            st.rerun()
    with col_po:
        new_po = st.number_input("💰 Or (PO)", min_value=0, max_value=100000, value=char.currency.get("po", 0), step=1, key=f"curr_po_{w_ver}")
        if new_po != char.currency.get("po", 0):
            char.currency["po"] = new_po
            st.rerun()
    with col_pp:
        new_pp = st.number_input("💎 Platine (PP)", min_value=0, max_value=100000, value=char.currency.get("pp", 0), step=1, key=f"curr_pp_{w_ver}")
        if new_pp != char.currency.get("pp", 0):
            char.currency["pp"] = new_pp
            st.rerun()

    with st.expander("💸 Transaction Rapide (Ajouter ou Dépenser des Pièces)"):
        t_c1, t_c2, t_c3 = st.columns([2, 2, 2])
        with t_c1:
            t_action = st.radio("Opération", ["Gagner 🟢", "Dépenser 🔴"], horizontal=True)
        with t_c2:
            t_amount = st.number_input("Montant", min_value=1, max_value=50000, value=10, key="quick_t_amount")
        with t_c3:
            t_type = st.selectbox(
                "Type de pièce",
                [("po", "Pièces d'Or (PO)"), ("pa", "Pièces d'Argent (PA)"), ("pc", "Pièces de Cuivre (PC)"), ("pe", "Pièces d'Électrum (PE)"), ("pp", "Pièces de Platine (PP)")],
                format_func=lambda x: x[1],
                key="quick_t_coin"
            )[0]
        if st.button("Valider la transaction", key="btn_apply_transaction"):
            if "Gagner" in t_action:
                char.currency[t_type] = char.currency.get(t_type, 0) + t_amount
                st.success(f"+{t_amount} {t_type.upper()} ajoutés à la bourse !")
            else:
                current = char.currency.get(t_type, 0)
                if current >= t_amount:
                    char.currency[t_type] = current - t_amount
                    st.success(f"-{t_amount} {t_type.upper()} dépensés !")
                else:
                    st.error(f"Fonds insuffisants ! Vous n'avez que {current} {t_type.upper()}.")
            st.rerun()

    st.divider()

    # 2. Objets et équipement
    st.markdown("#### 📦 Objets & Équipements du Sac")
    if char.inventory:
        for idx_item, item in enumerate(char.inventory):
            col_i_info, col_i_qty, col_i_eq, col_i_del = st.columns([6, 2, 2, 1])
            with col_i_info:
                badge_style = "background: #34495e; color: #ecf0f1;"
                if item.category == "Objet magique":
                    badge_style = "background: #8e44ad; color: #fff;"
                elif item.category == "Potion":
                    badge_style = "background: #27ae60; color: #fff;"
                elif item.category == "Vêtements":
                    badge_style = "background: #d35400; color: #fff;"
                
                equipped_badge = " <span style='background:#2980b9; color:#fff; padding:2px 6px; border-radius:3px; font-size:0.75rem;'>ÉQUIPÉ</span>" if item.is_equipped else ""
                
                st.markdown(f"""
                <div style="background: #1c2025; border-left: 3px solid {theme['primary']}; border-radius: 4px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-weight: bold; font-size: 1.05rem; color: #fff;">{item.name} {equipped_badge}</span>
                        <span style="{badge_style} padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; text-transform: uppercase;">{item.category}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #c0b3a0; margin-top: 4px;">
                        ⚖️ Poids unitaire : {item.weight} kg | Poids total : {round(item.weight * item.quantity, 2)} kg
                        {f' — <i>{item.description}</i>' if item.description else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_i_qty:
                q_c1, q_c2 = st.columns(2)
                with q_c1:
                    if st.button("−", key=f"inv_sub_{idx_item}"):
                        if item.quantity > 1:
                            item.quantity -= 1
                        else:
                            char.inventory.pop(idx_item)
                        st.rerun()
                with q_c2:
                    if st.button("➕", key=f"inv_add_{idx_item}"):
                        item.quantity += 1
                        st.rerun()
                st.caption(f"Qté: **{item.quantity}**")
            
            with col_i_eq:
                st.write("")
                eq_label = "Déséquiper" if item.is_equipped else "Équiper"
                if st.button(eq_label, key=f"inv_eq_{idx_item}"):
                    item.is_equipped = not item.is_equipped
                    st.rerun()

            with col_i_del:
                st.write("")
                if st.button("🗑️", key=f"inv_del_{idx_item}", help="Supprimer cet objet"):
                    char.inventory.pop(idx_item)
                    st.rerun()
    else:
        st.info("Aucun objet dans votre sac pour le moment.")

    st.divider()

    # 3. Formulaires d'ajout d'objets
    st.markdown("#### ➕ Ajouter un Objet à l'Inventaire")
    tab_add_db, tab_add_custom = st.tabs(["📚 Depuis le Catalogue Officiel", "✍️ Objet Personnalisé"])
    
    with tab_add_db:
        col_d1, col_d2, col_d3 = st.columns([4, 2, 2])
        with col_d1:
            item_keys = list(db.ITEMS_DB.keys())
            chosen_item_name = st.selectbox("Choisir un objet officiel", item_keys, key="select_db_item")
            item_info = db.ITEMS_DB[chosen_item_name]
            st.caption(f"Catégorie : **{item_info['category']}** | Poids : **{item_info['weight']} kg**")
            st.caption(f"ℹ️ {item_info['desc']}")
        with col_d2:
            chosen_qty = st.number_input("Quantité", min_value=1, max_value=100, value=1, key="db_item_qty")
        with col_d3:
            st.write("")
            st.write("")
            if st.button("📥 Ajouter au Sac", key="btn_add_db_item"):
                existing = next((it for it in char.inventory if it.name == chosen_item_name), None)
                if existing:
                    existing.quantity += chosen_qty
                else:
                    char.inventory.append(Item(
                        name=chosen_item_name,
                        quantity=chosen_qty,
                        category=item_info["category"],
                        weight=item_info["weight"],
                        description=item_info["desc"],
                        is_equipped=False
                    ))
                st.success(f"{chosen_item_name} (x{chosen_qty}) ajouté !")
                st.rerun()

    with tab_add_custom:
        col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
        with col_c1:
            cust_name = st.text_input("Nom de l'objet", placeholder="ex: Cape elfique brodée", key="cust_item_name")
        with col_c2:
            cust_cat = st.selectbox("Catégorie", ["Aventurier", "Objet magique", "Potion", "Vêtements", "Outils", "Instrument", "Trésor / Gemme", "Autre"], key="cust_item_cat")
        with col_c3:
            cust_qty = st.number_input("Quantité", min_value=1, max_value=500, value=1, key="cust_item_qty")
        
        col_c4, col_c5 = st.columns([2, 4])
        with col_c4:
            cust_weight = st.number_input("Poids unitaire (kg)", min_value=0.0, max_value=200.0, value=0.5, step=0.1, key="cust_item_weight")
        with col_c5:
            cust_desc = st.text_input("Description / Propriétés", placeholder="ex: Confère avantage aux jets de discrétion...", key="cust_item_desc")

        if st.button("✨ Créer et Ajouter cet Objet", key="btn_add_cust_item"):
            if cust_name.strip():
                char.inventory.append(Item(
                    name=cust_name.strip(),
                    quantity=cust_qty,
                    category=cust_cat,
                    weight=cust_weight,
                    description=cust_desc.strip(),
                    is_equipped=False
                ))
                st.success(f"Objet « {cust_name} » ajouté à l'inventaire !")
                st.rerun()
            else:
                st.warning("Veuillez renseigner un nom pour l'objet.")


# ------------------------------------------------------------------------------
# ONGLET 2 : GRIMOIRE & SORTS
# ------------------------------------------------------------------------------
with tab_grimoire:
    st.markdown("### 🔮 Grimoire & Magie")

    # 0. En-tête d'Incantation (Caractéristique, DD de Sauvegarde, Bonus d'attaque de sort, Sorts à préparer)
    sc_stats = db.get_spellcasting_stats(char.classes, char.raw_abilities, char.proficiency_bonus)
    if sc_stats.get("has_spellcasting"):
        sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
        mod_sign = f"+{sc_stats['ability_mod']}" if sc_stats["ability_mod"] >= 0 else f"{sc_stats['ability_mod']}"
        atk_sign = f"+{sc_stats['attack_bonus']}" if sc_stats["attack_bonus"] >= 0 else f"{sc_stats['attack_bonus']}"
        with sc_col1:
            st.markdown(f"""<div class="metric-shield"><div class="metric-value" style="font-size:1.35rem;">{sc_stats['caster_class']} ({sc_stats['ability_name']} {mod_sign})</div><div class="metric-label">Caractéristique d'Incantation</div></div>""", unsafe_allow_html=True)
        with sc_col2:
            st.markdown(f"""<div class="metric-shield"><div class="metric-value">🛡️ {sc_stats['save_dc']}</div><div class="metric-label">DD Sauvegarde des Sorts</div></div>""", unsafe_allow_html=True)
        with sc_col3:
            st.markdown(f"""<div class="metric-shield"><div class="metric-value">🎯 {atk_sign}</div><div class="metric-label">Bonus d'Attaque de Sort</div></div>""", unsafe_allow_html=True)
        with sc_col4:
            st.markdown(f"""<div class="metric-shield"><div class="metric-value">📖 {sc_stats['prepared_count']}</div><div class="metric-label">Sorts à Préparer</div></div>""", unsafe_allow_html=True)
        st.write("")

    # 1. Emplacements de sorts
    slots_max = db.calculate_spell_slots(char.classes)
    pact_slots_cnt, pact_slots_lvl = db.calculate_pact_slots(char.classes)

    st.markdown("#### 🌟 Emplacements de Sorts Disponibles")
    if slots_max or pact_slots_cnt > 0:
        if slots_max:
            for lvl, total_slots in slots_max.items():
                used_slots = char.spell_slots_used.get(lvl, 0)
                avail = max(0, total_slots - used_slots)
                
                col_sl1, col_sl2, col_sl3 = st.columns([3, 4, 3])
                with col_sl1:
                    st.write(f"**Niveau {lvl}** : `{avail} / {total_slots} disponibles`")
                with col_sl2:
                    pills = "🟢 " * avail + "🔴 " * used_slots
                    st.write(pills)
                with col_sl3:
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("−1 Dépenser", key=f"use_slot_{lvl}", disabled=(avail <= 0)):
                            char.spell_slots_used[lvl] = used_slots + 1
                            st.rerun()
                    with c_btn2:
                        if st.button("+1 Rendre", key=f"rest_slot_{lvl}", disabled=(used_slots <= 0)):
                            char.spell_slots_used[lvl] = max(0, used_slots - 1)
                            st.rerun()

        if pact_slots_cnt > 0:
            st.divider()
            st.markdown(f"##### 👁️ Magie de Pacte (Occultiste - Niveau {pact_slots_lvl})")
            avail_pact = max(0, pact_slots_cnt - char.pact_slots_used)
            col_p1, col_p2, col_p3 = st.columns([3, 4, 3])
            with col_p1:
                st.write(f"**Slots de Pacte** : `{avail_pact} / {pact_slots_cnt} disponibles`")
            with col_p2:
                st.write("🟢 " * avail_pact + "🔴 " * char.pact_slots_used)
            with col_p3:
                p_c1, p_c2 = st.columns(2)
                with p_c1:
                    if st.button("−1 Slot Pacte", key="use_pact_slot", disabled=(avail_pact <= 0)):
                        char.pact_slots_used += 1
                        st.rerun()
                with p_c2:
                    if st.button("+1 Slot Pacte", key="rest_pact_slot", disabled=(char.pact_slots_used <= 0)):
                        char.pact_slots_used = max(0, char.pact_slots_used - 1)
                        st.rerun()
    else:
        st.info("Ce personnage ne dispose pas d'emplacements de sorts de classe.")

    st.divider()

    # 2. Sorts connus dans le grimoire
    st.markdown("#### 📖 Sorts Connus dans votre Grimoire")
    if char.known_spells:
        for s_idx, sp in enumerate(char.known_spells):
            col_sp_card, col_sp_act = st.columns([7, 3])
            
            # Détermination des niveaux d'emplacements utilisables
            available_cast_levels = []
            if sp.level > 0:
                # Niveaux d'emplacements standards disponibles
                for lvl_cand in sorted(slots_max.keys()):
                    if lvl_cand >= sp.level:
                        avail_cnt = slots_max[lvl_cand] - char.spell_slots_used.get(lvl_cand, 0)
                        available_cast_levels.append((lvl_cand, "standard", avail_cnt))
                # Magie de Pacte (Occultiste)
                if pact_slots_cnt > 0 and pact_slots_lvl >= sp.level:
                    avail_pact_cnt = pact_slots_cnt - char.pact_slots_used
                    available_cast_levels.append((pact_slots_lvl, "pacte", avail_pact_cnt))

            with col_sp_act:
                st.write("")
                selected_cast_lvl = sp.level
                selected_slot_type = "standard"
                can_cast = False

                if sp.level == 0:
                    st.caption("✨ Tour de magie (Illimité)")
                    if st.button(f"✨ Lancer {sp.name}", key=f"cast_{s_idx}", use_container_width=True):
                        st.success(f"Tour de magie {sp.name} incanté !")
                else:
                    if available_cast_levels:
                        # Sélecteur de niveau d'emplacement pour le lancer (Upcasting)
                        slot_options = []
                        for lvl_c, s_type, cnt in available_cast_levels:
                            type_label = "Pacte" if s_type == "pacte" else "Standard"
                            slot_options.append((lvl_c, s_type, f"Niveau {lvl_c} ({type_label} : {cnt} dispo)"))

                        chosen_tuple = st.selectbox(
                            "Emplacement utilisé :",
                            slot_options,
                            format_func=lambda x: x[2],
                            key=f"slot_choice_{s_idx}"
                        )
                        selected_cast_lvl = chosen_tuple[0]
                        selected_slot_type = chosen_tuple[1]
                        
                        # Vérifier s'il reste des emplacements de ce type
                        if selected_slot_type == "standard":
                            avail_slots_now = slots_max.get(selected_cast_lvl, 0) - char.spell_slots_used.get(selected_cast_lvl, 0)
                        else:
                            avail_slots_now = pact_slots_cnt - char.pact_slots_used
                        can_cast = (avail_slots_now > 0)

                        if st.button(f"✨ Lancer (Niv {selected_cast_lvl})", key=f"cast_{s_idx}", disabled=not can_cast, use_container_width=True):
                            if selected_slot_type == "standard":
                                char.spell_slots_used[selected_cast_lvl] = char.spell_slots_used.get(selected_cast_lvl, 0) + 1
                            else:
                                char.pact_slots_used += 1
                            st.success(f"Sort {sp.name} lancé avec succès avec un emplacement de Niveau {selected_cast_lvl} !")
                            st.rerun()
                    else:
                        st.caption("🔒 Aucun emplacement de niveau suffisant")

                if st.button("🗑️ Oublier ce sort", key=f"del_spell_{s_idx}", use_container_width=True):
                    char.known_spells.pop(s_idx)
                    st.rerun()

            with col_sp_card:
                # Description dynamique avec upcasting selon l'emplacement sélectionné
                dyn_desc, is_upcast = db.get_dynamic_spell_description(sp.name, selected_cast_lvl)
                conc_badge = "🧠 [Concentration]" if sp.concentration else ""
                upcast_badge = f"<span style='background: #e67e22; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.82rem; font-weight: bold;'>🚀 Amplifié au Niveau {selected_cast_lvl}</span>" if is_upcast else ""

                st.markdown(f"""
                <div class="card-combat">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.15rem; font-weight: bold; color: {theme['accent']};">{sp.name} {upcast_badge}</span>
                        <span style="font-size: 0.9rem; color: #d4af37;">Base : Niv {sp.level} • {sp.school} {conc_badge}</span>
                    </div>
                    <div style="color: #b5a895; font-size: 0.95rem; margin-top: 4px;">
                        ⏱️ <b>Incantation :</b> {sp.casting_time} | 📏 <b>Portée :</b> {sp.range_area} | ⏳ <b>Durée :</b> {sp.duration}
                    </div>
                    <div style="color: #e0d5c1; margin-top: 6px; font-size: 1.02rem; line-height: 1.45;">
                        {dyn_desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Aucun sort dans votre grimoire pour le moment.")

    st.divider()

    # 3. Ajouter un sort depuis le catalogue
    st.markdown("#### ➕ Apprendre un Sort (Catalogue Officiel)")
    spell_keys = list(db.SPELLS_DB.keys())
    col_as1, col_as2 = st.columns([3, 1])
    with col_as1:
        chosen_sp_name = st.selectbox("Choisir un sort dans le catalogue", spell_keys, key="add_spell_select")
        sp_meta = db.SPELLS_DB[chosen_sp_name]
        st.caption(f"Niveau : {sp_meta['level']} | École : {sp_meta['school']} | Incantation : {sp_meta['time']} | Portée : {sp_meta['range']} | {sp_meta['desc']}")
    with col_as2:
        st.write("")
        st.write("")
        if st.button("📖 Ajouter au Grimoire", use_container_width=True):
            char.known_spells.append(Spell(
                name=chosen_sp_name,
                level=sp_meta["level"],
                school=sp_meta["school"],
                casting_time=sp_meta["time"],
                range_area=sp_meta["range"],
                duration="1 heure" if sp_meta.get("conc") else "Instantanée",
                concentration=sp_meta.get("conc", False),
                description=sp_meta["desc"]
            ))
            st.success(f"Sort {chosen_sp_name} appris !")
            st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 3 : APTITUDES DE CLASSE & DONS
# ------------------------------------------------------------------------------
with tab_traits:
    st.markdown("### ✨ Aptitudes de Classe & Capacités Spéciales")
    st.caption("Aptitudes calculées et mises à l'échelle dynamiquement selon vos niveaux dans chaque classe.")

    col_btn_sync, col_space = st.columns([4, 6])
    with col_btn_sync:
        if st.button("🔄 Synchroniser les aptitudes selon mes niveaux et sous-classes", use_container_width=True):
            updated_f, added_f = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
            char.traits_and_features = updated_f
            if added_f:
                st.success(f"Aptitudes synchronisées ! Nouvelles aptitudes ajoutées : {', '.join(added_f)}")
            else:
                st.info("Toutes les aptitudes officielles correspondant à vos niveaux sont déjà présentes !")
            st.rerun()

    st.write("")

    if char.traits_and_features:
        for t_idx, tr_name in enumerate(char.traits_and_features):
            # Calcul dynamique de l'aptitude selon les niveaux de classe
            feature_info = db.get_dynamic_feature_info(tr_name, char.classes)

            with st.expander(f"🌟 **{feature_info['title']}**", expanded=True):
                st.markdown(f"🏷️ **Source :** `{feature_info['source']}` | ⚡ **Type d'action :** `{feature_info['type']}`")
                st.markdown(f"""
                <div style='background: rgba(0,0,0,0.3); padding: 12px 16px; border-radius: 6px; border-left: 4px solid {theme['accent']}; font-size: 1.05rem; line-height: 1.5; color: #e8dcc6;'>
                    {feature_info['desc']}
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("🗑️ Retirer cette aptitude", key=f"del_feat_{t_idx}"):
                    char.traits_and_features.pop(t_idx)
                    st.rerun()
    else:
        st.info("Aucune aptitude enregistrée.")

    st.divider()

    # Ajouter une aptitude
    st.markdown("#### ➕ Ajouter une Aptitude depuis le Compendium")
    col_af1, col_af2 = st.columns([3, 1])
    with col_af1:
        db_feats = list(db.FEATURES_DB.keys())
        chosen_feat = st.selectbox("Sélectionner dans le catalogue", db_feats, key="select_feature_add")
        f_info = db.FEATURES_DB[chosen_feat]
        st.caption(f"Source : {f_info['source']} | Type : {f_info['type']}")
    with col_af2:
        st.write("")
        st.write("")
        if st.button("✨ Ajouter Aptitude", key="btn_add_feat", use_container_width=True):
            if chosen_feat not in char.traits_and_features:
                char.traits_and_features.append(chosen_feat)
                st.success(f"{chosen_feat} ajoutée !")
                st.rerun()

    # Aptitude personnalisée
    with st.expander("Créer une aptitude personnalisée sur-mesure"):
        custom_f_name = st.text_input("Nom de l'aptitude")
        custom_f_source = st.text_input("Source", value="Personnalisée")
        custom_f_type = st.text_input("Type", value="Action / Spécial")
        custom_f_desc = st.text_area("Descriptif complet")
        if st.button("Enregistrer cette aptitude sur-mesure"):
            if custom_f_name:
                char.traits_and_features.append(custom_f_name)
                db.FEATURES_DB[custom_f_name] = {
                    "source": custom_f_source,
                    "type": custom_f_type,
                    "desc": custom_f_desc
                }
                st.success(f"Aptitude {custom_f_name} créée et ajoutée !")
                st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 5 : COMPÉTENCES & SAUVEGARDES
# ------------------------------------------------------------------------------
with tab_skills:
    st.markdown("### 📜 Maîtrises, Compétences & Sauvegardes")
    
    col_sk_left, col_sk_right = st.columns([6, 4])

    with col_sk_left:
        st.markdown("#### 🎯 Compétences")
        data_skills = []
        for sk_name, ab in SKILL_ABILITY_MAP.items():
            mod = char.get_skill_modifier(sk_name)
            is_exp = sk_name in char.skill_expertises
            is_prof = sk_name in char.skill_proficiencies
            badge = "⭐ Expertise (x2)" if is_exp else ("✅ Maîtrisé" if is_prof else "—")
            data_skills.append({
                "Compétence": sk_name,
                "Carac": ab.name,
                "Bonus": f"+{mod}" if mod >= 0 else f"{mod}",
                "Statut": badge
            })
        df_skills = pd.DataFrame(data_skills)
        st.dataframe(df_skills, hide_index=True, use_container_width=True, height=520)

        max_exp_tab = db.get_max_expertises_count(char.classes)
        exp_label_info = f" (Droit de classe : {max_exp_tab} Expertises)" if max_exp_tab > 0 else ""
        with st.expander(f"⚙️ Modifier mes Compétences Maîtrisées & Expertises{exp_label_info}", expanded=True):
            all_skill_names = list(SKILL_ABILITY_MAP.keys())
            new_profs = st.multiselect(
                f"Compétences maîtrisées (+{char.proficiency_bonus})",
                options=all_skill_names,
                default=[s for s in char.skill_proficiencies if s in all_skill_names],
                key=f"edit_skill_profs_{w_ver}"
            )
            new_exps = st.multiselect(
                f"⭐ Expertises (+{char.proficiency_bonus * 2} au lieu de +{char.proficiency_bonus}){exp_label_info}",
                options=all_skill_names,
                default=[s for s in char.skill_expertises if s in all_skill_names],
                key=f"edit_skill_exps_{w_ver}"
            )
            if st.button("Enregistrer les compétences & expertises", key="btn_save_skills"):
                char.skill_proficiencies = list(dict.fromkeys(new_profs + new_exps))
                char.skill_expertises = new_exps
                sync_session_state_from_char(char)
                st.rerun()

    with col_sk_right:
        st.markdown("#### 🛡️ Jets de Sauvegarde")
        for ab in Ability:
            st_mod = char.get_saving_throw(ab)
            is_prof = any((p == ab or (hasattr(p, "name") and p.name == ab.name)) for p in char.saving_throw_proficiencies)
            mark = "🛡️ **Maîtrisé**" if is_prof else "—"
            st_val = f"+{st_mod}" if st_mod >= 0 else f"{st_mod}"
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span><b>{ab.value}</b> ({ab.name})</span>
                <span style="color: {theme['accent']}; font-weight: bold; font-size: 1.15rem;">{st_val} <small style="color: #aaa;">| {mark}</small></span>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("⚙️ Modifier les Jets de Sauvegarde Maîtrisés"):
            all_abs = list(Ability)
            default_abs = [a for a in all_abs if any((p == a or (hasattr(p, "name") and p.name == a.name)) for p in char.saving_throw_proficiencies)]
            new_st = st.multiselect(
                "Sauvegardes maîtrisées",
                options=all_abs,
                default=default_abs,
                format_func=lambda a: f"{a.value} ({a.name})",
                key=f"edit_save_profs_{w_ver}"
            )
            if st.button("Enregistrer les sauvegardes", key="btn_save_st"):
                char.saving_throw_proficiencies = new_st
                sync_session_state_from_char(char)
                st.rerun()

        st.divider()
        st.markdown("#### 🗣️ Autres Maîtrises & Langues")
        new_lang_prof = st.text_area(
            "Langues parlées, maîtrises d'armures, armes, outils et instruments",
            value=char.languages_and_proficiencies,
            height=160,
            placeholder="Ex: Langues : Commun, Elfique, Sylvain...\nMaîtrises : Armures légères, Arcs, Outils de voleur..."
        )
        if new_lang_prof != char.languages_and_proficiencies:
            char.languages_and_proficiencies = new_lang_prof
            st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 6 : HISTOIRE, RP, APPARENCE & DÉTAILS (PAGES 1 & 2 DU PDF)
# ------------------------------------------------------------------------------
with tab_lore:
    st.markdown("### 📖 Profil Roleplay, Apparence, Histoire & Trésors")
    st.caption("Retrouvez et éditez ici toutes les informations de rôle, d'apparence, d'alliés et de lore issues des Pages 1 et 2 de votre fiche.")

    # 1. Caractéristiques physiques (Page 2)
    st.markdown("#### 👤 Caractéristiques Physiques")
    p_c1, p_c2, p_c3, p_c4, p_c5, p_c6 = st.columns(6)
    with p_c1:
        char.age = st.text_input("Âge", value=char.age, placeholder="ex: 250 ans")
    with p_c2:
        char.height = st.text_input("Taille", value=char.height, placeholder="ex: 1m73")
    with p_c3:
        char.weight = st.text_input("Poids", value=char.weight, placeholder="ex: 60 kg")
    with p_c4:
        char.eyes = st.text_input("Yeux", value=char.eyes, placeholder="ex: Gris")
    with p_c5:
        char.skin = st.text_input("Peau", value=char.skin, placeholder="ex: Pâle")
    with p_c6:
        char.hair = st.text_input("Cheveux", value=char.hair, placeholder="ex: Gris-Argent")

    st.divider()

    # 2. Personnalité, Idéaux, Liens, Défauts (Page 1)
    st.markdown("#### 🎭 Personnalité & Psychologie")
    rp_c1, rp_c2 = st.columns(2)
    with rp_c1:
        char.personality_traits = st.text_area("Traits de Personnalité", value=char.personality_traits, height=120)
        char.bonds = st.text_area("Liens", value=char.bonds, height=110)
    with rp_c2:
        char.ideals = st.text_area("Idéaux", value=char.ideals, height=120)
        char.flaws = st.text_area("Défauts", value=char.flaws, height=110)

    st.divider()

    # 3. Apparence & Alliés / Organisations (Page 2)
    col_app, col_allies = st.columns(2)
    with col_app:
        st.markdown("#### 🪞 Apparence du Personnage")
        char.appearance = st.text_area("Description visuelle", value=char.appearance, height=160)
    with col_allies:
        st.markdown("#### 🤝 Alliés & Organisations")
        char.allies = st.text_area("Factions, compagnons et contacts", value=char.allies, height=160)

    st.divider()

    # 4. Histoire du personnage (Backstory) & Trésors spéciaux (Page 2)
    col_back, col_treas = st.columns([6, 4])
    with col_back:
        st.markdown("#### 📜 Histoire du Personnage (Backstory)")
        char.backstory = st.text_area("Récit complet de vos origines et aventures", value=char.backstory, height=340)
    with col_treas:
        st.markdown("#### 💎 Trésors & Objets Harmonisés (Détails)")
        char.treasure_notes = st.text_area("Propriétés détaillées des reliques et objets magiques", value=char.treasure_notes, height=160)
        st.markdown("#### 🌿 Notes d'Aptitudes & Capacités Supplémentaires")
        char.additional_features_notes = st.text_area("Notes complètes issues du PDF", value=char.additional_features_notes, height=145)


# ==============================================================================
# 10. PIED DE PAGE
# ==============================================================================
st.write("")
st.write("---")
st.caption(f"Chronique du Héros D&D 5e • Conçu pour **{char.name}** • Règles officielles D&D 5e SRD & Extensions en Français")

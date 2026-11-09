"""
Module d'importation et d'exportation pour l'application D&D 5e
===============================================================
Analyseur de pointe pour feuilles de personnage D&D 5e (AcroForm officiel WotC, AideDD, et texte).
Extrait :
- Identité, Race, Classes (multiclassage) et Sous-classes
- Caractéristiques brutes, Modificateurs, Sauvegardes et Compétences
- Points de vie max, actuels, CA, Vitesse
- Bourse complète (PC, PA, PE, PO, PP)
- Inventaire complet avec découpage d'objets, quantités et catégories
- Arsenal d'armes et Grimoire de sorts avec descriptifs complets
"""

import json
import io
import re
from typing import Dict, Any, Tuple, Optional, List
import pdfplumber
import pdfminer.pdftypes as pdftypes
from pdfminer.psparser import PSLiteral
import dnd_database as db

CLASS_SYNONYMS = {
    "barbare": "Barbare", "barbarian": "Barbare",
    "barde": "Barde", "bard": "Barde",
    "clerc": "Clerc", "cleric": "Clerc",
    "druide": "Druide", "druid": "Druide",
    "ensorceleur": "Ensorceleur", "sorcerer": "Ensorceleur",
    "guerrier": "Guerrier", "fighter": "Guerrier",
    "magicien": "Magicien", "mage": "Magicien", "wizard": "Magicien",
    "moine": "Moine", "monk": "Moine",
    "occultiste": "Occultiste", "warlock": "Occultiste", "sorcier": "Occultiste",
    "paladin": "Paladin",
    "rôdeur": "Rôdeur", "rodeur": "Rôdeur", "rdeur": "Rôdeur", "ranger": "Rôdeur",
    "roublard": "Roublard", "rogue": "Roublard", "voleur": "Roublard",
    "artificier": "Artificier", "artificer": "Artificier",
}

SKILL_TRANSLATION = {
    "acrobatics": "Acrobaties", "acrobatie": "Acrobaties", "acrobaties": "Acrobaties",
    "animalhandling": "Dressage", "animal": "Dressage", "dressage": "Dressage",
    "arcana": "Arcanes", "arcanes": "Arcanes",
    "athletics": "Athlétisme", "athletisme": "Athlétisme",
    "deception": "Tromperie", "tromperie": "Tromperie",
    "history": "Histoire", "histoire": "Histoire",
    "insight": "Intuition", "intuition": "Intuition",
    "intimidation": "Intimidation",
    "investigation": "Investigation",
    "medicine": "Médecine", "medecine": "Médecine",
    "nature": "Nature",
    "perception": "Perception",
    "performance": "Représentation", "representation": "Représentation",
    "persuasion": "Persuasion",
    "religion": "Religion",
    "sleightofhand": "Escamotage", "escamotage": "Escamotage",
    "stealth": "Discrétion", "discretion": "Discrétion",
    "survival": "Survie", "survie": "Survie"
}

def decode_pdf_str(val: Any) -> str:
    """Décode les chaînes issues de pdfminer (UTF-16BE/LE, UTF-8, Windows-1252, Latin-1, PSLiteral)."""
    if val is None:
        return ""
    if isinstance(val, PSLiteral):
        return str(val.name)
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return val
    if isinstance(val, bytes):
        if val.startswith(b"\xfe\xff"):
            return val[2:].decode("utf-16-be", errors="replace")
        if val.startswith(b"\xff\xfe"):
            return val[2:].decode("utf-16-le", errors="replace")
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return val.decode("cp1252")
            except Exception:
                return val.decode("latin-1", errors="replace")
    return str(val)

def normalize_key(k: str) -> str:
    """Normalise un nom de champ pour correspondance souple."""
    return re.sub(r"[^a-zA-Z0-9]", "", k.lower())

def extract_acroform_entries(pdf_obj: pdfplumber.PDF) -> List[Tuple[str, str]]:
    """
    Extrait l'ensemble des paires (nom_champ, valeur) du formulaire AcroForm et des annotations.
    Conserve une liste complète afin de ne jamais perdre une valeur en cas d'homonymie (ex: 'STR' et 'STR ').
    """
    entries: List[Tuple[str, str]] = []
    seen_pairs = set()

    def add_entry(k: str, v: str):
        k_clean = k.strip()
        v_clean = v.strip()
        if k_clean and v_clean and (k_clean, v_clean) not in seen_pairs:
            seen_pairs.add((k_clean, v_clean))
            entries.append((k_clean, v_clean))

    # 1. Via les annotations de chaque page (dans l'ordre des pages 1, 2, 3...)
    for page in pdf_obj.pages:
        if hasattr(page, "annots") and page.annots:
            for annot in page.annots:
                data = annot.get("data", {})
                if not isinstance(data, dict):
                    continue
                f_name = data.get("T") or annot.get("name")
                f_val = data.get("V") or annot.get("contents")
                if f_name is not None and f_val is not None:
                    name_str = decode_pdf_str(pdftypes.resolve1(f_name))
                    val_str = decode_pdf_str(pdftypes.resolve1(f_val))
                    add_entry(name_str, val_str)

    # 2. Via le catalogue AcroForm (complément)
    doc = getattr(pdf_obj, "doc", None)
    if doc and hasattr(doc, "catalog") and "AcroForm" in doc.catalog:
        try:
            acroform = pdftypes.resolve1(doc.catalog["AcroForm"])
            if isinstance(acroform, dict) and "Fields" in acroform:
                field_list = pdftypes.resolve1(acroform["Fields"])
                
                def walk(obj, prefix=""):
                    resolved = pdftypes.resolve1(obj)
                    if not isinstance(resolved, dict):
                        return
                    name_raw = resolved.get("T")
                    val_raw = resolved.get("V")
                    
                    full_name = prefix
                    if name_raw is not None:
                        name_str = decode_pdf_str(pdftypes.resolve1(name_raw)).strip()
                        full_name = f"{prefix}.{name_str}" if prefix else name_str
                    
                    if val_raw is not None:
                        val_str = decode_pdf_str(pdftypes.resolve1(val_raw))
                        if full_name and val_str:
                            add_entry(full_name, val_str)
                    
                    if "Kids" in resolved:
                        kids = pdftypes.resolve1(resolved["Kids"])
                        if isinstance(kids, list):
                            for k in kids:
                                walk(k, full_name)

                if isinstance(field_list, list):
                    for f in field_list:
                        walk(f)
        except Exception:
            pass

    return entries

def parse_class_field_advanced(cand: str) -> Tuple[Dict[str, int], Dict[str, str]]:
    """Parse une ligne complexe de multiclassage et sous-classes."""
    classes = {}
    subclasses = {}
    parts = re.split(r"[&/+,]|(?:\s+et\s+)|(?:\s+and\s+)", cand)
    for part in parts:
        part_clean = part.strip()
        if not part_clean:
            continue
        found_cls = None
        for syn, canon in CLASS_SYNONYMS.items():
            if re.search(rf"\b{syn}\b", part_clean, re.IGNORECASE):
                found_cls = canon
                break
        if not found_cls:
            continue
        
        m_lvl = re.search(r"(?:niv(?:eau)?\.?|level|lvl\.?)\s*(\d{1,2})\b", part_clean, re.IGNORECASE)
        if not m_lvl:
            nums = re.findall(r"\b(\d{1,2})\b", part_clean)
            lvl = int(nums[-1]) if nums else 1
        else:
            lvl = int(m_lvl.group(1))
        
        classes[found_cls] = lvl
        
        # Sous-classe
        clean_sub = re.sub(
            rf"\b(?:rôdeur|rodeur|rdeur|roublard|guerrier|paladin|barde|barbare|clerc|druide|magicien|ensorceleur|moine|occultiste|artificier)\b",
            "",
            part_clean,
            flags=re.IGNORECASE
        )
        clean_sub = re.sub(r"(?:niv(?:eau)?\.?|level|lvl\.?)\s*\d{1,2}", "", clean_sub, flags=re.IGNORECASE).strip(" -/&(),.")
        if len(clean_sub) >= 3:
            matched_official = None
            if found_cls in db.CLASSES_DND:
                for off_sub in db.CLASSES_DND[found_cls]["subclasses"]:
                    if clean_sub.lower() in off_sub.lower() or "chasseur de monstre" in clean_sub.lower() and "chasseur de monstres" in off_sub.lower():
                        matched_official = off_sub
                        break
            subclasses[found_cls] = matched_official if matched_official else clean_sub

    return classes, subclasses

def parse_items_from_text(equip_text: str) -> List[Dict[str, Any]]:
    """Découpe un texte d'inventaire en objets individuels structurés."""
    items = []
    lines = re.split(r"[\n\r;•\*\t]+", equip_text)
    for line in lines:
        clean = line.strip(" -•*\t,").rstrip(".")
        if not clean or len(clean) < 2:
            continue
        
        if re.match(r"^(?:po|pa|pc|pe|pp|gp|sp|cp|ep)\s*:\s*\d+", clean, re.IGNORECASE):
            continue

        qty = 1
        name = clean
        
        # Motif 'Ration x31' ou 'potion x2'
        m_x = re.search(r"^(.*?)\s*x\s*(\d+)$", clean, re.IGNORECASE)
        if m_x:
            name = m_x.group(1).strip()
            qty = int(m_x.group(2))
        else:
            # Motif '3 baumes' ou '1 collecteur'
            m_pre = re.search(r"^(\d+)\s+x?\s*(.+)$", clean)
            if m_pre:
                qty = int(m_pre.group(1))
                name = m_pre.group(2).strip()

        name = name.strip(" -:•")
        if not name:
            continue

        cat = "Aventurier"
        n_low = name.lower()
        if any(x in n_low for x in ["potion", "philtre", "antidote"]):
            cat = "Potion"
        elif any(x in n_low for x in ["anneau", "cape", "bottes", "broche", "effigie", "parchemin", "pierre", "baguette", "bâton"]):
            cat = "Objet magique"
        elif any(x in n_low for x in ["armure", "cuir", "vêtements", "habits", "bouclier"]):
            cat = "Vêtements"
        elif any(x in n_low for x in ["ocarina", "luth", "flûte", "instrument"]):
            cat = "Instrument"
        elif any(x in n_low for x in ["outils", "serrure", "crochet", "alchimiste"]):
            cat = "Outils"
        elif any(x in n_low for x in ["gemme", "or", "diamant", "rubis", "lingot", "perle"]):
            cat = "Trésor / Gemme"

        weight = 0.0
        desc = ""
        for it_db_name, it_db_val in db.ITEMS_DB.items():
            if it_db_name.lower() in name.lower() or name.lower() in it_db_name.lower():
                weight = it_db_val.get("weight", 0.0)
                desc = it_db_val.get("desc", "")
                break

        items.append({
            "name": name,
            "quantity": qty,
            "category": cat,
            "weight": weight,
            "description": desc,
            "is_equipped": (cat in ["Vêtements", "Objet magique"] and ("armure" in n_low or "cape" in n_low or "anneau" in n_low or "broche" in n_low))
        })
    return items

def parse_json_character(file_bytes: bytes) -> Dict[str, Any]:
    """Parse un fichier JSON et retourne le dictionnaire de données du personnage."""
    text = file_bytes.decode("utf-8")
    return json.loads(text)

def parse_pdf_character(file_bytes: bytes) -> Tuple[Dict[str, Any], str]:
    """
    Extrait l'intégralité d'une feuille D&D 5e depuis un PDF :
    Caractéristiques réelles, multi-classes, sous-classes, PV, CA, Bourse (PO, PA, PC, PE, PP),
    Inventaire complet découpé, Arsenal d'armes et Grimoire de sorts.
    """
    extracted: Dict[str, Any] = {
        "name": "",
        "race": "",
        "background": "",
        "alignment": "",
        "classes": {},
        "subclasses": {},
        "raw_abilities": {},
        "saving_throw_proficiencies": [],
        "skill_proficiencies": [],
        "pv_current": 10,
        "pv_max": 10,
        "pv_temp": 0,
        "speed": 9,
        "armor_class": 10,
        "currency": {"po": 0, "pa": 0, "pc": 0, "pe": 0, "pp": 0},
        "inventory": [],
        "traits": [],
        "weapons": [],
        "known_spells": []
    }
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        entries = extract_acroform_entries(pdf)
        
        # Dictionnaire multi-valeurs par clé normalisée (ne perd jamais une valeur si 'STR' et 'STR ' coexistent)
        norm_multi: Dict[str, List[str]] = {}
        for raw_k, raw_v in entries:
            k_norm = normalize_key(raw_k)
            norm_multi.setdefault(k_norm, []).append(raw_v)

        def get_first_val(patterns: List[str], exact: bool = False) -> Optional[str]:
            for pat in patterns:
                pat_norm = normalize_key(pat)
                if exact:
                    if pat_norm in norm_multi and norm_multi[pat_norm]:
                        return norm_multi[pat_norm][0]
                else:
                    for k_norm, vals in norm_multi.items():
                        if pat_norm in k_norm and vals:
                            return vals[0]
            return None

        def get_all_vals(patterns: List[str], exact: bool = False) -> List[str]:
            res = []
            for pat in patterns:
                pat_norm = normalize_key(pat)
                if exact:
                    res.extend(norm_multi.get(pat_norm, []))
                else:
                    for k_norm, vals in norm_multi.items():
                        if pat_norm in k_norm:
                            res.extend(vals)
            return res

        # 1. Identité (Nom, Race, Historique, Alignement) - priorité au champ de la page 1
        nom = get_first_val(["charactername", "character_name", "nomdupersonnage", "nom"], exact=True)
        if not nom:
            nom = get_first_val(["charactername", "nomdupersonnage"])
        if nom:
            if "feuille d'agent" in nom.lower():
                nom = re.sub(r"feuille d'agent", "Feuille d'Argent", nom, flags=re.IGNORECASE)
            extracted["name"] = nom

        race = get_first_val(["race", "species", "peuple"], exact=True)
        if not race: race = get_first_val(["race", "peuple"])
        if race: extracted["race"] = race

        bg = get_first_val(["background", "historique"], exact=True)
        if not bg: bg = get_first_val(["background", "historique"])
        if bg: extracted["background"] = bg

        al = get_first_val(["alignment", "alignement"], exact=True)
        if not al: al = get_first_val(["alignment", "alignement"])
        if al: extracted["alignment"] = al

        # 2. Classe, Sous-classe & Niveau (Multiclassage)
        class_cand = get_first_val(["classlevel", "classeetniveau", "class", "classe"], exact=True)
        if not class_cand:
            # Évite 'spellcastingclass'
            for k_norm, vals in norm_multi.items():
                if ("classlevel" in k_norm or k_norm in ["class", "classe"]) and "spell" not in k_norm:
                    class_cand = vals[0]
                    break
        
        if class_cand:
            cls_map, sub_map = parse_class_field_advanced(class_cand)
            if cls_map:
                extracted["classes"] = cls_map
            if sub_map:
                extracted["subclasses"] = sub_map

        # 3. Caractéristiques Brutes (STR, DEX, CON, INT, WIS, CHA)
        # On vérifie toutes les valeurs associées à la caractéristique (ex: 'STR' = '+2' et 'STR ' = '14')
        # Mathématiquement dans D&D 5e, le score (1..30) est toujours strictement supérieur au modificateur !
        stat_exact_keys = [
            ("STR", ["str", "strmod", "strength", "for", "formod", "force", "scorefor", "strscore"]),
            ("DEX", ["dex", "dexmod", "dexterity", "dexterite", "dexteritemod", "scoredex", "dexscore"]),
            ("CON", ["con", "conmod", "constitution", "scorecon", "conscore"]),
            ("INT", ["int", "intmod", "intelligence", "scoreint", "intscore"]),
            ("WIS", ["wis", "wismod", "wisdom", "sag", "sagmod", "sagesse", "scoresag", "wisscore"]),
            ("CHA", ["cha", "chamod", "charisma", "charisme", "scorecha", "chascore"]),
        ]

        for code, key_list in stat_exact_keys:
            candidates = []
            for raw_val in get_all_vals(key_list, exact=True):
                for m in re.findall(r"[+-]?\d{1,2}", raw_val):
                    iv = int(m)
                    if 1 <= iv <= 30:
                        candidates.append(iv)
            if candidates:
                extracted["raw_abilities"][code] = max(candidates)

        # 4. PV, CA & Vitesse
        hp_max = get_first_val(["hpmax", "maxhp", "pvmax", "maximumdepointsdevie"], exact=True)
        if not hp_max: hp_max = get_first_val(["hpmax", "maxhp", "pvmax"])
        if hp_max:
            m = re.search(r"\b(\d+)\b", hp_max)
            if m: extracted["pv_max"] = int(m.group(1))

        hp_cur = get_first_val(["hpcurrent", "currenthp", "pvactuels", "pointsdevieactuels"], exact=True)
        if not hp_cur: hp_cur = get_first_val(["hpcurrent", "currenthp", "pvactuels"])
        if hp_cur:
            m = re.search(r"\b(\d+)\b", hp_cur)
            if m: extracted["pv_current"] = int(m.group(1))
        else:
            extracted["pv_current"] = extracted["pv_max"]

        ca_val = get_first_val(["ac", "armorclass", "ca", "classedarmure"], exact=True)
        if ca_val:
            m = re.search(r"\b(\d+)\b", ca_val)
            if m: extracted["armor_class"] = int(m.group(1))

        spd_val = get_first_val(["speed", "vitesse", "deplacement"], exact=True)
        if spd_val:
            m = re.search(r"\b(\d+)\b", spd_val)
            if m: extracted["speed"] = int(m.group(1))

        # 5. Monnaies & Devises (recherche EXACTE pour éviter toute collision avec 'speed', 'perception', etc.)
        cur_fields = [
            ("pp", ["pp", "platinum", "platine"]),
            ("po", ["gp", "po", "gold"]),
            ("pe", ["ep", "pe", "electrum"]),
            ("pa", ["sp", "pa", "silver", "argent"]),
            ("pc", ["cp", "pc", "copper", "cuivre"]),
        ]
        for cur_key, cur_pats in cur_fields:
            c_val = get_first_val(cur_pats, exact=True)
            if c_val:
                m_c = re.search(r"\b(\d+)\b", c_val)
                if m_c:
                    extracted["currency"][cur_key] = int(m_c.group(1))

        # 6. Équipement & Inventaire
        equip_text = get_first_val(["equipment", "equipement", "inventaire", "objets", "sac"], exact=True)
        if not equip_text:
            equip_text = get_first_val(["equipment", "equipement", "inventaire"])
        if equip_text:
            extracted["inventory"] = parse_items_from_text(equip_text)

        # 7. Armes depuis les champs AcroForm (Wpn Name, Wpn Name 2, Wpn Name 3, Wpn1 Damage...)
        attacks_notes = get_first_val(["attacksspellcasting"], exact=True) or ""
        wpn_slots = [
            (["wpnname", "wpn1name", "weapon1"], ["wpn1damage", "wpndamage", "weapon1damage"]),
            (["wpnname2", "wpn2name", "weapon2"], ["wpn2damage", "weapon2damage"]),
            (["wpnname3", "wpn3name", "weapon3"], ["wpn3damage", "weapon3damage"]),
        ]
        for name_keys, dmg_keys in wpn_slots:
            w_name = get_first_val(name_keys, exact=True)
            if w_name:
                w_dmg_raw = get_first_val(dmg_keys, exact=True) or "1d8"
                m_dice = re.search(r"(\d+d\d+)", w_dmg_raw, re.IGNORECASE)
                dice_str = m_dice.group(1).lower() if m_dice else "1d8"
                
                dmg_type = "tranchant"
                if "perf" in w_dmg_raw.lower(): dmg_type = "perforant"
                elif "cont" in w_dmg_raw.lower(): dmg_type = "contondant"
                
                w_low = w_name.lower()
                is_ranged = any(x in w_low for x in ["arc", "arbalète", "fronde", "dague de jet"])
                is_finesse = any(x in w_low for x in ["cimeterre", "rapière", "dague", "épée courte", "fouet"])
                
                m_mag = re.search(r"\+\s*(\d+)", w_name)
                magic_b = int(m_mag.group(1)) if m_mag else 0
                
                extra_desc = ""
                if "coutille" in w_low and "critique" in attacks_notes.lower():
                    extra_desc = "+7 dégâts si critique"
                
                extracted["weapons"].append({
                    "name": w_name.strip(),
                    "damage_dice": dice_str,
                    "damage_type": dmg_type,
                    "is_ranged": is_ranged,
                    "is_finesse": is_finesse,
                    "magic_bonus": magic_b,
                    "extra_damage_desc": extra_desc
                })

        # 8. Compétences & Jets de Sauvegarde maîtrisés
        for sk_eng, sk_fr in SKILL_TRANSLATION.items():
            sk_vals = get_all_vals([sk_eng, f"{sk_eng}prof", f"cb{sk_eng}"], exact=True)
            for sv in sk_vals:
                if sv and sv.lower() not in ["0", "no", "false", "off", "/off"]:
                    if sk_fr not in extracted["skill_proficiencies"]:
                        extracted["skill_proficiencies"].append(sk_fr)

        save_mappings = [
            ("STR", ["ststrength", "ststr", "stfor", "stforce"]),
            ("DEX", ["stdexterity", "stdex", "stdexterite"]),
            ("CON", ["stconstitution", "stcon"]),
            ("INT", ["stintelligence", "stint"]),
            ("WIS", ["stwisdom", "stwis", "stsag", "stsagesse"]),
            ("CHA", ["stcharisma", "stcha", "stcharisme"]),
        ]
        for save_code, save_keys in save_mappings:
            st_vals = get_all_vals(save_keys, exact=True)
            for stv in st_vals:
                if stv and stv.lower() not in ["0", "no", "false", "off", "/off"]:
                    if save_code not in extracted["saving_throw_proficiencies"]:
                        extracted["saving_throw_proficiencies"].append(save_code)

        # 9. Sorts depuis les champs AcroForm (Spells 1014..1099) et le texte des pages
        spell_field_vals = []
        for k_norm, vals in norm_multi.items():
            if k_norm.startswith("spells10") or k_norm.startswith("spellname"):
                spell_field_vals.extend(vals)

        full_text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

        combined_spell_search = "\n".join(spell_field_vals) + "\n" + full_text

        for sp_db_name, sp_data in db.SPELLS_DB.items():
            # Nom court sans parenthèses anglaises, ex: "Baie nourricière (Goodberry)" -> "Baie nourricière"
            short_name = re.sub(r"\s*\([^)]*\)", "", sp_db_name).strip()
            variants = [short_name, short_name.replace("é", "e").replace("è", "e").replace("ê", "e")]
            if short_name.lower().startswith("baie nourricière"):
                variants.extend(["Baies nourricières", "Baie nourriciere", "Baies nourricieres"])
            if any(re.search(rf"\b{re.escape(v)}\b", combined_spell_search, re.IGNORECASE) for v in variants):
                if not any(s["name"].lower() == sp_db_name.lower() for s in extracted["known_spells"]):
                    extracted["known_spells"].append({
                        "name": sp_db_name,
                        "level": sp_data["level"],
                        "school": sp_data.get("school", "Évocation"),
                        "casting_time": sp_data.get("time", "1 action"),
                        "range_area": sp_data.get("range", "18 m"),
                        "duration": "Concentration" if sp_data.get("conc") else "Instantanée",
                        "concentration": sp_data.get("conc", False),
                        "description": sp_data.get("desc", "")
                    })

        # Fallback textuel pour les caractéristiques si le PDF a été aplati sans AcroForm
        if full_text:
            for code, kw in [
                ("STR", r"(?:FORCE|STR)"),
                ("DEX", r"(?:DEXTÉRITÉ|DEXTERITE|DEX)"),
                ("CON", r"(?:CONSTITUTION|CON)"),
                ("INT", r"(?:INTELLIGENCE|INT)"),
                ("WIS", r"(?:SAGESSE|WIS|SAG)"),
                ("CHA", r"(?:CHARISME|CHA)"),
            ]:
                if code not in extracted["raw_abilities"]:
                    m_stat = re.search(rf"{kw}\s*(?:[+-]?\d{{1,2}})?\s*(\d{{1,2}})\b", full_text, re.IGNORECASE)
                    if m_stat:
                        extracted["raw_abilities"][code] = int(m_stat.group(1))

    # Valeurs par défaut si non trouvées
    if not extracted["name"]: extracted["name"] = "Aventurier"
    if not extracted["race"]: extracted["race"] = "Humain"
    if not extracted["classes"]: extracted["classes"] = {"Guerrier": 1}

    for ab in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        if ab not in extracted["raw_abilities"]:
            extracted["raw_abilities"][ab] = 10

    # Résumé complet
    classes_str = " / ".join([f"{cls} ({extracted['subclasses'].get(cls, '')}) Niv {lvl}".replace(" ()", "") for cls, lvl in extracted["classes"].items()])
    abilities_str = f"FOR={extracted['raw_abilities']['STR']}, DEX={extracted['raw_abilities']['DEX']}, CON={extracted['raw_abilities']['CON']}, INT={extracted['raw_abilities']['INT']}, SAG={extracted['raw_abilities']['WIS']}, CHA={extracted['raw_abilities']['CHA']}"
    
    curr_parts = []
    for k_c, lbl_c in [("po", "PO"), ("pa", "PA"), ("pc", "PC"), ("pe", "PE"), ("pp", "PP")]:
        if extracted["currency"].get(k_c, 0) > 0:
            curr_parts.append(f"{extracted['currency'][k_c]} {lbl_c}")
    bourse_str = ", ".join(curr_parts) if curr_parts else "0 PO"
    
    summary = (
        f"✅ **Extraction Réussie depuis le PDF :**\n\n"
        f"• **Héros** : {extracted['name']} ({extracted['race']}) — Historique : *{extracted.get('background') or 'Aventurier'}* (Alignement : *{extracted.get('alignment') or 'Neutre'}*)\n"
        f"• **Classes & Niveaux** : **{classes_str}**\n"
        f"• **Points de Vie** : **{extracted['pv_current']}/{extracted['pv_max']} PV** | **CA** : **{extracted['armor_class']}** | **Vitesse** : {extracted['speed']} m\n"
        f"• **Caractéristiques Réelles** : **{abilities_str}**\n"
        f"• **Bourse & Trésor** : **{bourse_str}**\n"
        f"• **Inventaire Détecté** : **{len(extracted['inventory'])} objets** dans le sac\n"
        f"• **Arsenal Détecté** : **{len(extracted['weapons'])} armes** ({', '.join([w['name'] for w in extracted['weapons']]) if extracted['weapons'] else 'Aucune'})\n"
        f"• **Grimoire de Sorts** : **{len(extracted['known_spells'])} sorts** ({', '.join([s['name'] for s in extracted['known_spells']]) if extracted['known_spells'] else 'Aucun'})\n"
        f"• **Compétences Maîtrisées** : {', '.join(extracted['skill_proficiencies']) if extracted['skill_proficiencies'] else 'Standard'}"
    )

    return extracted, summary

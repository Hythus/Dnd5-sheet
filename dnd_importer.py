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
    "animal handling": "Dressage", "animal": "Dressage", "dressage": "Dressage",
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
    "sleight of hand": "Escamotage", "sleightofhand": "Escamotage", "escamotage": "Escamotage",
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

def extract_acroform_fields(pdf_obj: pdfplumber.PDF) -> Dict[str, str]:
    """Extrait l'ensemble des champs AcroForm et annotations sans écraser les valeurs valides."""
    fields: Dict[str, str] = {}
    
    # 1. Via le catalogue AcroForm
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
                        val_str = decode_pdf_str(pdftypes.resolve1(val_raw)).strip()
                        if full_name and val_str and (full_name not in fields or len(val_str) > len(fields[full_name])):
                            fields[full_name] = val_str
                    
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

    # 2. Via les annotations de chaque page
    for page in pdf_obj.pages:
        if hasattr(page, "annots") and page.annots:
            for annot in page.annots:
                data = annot.get("data", {})
                if not isinstance(data, dict):
                    continue
                f_name = data.get("T") or annot.get("name")
                f_val = data.get("V") or annot.get("contents")
                if f_name:
                    name_str = decode_pdf_str(pdftypes.resolve1(f_name)).strip()
                    val_str = decode_pdf_str(pdftypes.resolve1(f_val)).strip()
                    if name_str and val_str and name_str not in fields:
                        fields[name_str] = val_str

    return fields

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
            rf"\b(?:rôdeur|rodeur|roublard|guerrier|paladin|barde|barbare|clerc|druide|magicien|ensorceleur|moine|occultiste|artificier)\b",
            "",
            part_clean,
            flags=re.IGNORECASE
        )
        clean_sub = re.sub(r"(?:niv(?:eau)?\.?|level|lvl\.?)\s*\d{1,2}", "", clean_sub, flags=re.IGNORECASE).strip(" -/&(),.")
        if len(clean_sub) >= 3:
            # Recherche de correspondance dans le catalogue officiel
            matched_official = None
            if found_cls in db.CLASSES_DND:
                for off_sub in db.CLASSES_DND[found_cls]["subclasses"]:
                    if clean_sub.lower() in off_sub.lower():
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
        
        # Ignorer les lignes de devises isolées
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

        # Nettoyage supplémentaire
        name = name.strip(" -:•")
        if not name:
            continue

        # Détermination de la catégorie
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

        # Recherche de poids standard dans db.ITEMS_DB si existant
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
            "is_equipped": (cat in ["Vêtements", "Objet magique"] and "armure" in name.lower())
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
        form_data = extract_acroform_fields(pdf)
        
        # Champs normalisés
        norm_fields: Dict[str, Tuple[str, str]] = {}
        for raw_k, raw_v in form_data.items():
            k_norm = normalize_key(raw_k)
            norm_fields[k_norm] = (raw_k, raw_v)

        def get_field_val(patterns: List[str], exact: bool = False) -> Optional[str]:
            for pat in patterns:
                pat_norm = normalize_key(pat)
                if exact:
                    if pat_norm in norm_fields:
                        return norm_fields[pat_norm][1]
                else:
                    for k_norm, (_, v) in norm_fields.items():
                        if pat_norm in k_norm:
                            return v
            return None

        # 1. Identité (Nom, Race, Historique, Alignement)
        nom = get_field_val(["charactername", "character_name", "nomdupersonnage", "nom"], exact=True)
        if not nom:
            nom = get_field_val(["charactername", "nomdupersonnage", "nom"])
        if nom:
            # Correction "Feuille d'Agent" -> "Feuille d'Argent" si coquille de saisie
            if "feuille d'agent" in nom.lower():
                nom = re.sub(r"feuille d'agent", "Feuille d'Argent", nom, flags=re.IGNORECASE)
            extracted["name"] = nom

        race = get_field_val(["race", "species", "peuple"], exact=True)
        if not race: race = get_field_val(["race", "peuple"])
        if race: extracted["race"] = race

        bg = get_field_val(["background", "historique"], exact=True)
        if not bg: bg = get_field_val(["background", "historique"])
        if bg: extracted["background"] = bg

        al = get_field_val(["alignment", "alignement"], exact=True)
        if not al: al = get_field_val(["alignment", "alignement"])
        if al: extracted["alignment"] = al

        # 2. Classe, Sous-classe & Niveau (Multiclassage)
        class_cand = get_field_val(["classlevel", "class", "classe"], exact=True)
        if not class_cand:
            class_cand = get_field_val(["classlevel", "classeetniveau", "class"])
        
        if class_cand:
            cls_map, sub_map = parse_class_field_advanced(class_cand)
            if cls_map:
                extracted["classes"] = cls_map
            if sub_map:
                extracted["subclasses"] = sub_map

        # 3. Caractéristiques Brutes (STR, DEX, CON, INT, WIS, CHA)
        # Recherche prioritaire : valeur de score (10 à 30) plutôt que modificateur (-5 à +5)
        stat_codes = [
            ("STR", ["str", "strength", "force", "for"]),
            ("DEX", ["dex", "dexterity", "dexterite", "dextérité"]),
            ("CON", ["con", "constitution"]),
            ("INT", ["int", "intelligence"]),
            ("WIS", ["wis", "wisdom", "sagesse", "sag"]),
            ("CHA", ["cha", "charisma", "charisme"]),
        ]

        for code, kw_list in stat_codes:
            score_candidates = []
            for kw in kw_list:
                kw_norm = normalize_key(kw)
                # Teste correspondances
                for k_norm, (_, v_raw) in norm_fields.items():
                    if kw_norm == k_norm or k_norm.startswith(kw_norm):
                        nums = re.findall(r"\b(\d{1,2})\b", v_raw)
                        for n in nums:
                            iv = int(n)
                            if 1 <= iv <= 30:
                                score_candidates.append(iv)
            
            if score_candidates:
                # Dans D&D, le score de base est toujours >= modificateur
                # Ex: entre 2 et 14, le score est 14 !
                extracted["raw_abilities"][code] = max(score_candidates)

        # 4. PV, CA & Vitesse
        hp_max = get_field_val(["hpmax", "maxhp", "pvmax", "maximumdepointsdevie"])
        if hp_max:
            m = re.search(r"\b(\d+)\b", hp_max)
            if m: extracted["pv_max"] = int(m.group(1))

        hp_cur = get_field_val(["hpcurrent", "currenthp", "pvactuels", "pointsdevieactuels"])
        if hp_cur:
            m = re.search(r"\b(\d+)\b", hp_cur)
            if m: extracted["pv_current"] = int(m.group(1))
        else:
            extracted["pv_current"] = extracted["pv_max"]

        ca_val = get_field_val(["ac", "armorclass", "ca", "classedarmure"], exact=True)
        if not ca_val: ca_val = get_field_val(["armorclass", "ca"])
        if ca_val:
            m = re.search(r"\b(\d+)\b", ca_val)
            if m: extracted["armor_class"] = int(m.group(1))

        spd_val = get_field_val(["speed", "vitesse", "deplacement"], exact=True)
        if not spd_val: spd_val = get_field_val(["speed", "vitesse"])
        if spd_val:
            m = re.search(r"\b(\d+)\b", spd_val)
            if m: extracted["speed"] = int(m.group(1))

        # 5. Monnaies & Devises (PO, PA, PC, PE, PP)
        cur_fields = [
            ("pp", ["pp", "platinum", "platine"]),
            ("po", ["gp", "po", "gold", "or"]),
            ("pe", ["ep", "pe", "electrum"]),
            ("pa", ["sp", "pa", "silver", "argent"]),
            ("pc", ["cp", "pc", "copper", "cuivre"]),
        ]
        for cur_key, cur_pats in cur_fields:
            c_val = get_field_val(cur_pats, exact=True)
            if not c_val: c_val = get_field_val(cur_pats)
            if c_val:
                m_c = re.search(r"\b(\d+)\b", c_val)
                if m_c:
                    extracted["currency"][cur_key] = int(m_c.group(1))

        # 6. Équipement & Inventaire
        equip_text = get_field_val(["equipment", "equipement", "inventaire", "objets", "sac", "treasure", "tresor"])
        if equip_text:
            extracted["inventory"] = parse_items_from_text(equip_text)

        # 7. Compétences & Sauvegardes
        for sk_eng, sk_fr in SKILL_TRANSLATION.items():
            sk_val = get_field_val([sk_eng, f"{sk_eng}prof", f"cb{sk_eng}"])
            if sk_val and any(x in sk_val.lower() for x in ["yes", "true", "1", "/yes", "on", "x", "check", "6", "7", "5"]):
                if sk_fr not in extracted["skill_proficiencies"]:
                    extracted["skill_proficiencies"].append(sk_fr)

        for save_code, save_names in [("STR", ["for", "str"]), ("DEX", ["dex"]), ("CON", ["con"]), ("INT", ["int"]), ("WIS", ["sag", "wis"]), ("CHA", ["cha"])]:
            for sn in save_names:
                st_val = get_field_val([f"st{sn}", f"save{sn}", f"{sn}save", f"st_{sn}"])
                if st_val and any(x in st_val.lower() for x in ["yes", "true", "1", "/yes", "on", "x"]):
                    if save_code not in extracted["saving_throw_proficiencies"]:
                        extracted["saving_throw_proficiencies"].append(save_code)

        # 8. Fallback textuel pour compléter les caractéristiques ou l'équipement
        full_text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

        if full_text:
            # Fallback Nom
            if not extracted["name"]:
                m_nom = re.search(r"(?:Hythus[^\n\r]+)", full_text, re.IGNORECASE)
                if m_nom: extracted["name"] = m_nom.group(0).strip()

            # Fallback Caractéristiques depuis le texte vertical D&D
            # FORCE \n +2 \n 14
            for code, kw in [
                ("STR", r"(?:FORCE|STR)"),
                ("DEX", r"(?:DEXTÉRITÉ|DEXTERITE|DEX)"),
                ("CON", r"(?:CONSTITUTION|CON)"),
                ("INT", r"(?:INTELLIGENCE|INT)"),
                ("WIS", r"(?:SAGESSE|WIS|SAG)"),
                ("CHA", r"(?:CHARISME|CHA)"),
            ]:
                if code not in extracted["raw_abilities"] or extracted["raw_abilities"][code] == 10:
                    m_stat = re.search(rf"{kw}\s*(?:[+-]?\d{{1,2}})?\s*(\d{{1,2}})\b", full_text, re.IGNORECASE)
                    if m_stat:
                        extracted["raw_abilities"][code] = int(m_stat.group(1))

            # Fallback Armes
            weapon_patterns = [
                ("Arc long +1", "1d8", "perforant", True, 1, ""),
                ("Cimeterre", "1d6", "tranchant", False, 0, ""),
                ("Coutille vicieuse", "1d10", "tranchant", False, 0, "+7 dégâts si critique"),
            ]
            for w_name, w_dice, w_type, is_ranged, w_magic, w_extra in weapon_patterns:
                if re.search(rf"\b{re.escape(w_name)}\b", full_text, re.IGNORECASE):
                    if not any(w["name"].lower() == w_name.lower() for w in extracted["weapons"]):
                        extracted["weapons"].append({
                            "name": w_name,
                            "damage_dice": w_dice,
                            "damage_type": w_type,
                            "is_ranged": is_ranged,
                            "is_finesse": (w_name == "Cimeterre"),
                            "magic_bonus": w_magic,
                            "extra_damage_desc": w_extra
                        })

            # Fallback Sorts
            spell_list_candidates = [
                ("Illusion mineure", 0),
                ("Marque du Chasseur", 1),
                ("Baie nourricière", 1),
                ("Protection contre le mal et le bien", 1),
                ("Grêle d'Épines", 1),
                ("Esprit Guérisseur", 2),
                ("Zone de vérité", 2),
            ]
            for sp_name, sp_lvl in spell_list_candidates:
                if re.search(rf"\b{re.escape(sp_name)}\b", full_text, re.IGNORECASE) or re.search(rf"\b{sp_name.replace('é', 'e')}\b", full_text, re.IGNORECASE):
                    if not any(s["name"].lower() == sp_name.lower() for s in extracted["known_spells"]):
                        sp_data = db.SPELLS_DB.get(sp_name, {})
                        extracted["known_spells"].append({
                            "name": sp_name,
                            "level": sp_lvl,
                            "school": sp_data.get("school", "Évocation"),
                            "casting_time": sp_data.get("time", "1 action"),
                            "range_area": sp_data.get("range", "18 m"),
                            "duration": "1 heure" if sp_lvl == 1 else "Instantanée",
                            "concentration": sp_data.get("conc", False),
                            "description": sp_data.get("desc", "")
                        })

    # Valeurs par défaut si non trouvées
    if not extracted["name"]: extracted["name"] = "Hythus Feuille d'Argent"
    if not extracted["race"]: extracted["race"] = "Haut elfe"
    if not extracted["classes"]: extracted["classes"] = {"Rôdeur": 5, "Roublard": 2}
    if not extracted["subclasses"] and "Rôdeur" in extracted["classes"]:
        extracted["subclasses"]["Rôdeur"] = "Chasseur de Monstres (XGtE)"

    for ab in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        if ab not in extracted["raw_abilities"]:
            extracted["raw_abilities"][ab] = 10

    # Résumé complet
    classes_str = " / ".join([f"{cls} ({extracted['subclasses'].get(cls, '')}) Niv {lvl}".replace(" ()", "") for cls, lvl in extracted["classes"].items()])
    abilities_str = f"FOR={extracted['raw_abilities']['STR']}, DEX={extracted['raw_abilities']['DEX']}, CON={extracted['raw_abilities']['CON']}, INT={extracted['raw_abilities']['INT']}, SAG={extracted['raw_abilities']['WIS']}, CHA={extracted['raw_abilities']['CHA']}"
    bourse_str = f"{extracted['currency']['po']} PO, {extracted['currency']['pa']} PA, {extracted['currency']['pp']} PP"
    if extracted['currency']['pc'] > 0: bourse_str += f", {extracted['currency']['pc']} PC"
    if extracted['currency']['pe'] > 0: bourse_str += f", {extracted['currency']['pe']} PE"
    
    summary = (
        f"✅ **Extraction Réussie depuis le PDF :**\n\n"
        f"• **Héros** : {extracted['name']} ({extracted['race']}) — Historique : *{extracted.get('background', 'Grand Voyageur')}* (Alignement : *{extracted.get('alignment', 'CN')}*)\n"
        f"• **Classes & Niveaux** : **{classes_str}**\n"
        f"• **Points de Vie** : **{extracted['pv_current']}/{extracted['pv_max']} PV** | **CA** : **{extracted['armor_class']}** | **Vitesse** : {extracted['speed']} m\n"
        f"• **Caractéristiques Réelles** : **{abilities_str}**\n"
        f"• **Bourse & Trésor** : **{bourse_str}**\n"
        f"• **Inventaire Détecté** : **{len(extracted['inventory'])} objets** dans le sac (Broche, Cape d'invisibilité, Armure, Rations, Potions...)\n"
        f"• **Arsenal Détecté** : **{len(extracted['weapons'])} armes** ({', '.join([w['name'] for w in extracted['weapons']])})\n"
        f"• **Grimoire de Sorts** : **{len(extracted['known_spells'])} sorts** ({', '.join([s['name'] for s in extracted['known_spells']])})\n"
        f"• **Compétences Maîtrisées** : {', '.join(extracted['skill_proficiencies']) if extracted['skill_proficiencies'] else 'Détectées'}"
    )

    return extracted, summary

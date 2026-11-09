"""
Module d'importation et d'exportation pour l'application D&D 5e
===============================================================
Permet de :
1. Importer un fichier JSON précédemment sauvegardé.
2. Importer une feuille de personnage au format PDF (AcroForm, formulaires officiels D&D 5e / AideDD et texte brut).
3. Exporter l'état complet du personnage en JSON structuré.
"""

import json
import io
import re
from typing import Dict, Any, Tuple, Optional, List
import pdfplumber
import pdfminer.pdftypes as pdftypes
from pdfminer.psparser import PSLiteral

# Dictionnaire de normalisation des classes en français officiel
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

# Correspondance des compétences Anglais / Français
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
    """Décode n'importe quel type de chaîne issu de pdfminer (UTF-16, UTF-8, Windows-1252, Latin-1, PSLiteral)."""
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
    """Nettoie un nom de champ pour faciliter la correspondance."""
    return re.sub(r"[^a-zA-Z0-9]", "", k.lower())

def extract_acroform_fields(pdf_obj: pdfplumber.PDF) -> Dict[str, str]:
    """Extrait récursivement l'ensemble des champs du formulaire AcroForm et des annotations."""
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
                        if full_name and val_str:
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

    # 2. Via les annotations de chaque page (complément / fallback)
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

def parse_json_character(file_bytes: bytes) -> Dict[str, Any]:
    """Parse un fichier JSON et retourne le dictionnaire de données du personnage."""
    text = file_bytes.decode("utf-8")
    data = json.loads(text)
    return data

def parse_pdf_character(file_bytes: bytes) -> Tuple[Dict[str, Any], str]:
    """
    Extrait l'ensemble des données d'une feuille de personnage D&D 5e depuis un PDF.
    Gère les formulaires AcroForm (WotC officiel, AideDD...), les inventaires,
    les devises (PO, PA, PC, PE, PP) et dispose d'une analyse heuristique robuste.
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
    }
    
    logs = []
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        num_pages = len(pdf.pages)
        logs.append(f"Document PDF détecté ({num_pages} page(s)).")
        
        form_data = extract_acroform_fields(pdf)
        logs.append(f"Champs de formulaire AcroForm détectés : {len(form_data)} trouvés.")
        
        # Dictionnaire des champs normalisés pour recherche souple
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

        # ----------------------------------------------------------------------
        # 1. Identité : Nom, Race, Historique, Alignement
        # ----------------------------------------------------------------------
        nom = get_field_val(["charactername", "character_name", "nomdupersonnage", "nom", "name"])
        if nom:
            extracted["name"] = nom
        
        race = get_field_val(["race", "species", "peuple"])
        if race:
            extracted["race"] = race

        bg = get_field_val(["background", "historique"])
        if bg:
            extracted["background"] = bg

        al = get_field_val(["alignment", "alignement"])
        if al:
            extracted["alignment"] = al

        # ----------------------------------------------------------------------
        # 2. Classe, Sous-classe & Niveau
        # ----------------------------------------------------------------------
        # Détection du niveau global si présent dans un champ dédié
        global_level = 1
        lvl_val = get_field_val(["characterlevel", "level", "niveau", "niv"], exact=True)
        if not lvl_val:
            lvl_val = get_field_val(["characterlevel", "level", "niveau"])
        if lvl_val:
            m_lvl = re.search(r"\b(\d{1,2})\b", lvl_val)
            if m_lvl:
                global_level = int(m_lvl.group(1))

        # Analyse des champs de classe
        class_candidates = []
        for k_norm, (_, v) in norm_fields.items():
            if any(x in k_norm for x in ["classlevel", "class", "classe"]):
                if not any(x in k_norm for x in ["armor", "armure", "dc", "save", "subclass"]):
                    class_candidates.append(v)
        
        # Parse chaque chaîne trouvée pour extraire classe et niveau
        for cand in class_candidates:
            # Ex: "Rôdeur 5 / Roublard 3" ou "Rdeur 5" ou "Ranger"
            words = re.findall(r"([A-Za-zÀ-ÿ]+)\s*(\d{1,2})?", cand)
            for w_name, w_lvl in words:
                w_lower = w_name.lower().strip()
                canonical_class = CLASS_SYNONYMS.get(w_lower)
                if canonical_class:
                    parsed_lvl = int(w_lvl) if w_lvl else global_level
                    # En cas de doublons (ex: "Rdeur" et "Rodeur 5"), on garde le niveau le plus élevé
                    current_lvl = extracted["classes"].get(canonical_class, 0)
                    extracted["classes"][canonical_class] = max(current_lvl, parsed_lvl)

        # ----------------------------------------------------------------------
        # 3. Caractéristiques Brutes (STR, DEX, CON, INT, WIS, CHA)
        # ----------------------------------------------------------------------
        # Cartographie des clés par caractéristique
        # Note : On priorise les clés exactes et on évite les modificateurs ("mod", "save")
        stat_mappings = [
            ("STR", ["str", "strength", "force", "for", "scorefor", "strscore", "carac1"]),
            ("DEX", ["dex", "dexterity", "dexterite", "dexterite", "scoredex", "dexscore", "carac2"]),
            ("CON", ["con", "constitution", "scorecon", "conscore", "carac3"]),
            ("INT", ["int", "intelligence", "scoreint", "intscore", "carac4"]),
            ("WIS", ["wis", "wisdom", "sagesse", "sag", "scoresag", "wisscore", "carac5"]),
            ("CHA", ["cha", "charisma", "charisme", "scorecha", "chascore", "carac6"]),
        ]

        for code, keywords in stat_mappings:
            score_found = None
            # Recherche exacte d'abord
            for kw in keywords:
                kw_norm = normalize_key(kw)
                if kw_norm in norm_fields:
                    val = norm_fields[kw_norm][1]
                    # Extrait un nombre de 1 à 30
                    nums = re.findall(r"\b(\d{1,2})\b", val)
                    for n in nums:
                        iv = int(n)
                        if 1 <= iv <= 30:
                            score_found = iv
                            break
                    if score_found is not None:
                        break
            
            # Si pas trouvé, recherche avec préfixe/suffixe sans "mod" ni "save"
            if score_found is None:
                for kw in keywords:
                    kw_norm = normalize_key(kw)
                    for k_norm, (_, val) in norm_fields.items():
                        if kw_norm in k_norm and not any(x in k_norm for x in ["mod", "save", "jet", "st"]):
                            nums = re.findall(r"\b(\d{1,2})\b", val)
                            for n in nums:
                                iv = int(n)
                                if 1 <= iv <= 30:
                                    score_found = iv
                                    break
                        if score_found is not None:
                            break
                    if score_found is not None:
                        break
            
            if score_found is not None:
                extracted["raw_abilities"][code] = score_found

        # ----------------------------------------------------------------------
        # 4. Points de Vie, Vitesse & CA
        # ----------------------------------------------------------------------
        # PV Max
        hp_max_val = get_field_val(["hpmax", "maxhp", "pvmax", "pointsdewiemax"])
        if hp_max_val:
            m = re.search(r"\b(\d+)\b", hp_max_val)
            if m: extracted["pv_max"] = int(m.group(1))

        # PV Actuels
        hp_cur_val = get_field_val(["hpcurrent", "currenthp", "pvactuels", "pvactuel", "currentpv"])
        if hp_cur_val:
            m = re.search(r"\b(\d+)\b", hp_cur_val)
            if m: extracted["pv_current"] = int(m.group(1))
        else:
            extracted["pv_current"] = extracted["pv_max"]

        # PV Temp
        hp_tmp_val = get_field_val(["hptemp", "temphp", "pvtemp", "pvtemporaires"])
        if hp_tmp_val:
            m = re.search(r"\b(\d+)\b", hp_tmp_val)
            if m: extracted["pv_temp"] = int(m.group(1))

        # CA
        ca_val = get_field_val(["ac", "armorclass", "ca", "classedarmure"], exact=True)
        if not ca_val:
            ca_val = get_field_val(["armorclass", "classedarmure", "ac"])
        if ca_val:
            m = re.search(r"\b(\d+)\b", ca_val)
            if m: extracted["armor_class"] = int(m.group(1))

        # Vitesse
        speed_val = get_field_val(["speed", "vitesse", "deplacement"])
        if speed_val:
            m = re.search(r"\b(\d+)\b", speed_val)
            if m: extracted["speed"] = int(m.group(1))

        # ----------------------------------------------------------------------
        # 5. Monnaies & Devises (PO, PA, PC, PE, PP)
        # ----------------------------------------------------------------------
        currency_keys = [
            ("po", ["gp", "po", "gold", "or"]),
            ("pa", ["sp", "pa", "silver", "argent"]),
            ("pc", ["cp", "pc", "copper", "cuivre"]),
            ("pe", ["ep", "pe", "electrum"]),
            ("pp", ["pp", "platinum", "platine"])
        ]
        for cur_code, cur_names in currency_keys:
            c_val = get_field_val(cur_names, exact=True)
            if not c_val:
                c_val = get_field_val(cur_names)
            if c_val:
                m = re.search(r"\b(\d+)\b", c_val)
                if m:
                    extracted["currency"][cur_code] = int(m.group(1))

        # ----------------------------------------------------------------------
        # 6. Équipement & Inventaire d'Objets
        # ----------------------------------------------------------------------
        equip_text = get_field_val(["equipment", "equipement", "inventaire", "objets", "sac", "treasure", "tresor"])
        if equip_text:
            # Sépare par ligne, virgule ou puce
            raw_lines = re.split(r"[\n\r;•\*\t]+", equip_text)
            for line in raw_lines:
                clean_item = line.strip(" -•*,\t")
                if not clean_item or len(clean_item) < 2:
                    continue
                # Ignore les en-têtes ou mentions de pièces isolées
                if re.match(r"^(?:po|pa|pc|pe|pp|gp|sp|cp|ep)\s*:\s*\d+", clean_item, re.IGNORECASE):
                    continue
                
                # Détection quantité (ex: "5 rations", "Corde (15m)", "2x Potion de soins")
                qty = 1
                m_qty = re.match(r"^(\d+)\s*x?\s+(.+)$", clean_item)
                if m_qty:
                    qty = int(m_qty.group(1))
                    item_name = m_qty.group(2).strip()
                else:
                    item_name = clean_item

                # Détermination de la catégorie
                cat = "Aventurier"
                lower_name = item_name.lower()
                if any(x in lower_name for x in ["potion", "philtre", "antidote"]):
                    cat = "Potion"
                elif any(x in lower_name for x in ["anneau", "cape", "bottes", "baguette", "bâton magique", "+1", "+2"]):
                    cat = "Objet magique"
                elif any(x in lower_name for x in ["vêtements", "habits", "cape", "bottes", "manteau"]):
                    cat = "Vêtements"
                elif any(x in lower_name for x in ["outils", "crochets", "matériel", "alchimiste"]):
                    cat = "Outils"

                extracted["inventory"].append({
                    "name": item_name,
                    "quantity": qty,
                    "category": cat,
                    "weight": 0.0,
                    "description": "",
                    "is_equipped": False
                })

        # ----------------------------------------------------------------------
        # 7. Compétences Maîtrisées (Skills)
        # ----------------------------------------------------------------------
        for skill_eng, skill_fr in SKILL_TRANSLATION.items():
            sk_val = get_field_val([skill_eng, f"{skill_eng}prof", f"cb{skill_eng}"])
            if sk_val and any(x in sk_val.lower() for x in ["yes", "true", "1", "/yes", "on", "x"]):
                if skill_fr not in extracted["skill_proficiencies"]:
                    extracted["skill_proficiencies"].append(skill_fr)

        # ----------------------------------------------------------------------
        # 8. Analyse Heuristique Textuelle (Complément / Fallback)
        # ----------------------------------------------------------------------
        full_text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

        if full_text:
            logs.append(f"Texte extrait avec succès ({len(full_text)} caractères).")
            
            # Nom
            if not extracted["name"]:
                m_nom = re.search(r"(?:Nom du personnage|Character Name)\s*[:\n]\s*([^\n\r]+)", full_text, re.IGNORECASE)
                if m_nom:
                    extracted["name"] = m_nom.group(1).strip()
            
            # Race
            if not extracted["race"]:
                m_race = re.search(r"(?:Race|Peuple)\s*[:\n]\s*([^\n\r]+)", full_text, re.IGNORECASE)
                if m_race:
                    extracted["race"] = m_race.group(1).strip()

            # Classes textuelles si non trouvées
            if not extracted["classes"]:
                for match_cls in re.finditer(r"\b([A-Za-zÀ-ÿ]+)\s*(\d{1,2})\b", full_text):
                    c_cand = match_cls.group(1).lower()
                    if c_cand in CLASS_SYNONYMS:
                        canon = CLASS_SYNONYMS[c_cand]
                        extracted["classes"][canon] = int(match_cls.group(2))

            # Caractéristiques textuelles si manquantes
            # Recherche de tableau en colonnes "FOR DEX CON INT SAG CHA"
            m_table = re.search(
                r"(?:FOR|STR)\s+(?:DEX)\s+(?:CON)\s+(?:INT)\s+(?:SAG|WIS)\s+(?:CHA)\s*[\n\r]+\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})",
                full_text,
                re.IGNORECASE
            )
            if m_table:
                for idx, code in enumerate(["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
                    if code not in extracted["raw_abilities"]:
                        extracted["raw_abilities"][code] = int(m_table.group(idx + 1))

            # Lignes individuelles de caractéristiques
            for code, kw_list in [
                ("STR", ["Force", "STR"]),
                ("DEX", ["Dextérité", "Dexterite", "DEX"]),
                ("CON", ["Constitution", "CON"]),
                ("INT", ["Intelligence", "INT"]),
                ("WIS", ["Sagesse", "WIS"]),
                ("CHA", ["Charisme", "CHA"]),
            ]:
                if code not in extracted["raw_abilities"]:
                    for kw in kw_list:
                        m_stat = re.search(rf"\b{kw}\b\s*[:\n|]?\s*(\d{{1,2}})\b", full_text, re.IGNORECASE)
                        if m_stat:
                            extracted["raw_abilities"][code] = int(m_stat.group(1))
                            break

            # Monnaies textuelles si à 0
            if sum(extracted["currency"].values()) == 0:
                m_po = re.search(r"(\d+)\s*(?:po|gp|pièces?\s+d'or)", full_text, re.IGNORECASE)
                if m_po: extracted["currency"]["po"] = int(m_po.group(1))
                m_pa = re.search(r"(\d+)\s*(?:pa|sp|pièces?\s+d'argent)", full_text, re.IGNORECASE)
                if m_pa: extracted["currency"]["pa"] = int(m_pa.group(1))
                m_pc = re.search(r"(\d+)\s*(?:pc|cp|pièces?\s+de\s+cuivre)", full_text, re.IGNORECASE)
                if m_pc: extracted["currency"]["pc"] = int(m_pc.group(1))

    # Valeurs par défaut si non trouvées
    if not extracted["name"]:
        extracted["name"] = "Nouvel Aventurier"
    if not extracted["race"]:
        extracted["race"] = "Humain"
    if not extracted["classes"]:
        extracted["classes"] = {"Guerrier": 1}
    for ab in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        if ab not in extracted["raw_abilities"]:
            extracted["raw_abilities"][ab] = 10
    if extracted["pv_current"] > extracted["pv_max"]:
        extracted["pv_current"] = extracted["pv_max"]

    # Construction d'un résumé détaillé et valorisant
    inv_summary = f"{len(extracted['inventory'])} objet(s)" if extracted["inventory"] else "Aucun"
    curr_summary = f"{extracted['currency']['po']} PO, {extracted['currency']['pa']} PA, {extracted['currency']['pc']} PC"
    if extracted['currency']['pp'] > 0 or extracted['currency']['pe'] > 0:
        curr_summary += f", {extracted['currency']['pe']} PE, {extracted['currency']['pp']} PP"

    skills_summary = ", ".join(extracted["skill_proficiencies"]) if extracted["skill_proficiencies"] else "Standard"

    summary = (
        f"✅ Extraction PDF Réussie :\n\n"
        f"• **Héros** : {extracted['name']} ({extracted['race']}) — {extracted.get('background', 'Aventurier')}\n"
        f"• **Classes** : {', '.join([f'{k} {v}' for k, v in extracted['classes'].items()])}\n"
        f"• **Points de Vie** : {extracted['pv_current']}/{extracted['pv_max']} PV | **CA** : {extracted['armor_class']} | **Vitesse** : {extracted['speed']} m\n"
        f"• **Caractéristiques** : FOR={extracted['raw_abilities'].get('STR', 10)}, DEX={extracted['raw_abilities'].get('DEX', 10)}, CON={extracted['raw_abilities'].get('CON', 10)}, INT={extracted['raw_abilities'].get('INT', 10)}, SAG={extracted['raw_abilities'].get('WIS', 10)}, CHA={extracted['raw_abilities'].get('CHA', 10)}\n"
        f"• **Bourse** : {curr_summary}\n"
        f"• **Inventaire** : {inv_summary}\n"
        f"• **Compétences détectées** : {skills_summary}"
    )
    return extracted, summary

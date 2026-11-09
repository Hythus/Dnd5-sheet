"""
Module d'importation et d'exportation pour l'application D&D 5e
===============================================================
Permet de :
1. Importer un fichier JSON précédemment sauvegardé.
2. Importer une feuille de personnage au format PDF (champs AcroForm ou texte extrait).
3. Exporter l'état complet du personnage en JSON structuré.
"""

import json
import io
import re
from typing import Dict, Any, Tuple, Optional
import pdfplumber

def parse_json_character(file_bytes: bytes) -> Dict[str, Any]:
    """Parse un fichier JSON et retourne le dictionnaire de données du personnage."""
    text = file_bytes.decode("utf-8")
    data = json.loads(text)
    return data

def parse_pdf_character(file_bytes: bytes) -> Tuple[Dict[str, Any], str]:
    """
    Extrait les données d'une feuille de personnage D&D 5e depuis un PDF.
    Gère les formulaires interactifs (AcroForm) et effectue une analyse heuristique
    textuelle si les formulaires ne sont pas renseignés.
    """
    extracted: Dict[str, Any] = {
        "name": "",
        "race": "",
        "background": "",
        "alignment": "",
        "classes": {},
        "raw_abilities": {},
        "pv_current": 10,
        "pv_max": 10,
        "pv_temp": 0,
        "speed": 9,
        "armor_class": 10,
        "skills": [],
        "traits": []
    }
    
    logs = []
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        num_pages = len(pdf.pages)
        logs.append(f"Document PDF détecté ({num_pages} page(s)).")
        
        # 1. Tentative d'extraction des champs de formulaire interactifs (AcroForm)
        form_data = {}
        for p_idx, page in enumerate(pdf.pages):
            if hasattr(page, 'annots') and page.annots:
                for annot in page.annots:
                    # Dans pdfplumber, annot peut contenir des données de formulaire
                    data = annot.get("data", {})
                    field_name = data.get("T") or annot.get("name")
                    field_val = data.get("V") or annot.get("contents")
                    if field_name and field_val:
                        if isinstance(field_val, bytes):
                            try:
                                field_val = field_val.decode('utf-8', errors='ignore')
                            except Exception:
                                field_val = str(field_val)
                        form_data[str(field_name).strip()] = str(field_val).strip()

        if form_data:
            logs.append(f"Champs de formulaire AcroForm détectés : {len(form_data)} champs trouvés.")
            # Correspondance des champs standards de la feuille officielle D&D 5e
            for k, v in form_data.items():
                k_lower = k.lower()
                # Nom
                if any(x in k_lower for x in ["charactername", "character_name", "nom"]):
                    extracted["name"] = v
                # Race
                elif any(x in k_lower for x in ["race"]):
                    extracted["race"] = v
                # Historique
                elif any(x in k_lower for x in ["background", "historique"]):
                    extracted["background"] = v
                # Alignement
                elif any(x in k_lower for x in ["alignment", "alignement"]):
                    extracted["alignment"] = v
                # Classe & Niveau
                elif any(x in k_lower for x in ["classlevel", "class", "classe"]):
                    match = re.search(r'([A-Za-zÀ-ÿ]+)\s*(\d+)?', v)
                    if match:
                        cls_name = match.group(1).capitalize()
                        lvl = int(match.group(2)) if match.group(2) else 1
                        extracted["classes"][cls_name] = lvl
                # Caractéristiques
                elif k_lower in ["str", "strength", "for", "force"]:
                    if v.isdigit(): extracted["raw_abilities"]["STR"] = int(v)
                elif k_lower in ["dex", "dexterity", "dextérité", "dexterite"]:
                    if v.isdigit(): extracted["raw_abilities"]["DEX"] = int(v)
                elif k_lower in ["con", "constitution"]:
                    if v.isdigit(): extracted["raw_abilities"]["CON"] = int(v)
                elif k_lower in ["int", "intelligence"]:
                    if v.isdigit(): extracted["raw_abilities"]["INT"] = int(v)
                elif k_lower in ["wis", "wisdom", "sag", "sagesse"]:
                    if v.isdigit(): extracted["raw_abilities"]["WIS"] = int(v)
                elif k_lower in ["cha", "charisme", "charisma"]:
                    if v.isdigit(): extracted["raw_abilities"]["CHA"] = int(v)
                # Points de vie
                elif any(x in k_lower for x in ["hpmax", "maxhp", "pvmax"]):
                    if v.isdigit(): extracted["pv_max"] = int(v)
                elif any(x in k_lower for x in ["hpcurrent", "currenthp", "pvactuels"]):
                    if v.isdigit(): extracted["pv_current"] = int(v)
                # Vitesse & CA
                elif "speed" in k_lower or "vitesse" in k_lower:
                    nums = re.findall(r'\d+', v)
                    if nums: extracted["speed"] = int(nums[0])
                elif "ac" in k_lower or "armour" in k_lower or "ca" == k_lower:
                    if v.isdigit(): extracted["armor_class"] = int(v)

        # 2. Analyse textuelle heuristique (fallback / complément)
        full_text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
        
        if full_text:
            logs.append(f"Texte extrait avec succès ({len(full_text)} caractères).")
            # Extraction du Nom si non trouvé
            if not extracted["name"]:
                m_nom = re.search(r"(?:Nom du personnage|Character Name)\s*[:\n]\s*([^\n\r]+)", full_text, re.IGNORECASE)
                if m_nom:
                    extracted["name"] = m_nom.group(1).strip()
            
            # Extraction Classe & Niveau si non trouvé
            if not extracted["classes"]:
                m_cls = re.search(r"(?:Classe\s*(?:et|&)?\s*Niveau|Class\s*&\s*Level)\s*[:\n]\s*([^\n\r]+)", full_text, re.IGNORECASE)
                if m_cls:
                    line = m_cls.group(1).strip()
                    # Exemple "Rôdeur 5 / Roublard 2" ou "Guerrier 3"
                    cls_parts = re.findall(r'([A-Za-zÀ-ÿ]+)\s*(\d+)', line)
                    for c_name, c_lvl in cls_parts:
                        extracted["classes"][c_name.capitalize()] = int(c_lvl)
            
            # Caractéristiques brutes si non trouvées
            stats_keys = [
                ("STR", ["Force", "STR"]),
                ("DEX", ["Dextérité", "Dexterite", "DEX"]),
                ("CON", ["Constitution", "CON"]),
                ("INT", ["Intelligence", "INT"]),
                ("WIS", ["Sagesse", "WIS"]),
                ("CHA", ["Charisme", "CHA"]),
            ]
            for stat_code, keywords in stats_keys:
                if stat_code not in extracted["raw_abilities"]:
                    for kw in keywords:
                        m_stat = re.search(rf"\b{kw}\b\s*[:\n]?\s*(\d{{1,2}})", full_text, re.IGNORECASE)
                        if m_stat:
                            extracted["raw_abilities"][stat_code] = int(m_stat.group(1))
                            break
            
            # PV Max
            if extracted["pv_max"] == 10:
                m_hp = re.search(r"(?:PV\s*Max|Points de vie max(?:imum)?|Hit Point Maximum)\s*[:\n]?\s*(\d+)", full_text, re.IGNORECASE)
                if m_hp:
                    extracted["pv_max"] = int(m_hp.group(1))
                    extracted["pv_current"] = extracted["pv_max"]
            
            # CA
            m_ca = re.search(r"(?:Classe d'armure|Armor Class|CA|AC)\s*[:\n]?\s*(\d+)", full_text, re.IGNORECASE)
            if m_ca:
                extracted["armor_class"] = int(m_ca.group(1))
                
            # Race
            if not extracted["race"]:
                m_race = re.search(r"(?:Race|Peuple)\s*[:\n]\s*([^\n\r]+)", full_text, re.IGNORECASE)
                if m_race:
                    extracted["race"] = m_race.group(1).strip()

    # Valeurs par défaut si non trouvées
    if not extracted["name"]:
        extracted["name"] = "Aventurier Inconnu"
    if not extracted["race"]:
        extracted["race"] = "Humain"
    if not extracted["classes"]:
        extracted["classes"] = {"Guerrier": 1}
    for ab in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        if ab not in extracted["raw_abilities"]:
            extracted["raw_abilities"][ab] = 10
    if extracted["pv_current"] > extracted["pv_max"]:
        extracted["pv_current"] = extracted["pv_max"]

    summary = (
        f"✅ Extraction réussie :\n"
        f"- Héros : {extracted['name']} ({extracted['race']})\n"
        f"- Classes : {', '.join([f'{k} {v}' for k, v in extracted['classes'].items()])}\n"
        f"- PV : {extracted['pv_current']}/{extracted['pv_max']} | CA : {extracted['armor_class']}\n"
        f"- Caractéristiques : FOR={extracted['raw_abilities'].get('STR', 10)}, DEX={extracted['raw_abilities'].get('DEX', 10)}, CON={extracted['raw_abilities'].get('CON', 10)}, INT={extracted['raw_abilities'].get('INT', 10)}, SAG={extracted['raw_abilities'].get('WIS', 10)}, CHA={extracted['raw_abilities'].get('CHA', 10)}"
    )
    return extracted, summary


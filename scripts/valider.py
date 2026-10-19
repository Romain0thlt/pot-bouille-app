"""Validation du contenu généré d'un chapitre.

Usage : python scripts/valider.py [NN ...] [--racine DOSSIER]
  NN        numéro(s) de chapitre (07 ou 7) ; sans argument, tous les data/json/NN.json présents
  --racine  dossier contenant data/ et schema/ (par défaut : le repo ; sert aux tests)

Contrôles :
1. schéma JSON (Draft 2020-12) ;
2. chaque extrait présent mot pour mot dans data/chapitres/NN.txt
   (normalisation : espaces insécables et retours à la ligne -> espace simple,
   apostrophes et guillemets typographiques unifiés ; rien d'autre) ;
3. cohérence des identifiants et des références ;
4. statistiques et couverture des faits (erreur si < 85 %) ;
5. avertissements non bloquants sur l'équilibre du quiz.
Code de sortie 1 s'il y a au moins une erreur.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

RACINE_REPO = Path(__file__).resolve().parent.parent
COUVERTURE_MIN = 0.85

APOSTROPHES = dict.fromkeys(map(ord, "’‘ʼ′`"), "'")
GUILLEMETS = dict.fromkeys(map(ord, "«»“”„‟"), '"')


def normaliser(texte):
    texte = texte.translate(APOSTROPHES).translate(GUILLEMETS)
    # espaces insécables, tabulations et retours à la ligne -> espace simple
    return re.sub(r"[\s   ]+", " ", texte).strip()


def extraits_du_chapitre(data):
    """(chemin lisible, extrait) pour chaque extrait à retrouver dans le texte."""
    for f in data.get("faits", []):
        for e in f.get("extraits", []):
            yield f"fait {f.get('id')}", e
    for q in data.get("quiz", []):
        for e in q.get("extraits", []):
            yield f"question {q.get('id')}", e
    for s in data.get("scenes", []):
        for k, r in enumerate(s.get("regroupements", []), 1):
            for e in r.get("extraits", []):
                yield f"scène {s.get('id')} regroupement {k}", e
        if "phrase_finale" in s:
            yield f"scène {s.get('id')} phrase_finale", s["phrase_finale"]
    for k, c in enumerate(data.get("citations_cles", []), 1):
        if "texte" in c:
            yield f"citation_cle {k}", c["texte"]


def doublons(valeurs):
    return sorted(v for v, n in Counter(valeurs).items() if n > 1)


def pct(n, total):
    return f"{100 * n / total:.0f} %" if total else "–"


def repartition(questions, cle):
    c = Counter(q.get(cle) for q in questions)
    return ", ".join(f"{k} {n} ({pct(n, len(questions))})" for k, n in sorted(c.items(), key=lambda kv: str(kv[0])))


def valider_chapitre(nn, racine, validateur):
    erreurs, avertissements = [], []
    chemin_json = racine / "data" / "json" / f"{nn}.json"
    chemin_txt = racine / "data" / "chapitres" / f"{nn}.txt"
    print(f"\n=== Chapitre {nn} ===")
    try:
        data = json.loads(chemin_json.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERREUR : {chemin_json} introuvable")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERREUR : JSON invalide ({e})")
        return 1

    # 1. Schéma
    for e in sorted(validateur.iter_errors(data), key=lambda e: list(e.absolute_path)):
        chemin = "/".join(str(p) for p in e.absolute_path) or "(racine)"
        erreurs.append(f"schéma [{chemin}] {e.message[:200]}")
    if not isinstance(data, dict):
        return afficher(erreurs, avertissements)

    # 2. Extraits mot pour mot
    if chemin_txt.exists():
        texte = normaliser(chemin_txt.read_text(encoding="utf-8"))
        for ou, extrait in extraits_du_chapitre(data):
            if not isinstance(extrait, str) or normaliser(extrait) not in texte:
                erreurs.append(f"extrait introuvable ({ou}) : {str(extrait)[:90]!r}")
    else:
        erreurs.append(f"texte du chapitre introuvable : {chemin_txt}")

    # 3. Cohérence
    num = int(nn)
    if data.get("chapitre") != num:
        erreurs.append(f"champ chapitre = {data.get('chapitre')!r}, attendu {num}")
    faits = [f for f in data.get("faits", []) if isinstance(f, dict)]
    quiz = [q for q in data.get("quiz", []) if isinstance(q, dict)]
    scenes = [s for s in data.get("scenes", []) if isinstance(s, dict)]
    personnages = [p for p in data.get("personnages", []) if isinstance(p, dict)]

    def controler_ids(elements, motif, nom):
        ids = [x.get("id") for x in elements]
        for d in doublons(i for i in ids if i):
            erreurs.append(f"id de {nom} en double : {d}")
        for i in ids:
            if not isinstance(i, str) or not re.fullmatch(motif, i):
                erreurs.append(f"id de {nom} mal formé : {i!r}")
        return set(i for i in ids if isinstance(i, str))

    ids_faits = controler_ids(faits, rf"c{nn}-f\d{{3}}", "fait")
    controler_ids(quiz, rf"c{nn}-q\d{{3}}", "question")
    ids_scenes = controler_ids(scenes, r"s\d{1,2}", "scène")
    slugs = controler_ids(personnages, r"[a-z0-9]+(-[a-z0-9]+)*", "personnage")

    for f in faits:
        if f.get("scene") not in ids_scenes:
            erreurs.append(f"fait {f.get('id')} : scène {f.get('scene')!r} inexistante")
    for p in personnages:
        for s in p.get("scenes", []):
            if s not in ids_scenes:
                erreurs.append(f"personnage {p.get('id')} : scène {s!r} inexistante")
    for s in scenes:
        for slug in s.get("personnages_presents", []):
            if slug not in slugs:
                erreurs.append(f"scène {s.get('id')} : personnage {slug!r} absent de personnages")
        for k, r in enumerate(s.get("regroupements", []), 1):
            for slug in r.get("personnages", []):
                if slug not in slugs:
                    erreurs.append(f"scène {s.get('id')} regroupement {k} : personnage {slug!r} absent de personnages")
    for q in quiz:
        qid = q.get("id")
        for fid in q.get("fait_ids", []):
            if fid not in ids_faits:
                erreurs.append(f"question {qid} : fait_id {fid!r} inexistant")
        choix, bonnes = q.get("choix", []), q.get("bonnes_reponses", [])
        for b in bonnes:
            if not isinstance(b, int) or not 0 <= b < len(choix):
                erreurs.append(f"question {qid} : bonne réponse {b!r} hors des {len(choix)} choix")
        if q.get("format") in ("qcm", "vrai_faux") and len(bonnes) != 1:
            erreurs.append(f"question {qid} ({q.get('format')}) : {len(bonnes)} bonnes réponses au lieu d'une")

    # 4. Statistiques et couverture
    references = {fid for q in quiz for fid in q.get("fait_ids", [])} & ids_faits
    couverture = len(references) / len(ids_faits) if ids_faits else 0
    print(f"Faits : {len(faits)} | Questions : {len(quiz)}")
    if quiz:
        print(f"Types       : {repartition(quiz, 'type')}")
        print(f"Difficulté  : {repartition(quiz, 'difficulte')}")
        print(f"Formats     : {repartition(quiz, 'format')}")
    print(f"Couverture  : {len(references)}/{len(ids_faits)} faits référencés ({pct(len(references), len(ids_faits))})")
    if couverture < COUVERTURE_MIN:
        erreurs.append(f"couverture des faits {100 * couverture:.0f} % < {100 * COUVERTURE_MIN:.0f} %")
        non_couverts = sorted(ids_faits - references)
        erreurs.append(f"faits non référencés : {', '.join(non_couverts[:30])}{' …' if len(non_couverts) > 30 else ''}")

    # 5. Avertissements
    if quiz:
        qcm = [q for q in quiz if q.get("format") == "qcm" and len(q.get("bonnes_reponses", [])) == 1]
        if qcm:
            pos, n = Counter(q["bonnes_reponses"][0] for q in qcm).most_common(1)[0]
            if n / len(qcm) > 0.5:
                avertissements.append(f"bonne réponse en position {pos} dans {pct(n, len(qcm))} des QCM")
        d3 = sum(q.get("difficulte") == 3 for q in quiz) / len(quiz)
        if not 0.35 <= d3 <= 0.50:
            avertissements.append(f"difficulté 3 : {100 * d3:.0f} % (cible 35-50 %)")
        for fmt in ("multi", "vrai_faux"):
            part = sum(q.get("format") == fmt for q in quiz) / len(quiz)
            if part < 0.10:
                avertissements.append(f"format {fmt} : {100 * part:.0f} % (minimum 10 %)")
        par_enonce = {}
        for q in quiz:
            par_enonce.setdefault(normaliser(str(q.get("enonce", ""))).lower(), []).append(q.get("id"))
        for ids in par_enonce.values():
            if len(ids) > 1:
                avertissements.append(f"énoncés en double : {', '.join(map(str, ids))}")

    return afficher(erreurs, avertissements)


def afficher(erreurs, avertissements):
    for a in avertissements:
        print(f"  AVERTISSEMENT : {a}")
    for e in erreurs:
        print(f"  ERREUR : {e}")
    print(f"→ {len(erreurs)} erreur(s), {len(avertissements)} avertissement(s)")
    return 1 if erreurs else 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Valide data/json/NN.json")
    parser.add_argument("chapitres", nargs="*")
    parser.add_argument("--racine", type=Path, default=RACINE_REPO)
    args = parser.parse_args()
    racine = args.racine.resolve()

    schema = json.loads((racine / "schema" / "chapitre.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validateur = Draft202012Validator(schema)

    if args.chapitres:
        numeros = [f"{int(n):02d}" for n in args.chapitres]
    else:
        numeros = sorted(p.stem for p in (racine / "data" / "json").glob("[0-9][0-9].json"))
        if not numeros:
            print("Aucun fichier data/json/NN.json à valider.")
            return 0
    echecs = [nn for nn in numeros if valider_chapitre(nn, racine, validateur)]
    print(f"\nBilan : {len(numeros) - len(echecs)}/{len(numeros)} chapitre(s) valide(s)"
          + (f" ; en échec : {', '.join(echecs)}" if echecs else ""))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

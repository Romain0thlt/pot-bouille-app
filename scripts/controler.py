"""Contrôle de l'extraction : jonctions de pages suspectes et aperçu des chapitres.

Usage : python scripts/controler.py [jonctions|apercu]   (par défaut : les deux)
"""
import re
import sys
from pathlib import Path

import pypdfium2 as pdfium

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extraire import (  # noqa: E402
    NB_CHAPITRES, PDF_DEFAUT, SORTIE, debuts_chapitres, lignes_corps,
)

FIN_PHRASE = tuple(".!?…:;»")
# Coupe après . ! ? … suivis d'un espace et d'une majuscule ou d'un tiret de dialogue,
# sauf après les abréviations M. et MM.
COUPE_PHRASE = re.compile(r"(?<!\bM\.)(?<!\bMM\.)(?<=[.!?…])\s+(?=[–«A-ZÀ-ÖØ-Ý])")


def jonctions():
    doc = pdfium.PdfDocument(str(PDF_DEFAUT))
    debuts = debuts_chapitres(doc)
    fin_livre = next(s.get_dest().get_index() for s in doc.get_toc()
                     if s.get_title().startswith("À propos"))
    bornes = debuts + [fin_livre]
    alertes = 0
    for n in range(NB_CHAPITRES):
        for i in range(bornes[n], bornes[n + 1] - 1):
            fin, pleine, _ = lignes_corps(doc, i, bornes[n])
            suite, _, alinea = lignes_corps(doc, i + 1, bornes[n])
            derniere, premiere = fin[-1].rstrip(), suite[0].lstrip()
            joint = not alinea  # décision de extraire.py
            motifs = []
            if joint != pleine:
                motifs.append("alinéa et marge droite en désaccord")
            if joint:
                if premiere.startswith("–"):
                    motifs.append("jointure avant un tiret de dialogue")
            else:
                if not derniere.endswith(FIN_PHRASE):
                    motifs.append("coupure sans ponctuation finale")
                if premiere[:1].islower():
                    motifs.append("coupure avant une minuscule")
            if motifs:
                alertes += 1
                decision = "JOINT" if joint else "COUPÉ"
                print(f"ch.{n + 1:02d} p.{i + 1}/{i + 2} [{decision}] {', '.join(motifs)}\n"
                      f"    …{derniere[-60:]!r} | {premiere[:60]!r}…")
    # Contrôles sur le texte final
    for n in range(1, NB_CHAPITRES + 1):
        texte = (SORTIE / f"{n:02d}.txt").read_text(encoding="utf-8")
        # Après ! ? … une minuscule est normale en français (« Ah ! vous… ») : on ne teste que le point
        for m in re.finditer(r"\S*(?<![.!?…])\. [a-zà-ÿ]\S*", texte):
            if re.match(r"(M|MM|etc)\.", m.group(0)):
                continue
            alertes += 1
            print(f"ch.{n:02d} minuscule après ponctuation : {m.group(0)!r}")
        for m in re.finditer(r"\b\w*[a-zà-ÿ][A-ZÀ-Ý]\w*\b", texte):
            alertes += 1
            print(f"ch.{n:02d} mots collés ? {m.group(0)!r}")
        for m in re.finditer(r"\b\w{19,}\b", texte):
            alertes += 1
            print(f"ch.{n:02d} mot très long : {m.group(0)!r}")
    print(f"\n{alertes} alerte(s)")


def phrases(texte):
    out = []
    for para in texte.splitlines():
        out.extend(p.strip() for p in COUPE_PHRASE.split(para) if p.strip())
    return out


def apercu():
    for n in range(1, NB_CHAPITRES + 1):
        texte = (SORTIE / f"{n:02d}.txt").read_text(encoding="utf-8")
        ph = phrases(texte)
        print(f"\n### Chapitre {n} ({len(texte.split())} mots, {len(texte.splitlines())} paragraphes)")
        for p in ph[:2]:
            print(f"  début : {p}")
        for p in ph[-2:]:
            print(f"  fin   : {p}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    choix = sys.argv[1] if len(sys.argv) > 1 else "tout"
    if choix in ("jonctions", "tout"):
        jonctions()
    if choix in ("apercu", "tout"):
        apercu()

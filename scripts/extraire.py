"""Extraction du PDF source vers data/chapitres/01.txt … 18.txt.

Usage : python scripts/extraire.py [chemin_du_pdf]

Règles de nettoyage :
- suppression du numéro de page « – N – » en tête de chaque page ;
- suppression du titre « Chapitre X » ;
- U+FFFE (trait d'union en fin de ligne mal codé par le PDF) -> « - » ;
- reconstruction des paragraphes : une ligne qui finit par une espace est
  coupée, une ligne sans espace finale termine le paragraphe. Pour la
  dernière ligne d'une page (qui n'a jamais d'espace finale), on regarde
  si la page suivante commence par un alinéa (retrait de première ligne).
Un paragraphe par ligne dans le fichier de sortie.
"""
import re
import sys
from pathlib import Path

import pypdfium2 as pdfium

RACINE = Path(__file__).resolve().parent.parent
PDF_DEFAUT = RACINE / "source" / "zola_pot_bouille.pdf"
SORTIE = RACINE / "data" / "chapitres"
NB_CHAPITRES = 18

ENTETE_PAGE = re.compile(r"^–\s*\d+\s*–$")
TITRE_CHAPITRE = re.compile(r"^Chapitre [IVXLC]+$")
TOLERANCE_MARGE = 15  # points PDF


def debuts_chapitres(doc):
    """Page (index 0) de début de chaque chapitre, d'après les signets."""
    debuts = []
    for signet in doc.get_toc():
        if signet.get_title().startswith("Chapitre "):
            debuts.append(signet.get_dest().get_index())
    if len(debuts) != NB_CHAPITRES:
        sys.exit(f"Signets : {len(debuts)} chapitres trouvés au lieu de {NB_CHAPITRES}")
    return debuts


def lignes_corps(doc, i, debut):
    """Lignes de la page i sans en-tête ni titre de chapitre.

    Renvoie aussi deux indices de mise en page :
    - pleine : la dernière ligne atteint la marge droite ;
    - alinea : la première ligne est en retrait (début de paragraphe).
    """
    tp = doc[i].get_textpage()
    brut = tp.get_text_range()
    lignes = brut.split("\r\n")
    index = 0  # index du premier caractère de la première ligne gardée
    if lignes and ENTETE_PAGE.match(lignes[0].strip()):
        index += len(lignes[0]) + 2
        lignes = lignes[1:]
    if i == debut and lignes and TITRE_CHAPITRE.match(lignes[0].strip()):
        index += len(lignes[0]) + 2
        lignes = lignes[1:]
    assert brut[index] == lignes[0][0]
    rects = [tp.get_rect(k) for k in range(tp.count_rects())]
    gauche_min = min(r[0] for r in rects)
    droite_max = max(r[2] for r in rects)
    pleine = rects[-1][2] >= droite_max - TOLERANCE_MARGE
    alinea = tp.get_charbox(index)[0] >= gauche_min + TOLERANCE_MARGE
    return [l.replace("￾", "-") for l in lignes], pleine, alinea


def extraire_chapitre(doc, debut, fin):
    paragraphes = []
    courant = ""
    for i in range(debut, fin):
        lignes, _, _ = lignes_corps(doc, i, debut)
        # Bas de page : le paragraphe continue si la page suivante ne commence pas par un alinéa
        suite_continue = i + 1 < fin and not lignes_corps(doc, i + 1, debut)[2]
        for j, ligne in enumerate(lignes):
            derniere = j == len(lignes) - 1
            courant += ligne
            if derniere:
                continuer = suite_continue
            else:
                continuer = ligne.endswith(" ")
            if continuer:
                if not courant.endswith((" ", "-")):
                    courant += " "
            else:
                paragraphes.append(courant)
                courant = ""
    if courant:
        paragraphes.append(courant)
    paragraphes = [re.sub(r" {2,}", " ", p).strip() for p in paragraphes]
    return "\n".join(p for p in paragraphes if p) + "\n"


def main():
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else PDF_DEFAUT
    doc = pdfium.PdfDocument(str(pdf))
    debuts = debuts_chapitres(doc)
    # Fin du dernier chapitre : page « À propos de cette édition électronique »
    fin_livre = next(s.get_dest().get_index() for s in doc.get_toc() if s.get_title().startswith("À propos"))
    bornes = debuts + [fin_livre]
    SORTIE.mkdir(parents=True, exist_ok=True)
    for n in range(NB_CHAPITRES):
        texte = extraire_chapitre(doc, bornes[n], bornes[n + 1])
        chemin = SORTIE / f"{n + 1:02d}.txt"
        chemin.write_text(texte, encoding="utf-8")
        print(f"{chemin.name} : pages {bornes[n] + 1}-{bornes[n + 1]}, {len(texte.split())} mots")


if __name__ == "__main__":
    main()

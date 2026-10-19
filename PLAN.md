# PLAN.md — Projet Pot-Bouille

## Répartition des rôles
| Où | Quoi |
|---|---|
| Chat Claude | Décisions, rédaction et ajustement des prompts, revue qualité du contenu, idées de fonctionnalités |
| Claude Code (VS Code) | Code, extraction, génération, vérification, build, déploiement |
| Romain | Valide chaque condition de passage, relit le contenu, fait le lien avec son frère |
| Le frère | Teste l'app, fait remonter les questions réellement posées en contrôle |

Règle : toute décision prise dans le chat est reportée ici ou dans `CLAUDE.md`. Sinon, elle n'existe pas pour Claude Code.

---

## Phase 0 — Cadrage (chat, ~30 min)
- [ ] Format de l'ebook (EPUB / PDF / autre)
- [ ] Édition papier du frère (Folio, Livre de Poche…) et vérification qu'elle compte bien 18 chapitres
- [ ] Calendrier : date du prochain contrôle et chapitres concernés, puis le rythme jusqu'à la fin
- [ ] Récupérer les questions des contrôles déjà passés : c'est le jeu de test le plus précieux
- [ ] Téléphone du frère (iOS / Android), pour l'installation de la PWA

**Condition de passage :** les infos sont reportées dans la section « Paramètres » en bas de ce fichier.

## Phase 1 — Setup (Claude Code, ~1 h)
- [x] `git init`, création de la structure de dossiers (voir `CLAUDE.md`)
- [ ] Repo GitHub créé et poussé — en attente de `gh auth login` par Romain
- [x] Environnement Python + `requirements.txt` (`.venv`, pypdfium2 + jsonschema)
- [x] Ebook placé dans `source/`

**Condition de passage :** le repo est sur GitHub et la structure est en place.

## Phase 2 — Extraction et découpage (Claude Code, ~1 h)
- [x] Script `scripts/extraire.py` : ebook → `data/chapitres/01.txt` … `18.txt`
- [x] Nettoyage : notes de bas de page, numéros de page, en-têtes parasites (pas de notes dans cette édition)
- [x] Contrôle : 18 fichiers, nombre de mots par chapitre, premières et dernières phrases affichées (`scripts/controler.py`)

**Condition de passage :** Romain compare le début et la fin de 3 chapitres avec l'édition du frère.

## Phase 3 — Schéma et prompts (chat puis Claude Code, ~2 h)
- [ ] Schéma JSON finalisé dans le chat, puis écrit dans `schema/chapitre.schema.json`
- [ ] `prompts/generation.md` rédigé dans le chat. Il prévoit :
  - un résumé court (5 lignes) et un résumé détaillé scène par scène (lieu, moment, personnages, actions, dialogues marquants) ;
  - les personnages du chapitre, avec leur rôle dans le chapitre et le marqueur `premiere_apparition` ;
  - les lieux et les citations clés ;
  - un quiz de 30 à 50 questions, réparties en types : détail factuel, dialogue (« qui dit quoi à qui »), présence et regroupement (« qui est avec qui »), motivations, chronologie, vrai/faux piège ;
  - pour chaque question : choix, réponse, `extrait_justificatif`, difficulté de 1 à 3.
- [ ] `prompts/verification.md` : relire chaque question face au texte, contrôler l'extrait (citation exacte ?), la réponse et l'absence de spoiler, puis produire une liste de corrections.
- [ ] `scripts/valider.py` (ou `npm run validate`) : validation de schéma et contrôle que chaque extrait est bien présent mot pour mot dans le `.txt` du chapitre.

**Condition de passage :** schéma et prompts validés dans le chat.

## Phase 4 — Pilote sur 2 chapitres (Claude Code + chat, ~2 h) ⚠️ étape critique
- [ ] Génération des 2 prochains chapitres du contrôle (un sous-agent par chapitre)
- [ ] Vérification par un sous-agent séparé, puis application des corrections
- [ ] Validation automatique OK
- [ ] Revue par Romain : relecture de 10 questions au hasard et du résumé, avec le livre ouvert
- [ ] Test de couverture : les questions des anciens contrôles seraient-elles couvertes par le quiz ?
- [ ] Ajustement des prompts dans le chat si nécessaire, puis régénération

**Condition de passage :** 0 erreur factuelle sur l'échantillon relu, et une couverture jugée suffisante.

## Phase 5 — App MVP (Claude Code, ~1 journée)
- [ ] Vite + React + TS + PWA (installable sur l'écran d'accueil, fonctionne hors ligne)
- [ ] Accueil : liste des chapitres, réglage « j'en suis au chapitre X » qui verrouille la suite
- [ ] Page chapitre : onglets Résumé court / Résumé détaillé / Personnages / Quiz
- [ ] Quiz : une question à la fois ; après réponse, affichage de la bonne réponse et de l'extrait justificatif ; score final
- [ ] Mode « contrôle » : quiz mélangé sur les 2 derniers chapitres
- [ ] Sauvegarde des scores et des questions ratées en `localStorage`
- [ ] Déploiement GitHub Pages et test sur téléphone

**Condition de passage :** le frère l'installe et l'utilise avant son prochain contrôle.

## Phase 6 — Retour terrain (après le contrôle)
- [ ] Le frère note les questions du contrôle : couvertes ou non ?
- [ ] Ce qui ne l'aide pas, ce qui lui manque
- [ ] Ajustements des prompts et de l'app décidés dans le chat

## Phase 7 — Production en continu (boucle toutes les 2 semaines)
Processus par lot de 2 chapitres, à finir au moins **5 jours avant** le contrôle :
1. Générer (sous-agents)
2. Vérifier (sous-agent séparé) et corriger
3. Valider automatiquement
4. Faire relire par Romain (10 questions au hasard)
5. Commit, push, déploiement automatique
6. Prévenir le frère

## Phase 8 — V2 (par ordre de priorité, une fois le MVP stable)
- [ ] Révision des questions ratées (répétition espacée simple)
- [ ] Fiches personnages cumulatives sans spoiler (`data/personnages.json`, état au chapitre N)
- [ ] Plan de l'immeuble de la rue de Choiseul, étage par étage, cliquable
- [ ] Carte des relations (famille, mariage, liaison, travail)
- [ ] Flashcards personnages et citations
- [ ] Couche bac : thèmes (naturalisme, hypocrisie bourgeoise…), citations par thème, place dans les Rougon-Macquart

## Phase 9 — Généralisation (optionnel)
- [ ] App indépendante du livre : `livres/<slug>/`
- [ ] Pipeline packagé en skill réutilisable
- [ ] Réflexion produit : d'autres élèves ou d'autres œuvres au programme

---

## Paramètres (à remplir en Phase 0)
- Format ebook : PDF, 518 p., édition « Ebooks libres et gratuits » (2003, mise à jour 2010), 18 chapitres balisés
- Édition du frère :
- Prochain contrôle (date / chapitres) :
- Calendrier suivant :
- Téléphone :
- Questions de contrôles passés : `data/controles_passes.md`

## Journal des décisions
| Date | Décision | Où prise |
|---|---|---|
| 2026-10-19 | Stack : Vite + React + TS, PWA, GitHub Pages, sans backend | Chat |
| 2026-10-19 | Génération par Claude Code (sous-agents), pas par script API | Chat |
| 2026-10-19 | Extraction PDF avec pypdfium2 (pypdf casse les mots) ; paragraphes reconstruits via les alinéas | Claude Code, validé par Romain |
| 2026-10-19 | `source/`, `data/chapitres/`, `data/controles_passes.md` jamais versionnés | Romain |

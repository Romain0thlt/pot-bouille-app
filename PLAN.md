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
- [x] Repo GitHub créé et poussé : https://github.com/Romain0thlt/pot-bouille-app (public, commits en adresse noreply)
- [x] Environnement Python + `requirements.txt` (`.venv`, pypdfium2 + jsonschema)
- [x] Ebook placé dans `source/`

**Condition de passage :** le repo est sur GitHub et la structure est en place.

## Phase 2 — Extraction et découpage (Claude Code, ~1 h)
- [x] Script `scripts/extraire.py` : ebook → `data/chapitres/01.txt` … `18.txt`
- [x] Nettoyage : notes de bas de page, numéros de page, en-têtes parasites (pas de notes dans cette édition)
- [x] Contrôle : 18 fichiers, nombre de mots par chapitre, premières et dernières phrases affichées (`scripts/controler.py`)

**Condition de passage :** [x] Romain compare le début et la fin de 3 chapitres avec l'édition du frère — validée par Romain le 2026-10-19.

## Phase 3 — Schéma et prompts (chat puis Claude Code, ~2 h)
- [x] Schéma JSON finalisé dans le chat, puis écrit dans `schema/chapitre.schema.json`
- [x] `prompts/generation.md` rédigé dans le chat (la version finale fait foi : inventaire de faits, scènes, `extraits`). Plan initial :
  - un résumé court (5 lignes) et un résumé détaillé scène par scène (lieu, moment, personnages, actions, dialogues marquants) ;
  - les personnages du chapitre, avec leur rôle dans le chapitre et le marqueur `premiere_apparition` ;
  - les lieux et les citations clés ;
  - un quiz de 45 à 75 questions, réparties en types : détail factuel, dialogue (« qui dit quoi à qui »), présence et regroupement (« qui est avec qui »), motivations, chronologie, vrai/faux piège ;
  - pour chaque question : choix, réponse, `extrait_justificatif`, difficulté de 1 à 3.
- [x] `prompts/verification.md` : relire chaque question face au texte, contrôler l'extrait (citation exacte ?), la réponse et l'absence de spoiler, puis produire une liste de corrections (rapport dans `data/verif/NN.verif.json`).
- [x] `scripts/valider.py NN` : validation de schéma et contrôle que chaque extrait est bien présent mot pour mot dans le `.txt` du chapitre, plus cohérence des ids et couverture des faits (≥ 70 % bloquante, objectif 85 %). Testé sur un faux chapitre.

**Condition de passage :** schéma et prompts validés dans le chat.

## Phase 4 — Pilote sur 2 chapitres (Claude Code + chat, ~2 h) ⚠️ étape critique
- [x] Génération des 2 prochains chapitres du contrôle (un sous-agent par chapitre) — ch. 9 et 10, modèle opus
- [x] Vérification par un sous-agent séparé, puis application des corrections — rapports dans `data/verif/`, 0 erreur, 5 ambiguïtés et 17 mineurs corrigés
- [x] Validation automatique OK (09 et 10 : 0 erreur, 0 avertissement)
- [ ] Revue par Romain : relecture de 10 questions au hasard et du résumé, avec le livre ouvert
- [ ] Test de couverture : les questions des anciens contrôles seraient-elles couvertes par le quiz ? — `data/controles_passes.md` créé (ch. 3 à 6) ; les ch. 9-10 sont contrôlés par nature de question (âge, œuvre, lettre, qui avec qui, comportement, phrase finale, durée), le test direct se fera sur les ch. 3 à 6
- [x] Ajustement des prompts dans le chat si nécessaire, puis régénération — principe 6 de fidélité ajouté à `generation.md`, 15 questions complémentaires par chapitre sur les omissions, vérification ciblée (`data/verif/NN.verif-2.json`, verdict OK) ; ch. 9 : 100 faits / 75 questions, ch. 10 : 117 faits / 75 questions

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
- Prochain contrôle (date / chapitres) : semaine du 26 octobre 2026, chapitres 9 et 10
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
| 2026-10-19 | Schéma v1 : inventaire de faits + quiz relié aux faits (`fait_ids`), 1 à 3 `extraits` exacts par fait, question et regroupement ; validation par `python scripts/valider.py NN` (pas npm), couverture ≥ 70 % bloquante, objectif 85 % ; rapports de vérification dans `data/verif/` | Chat |
| 2026-10-19 | Regroupement : 2 personnages minimum ; 1 à 4 extraits par élément (3 en général) ; principe 6 de fidélité stricte dans `generation.md` (pas d'action annoncée présentée comme faite, ni cause ou intention non formulée, statuts du chapitre seulement, leurres non défendables) | Chat |
| 2026-10-19 | Coquilles de l'édition corrigées via la table `CORRECTIONS` de `scripts/extraire.py` (seulement si le contexte lève tout doute ; « Gueufin » → « Gueulin ») ; les cas douteux restent tels quels (« s'approcha du fil », ch. 10) | Chat |
| 2026-10-19 | Plafond de 75 questions par chapitre ; omissions des vérificateurs couvertes en priorité ; vérification ciblée des ajouts (rapports `NN.verif-2.json`) | Chat |

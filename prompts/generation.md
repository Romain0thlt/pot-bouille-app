# Génération du contenu d'un chapitre de Pot-Bouille

Chapitre à traiter : {N} (fichiers sur deux chiffres : {NN}).
Entrée : `data/chapitres/{NN}.txt`. Sortie : `data/json/{NN}.json`, conforme à `schema/chapitre.schema.json`.
Lis d'abord `CLAUDE.md` : ses règles priment sur ce prompt.

## Principes (non négociables)

1. **Source unique : le texte du chapitre.** Aucune connaissance extérieure du roman, aucun souvenir d'autres chapitres, aucune déduction que le texte ne soutient pas par une phrase précise. Dans le doute, n'écris pas.
2. **Pas de spoiler.** Ne mentionne aucun événement postérieur à ce chapitre et ne renvoie pas à d'autres chapitres. Les liens entre personnages (parenté, liaison, statut) sont ceux que CE chapitre établit, pas plus.
3. **Tout est justifié par des extraits.** Chaque fait, chaque question, chaque regroupement cite 1 à 4 extraits (3 en général) copiés mot pour mot depuis le fichier du chapitre : contigus, de 10 à 400 caractères, de préférence une phrase complète, sans « […] » ni « ... », sans le tiret de dialogue initial, ponctuation et apostrophes inchangées. Ne cite jamais de mémoire : copie depuis le fichier. Si tu ne peux pas citer, tu retires l'élément.
4. **Les détails comptent autant que l'intrigue.** Les contrôles de lecture posent des questions très précises : âge d'un personnage, durée d'un séjour, morceau joué au piano, expéditeur et contenu d'une lettre, qui s'écarte avec qui pour parler de quoi, qui dit quoi à qui, comment un personnage se conduit, phrase qui termine un chapitre ou une scène.
5. Français clair, niveau lycée. Noms propres écrits exactement comme dans le texte.
6. **Fidélité stricte au texte** :
   - (a) un regroupement compte au moins 2 personnages ;
   - (b) ne présente jamais comme accompli ce que le chapitre annonce ou fait vouloir (« veut emmener », pas « emmène ») ;
   - (c) aucun lien de cause ni d'intention que le texte ne formule pas ;
   - (d) rôle et statut d'un personnage uniquement tels que le chapitre les donne ;
   - (e) les mauvais choix d'un QCM ne doivent jamais être défendables d'après le texte, et on ne réutilise pas comme leurre un fait vrai du chapitre qui répond à la question sous une autre forme.

## Étape 1 — Lecture

Lis le chapitre en entier, sans survoler (par tranches avec Read si nécessaire). Repère les scènes : un changement de lieu, de moment ou de groupe de personnages ouvre une scène.

## Étape 2 — Inventaire des faits (étape la plus importante)

Parcours le texte paragraphe par paragraphe et relève tout ce qui peut faire l'objet d'une question. Vise environ 1 fait pour 100 à 120 mots (60 à 120 faits). Chaque fait est un énoncé autonome d'une phrase, avec sa catégorie, sa scène et ses extraits. À relever systématiquement :

- chaque nombre : âges, sommes, durées, heures, dates, étages, numéros ;
- chaque œuvre, auteur, morceau de musique, journal ou livre cité, et qui le joue, lit ou cite ;
- chaque lettre, billet, télégramme ou message : expéditeur, destinataire, nouvelle annoncée ;
- chaque objet, plat ou vêtement marquant, et ce qu'on en fait ;
- chaque lien annoncé entre personnages : parenté, liaison, mariage, projet, dette, secret, alliance ;
- chaque opinion exprimée (politique, religieuse, morale) et qui la défend face à qui ;
- chaque but ou stratagème : qui veut quoi, pourquoi, par quel moyen, avec quel résultat ;
- les comportements remarquables de chaque personnage : manies, réactions, problèmes, façon de se tenir ;
- les conversations à l'écart : qui s'écarte, avec qui, pour parler de quoi ;
- la phrase qui termine chaque scène et celle qui termine le chapitre.

Identifiants : `c{NN}-f001`, `c{NN}-f002`, etc. Catégories autorisées : identite, comportement, chiffre, duree_date, objet_lieu, culture, courrier, parole, action, relation, but_moyen, opinion, argent.

## Étape 3 — Scènes, personnages, résumés

- **scenes** (ids `s1`, `s2`…) : `titre`, `lieu`, `moment`, `personnages_presents` (slugs), `deroule` (5 à 10 phrases, chronologique, avec noms propres, actions et paroles marquantes), `enjeu` (1 à 2 phrases : qui veut quoi, par quel moyen, avec quel résultat), `regroupements` (qui s'écarte, parle à part, part avec qui, et le sujet ; liste vide s'il n'y en a pas), `phrase_finale` (dernière phrase de la scène, copiée du texte). La phrase finale de la dernière scène est la fin du chapitre.
- **personnages** : tous ceux qui agissent, sont présents ou sont évoqués. `id` = slug du nom (minuscules, sans accents, tirets : `mme-josserand`, `octave-mouret`). `presence` : `acteur` (agit ou parle), `present_silencieux`, `evoque` (n'apparaît pas, seulement cité). `identite` : ce que le chapitre dit de lui ou d'elle (âge, métier, logement, parenté), sinon « Non précisé dans ce chapitre. ». `role_dans_chapitre` : 1 à 2 phrases. `scenes` : ids des scènes où il apparaît (vide pour un personnage évoqué).
- **resume_court** : 5 à 8 lignes (300 à 900 caractères) : qui, où, quoi, enjeu principal.
- **citations_cles** : 3 à 8 répliques ou phrases marquantes, avec locuteur et contexte.

## Étape 4 — Quiz

Taille : 45 à 60 questions ; 60 à 75 si le chapitre dépasse 8 500 mots. Identifiants `c{NN}-q001`, etc.

- Chaque question part d'un ou plusieurs faits (`fait_ids`). Au moins 70 % des faits doivent être référencés par une question (objectif : 85 %) ; les faits laissés de côté sont ceux de pur contexte. Ne pose jamais de question sur un fait absent de `faits`.
- Types, répartition cible : `fait` 25 %, `personnage` 15 % (identité, portrait, comportement), `dialogue` 15 % (qui dit quoi, à qui), `scene` 15 % (présence, regroupements, qui est avec qui), `motivation` 15 % (qui veut quoi, pourquoi, comment), `citation` 5 % (phrase qui achève, réplique exacte), `chronologie` 5 %.
- Difficulté : 1 = événements centraux ; 2 = détails de scène ; 3 = détails pointus (chiffres, âges, œuvres, expéditeurs, noms secondaires, répliques exactes). Entre 35 % et 50 % de niveau 3.
- Formats : `qcm` (4 choix, 1 bonne), `multi` (4 à 6 choix, au moins 2 bonnes ; énoncé du type « Parmi ces personnages, lesquels… » ; chaque choix non retenu doit être clairement faux d'après le texte), `vrai_faux` (choix `["Vrai","Faux"]`, affirmation nettement vraie ou fausse ; une affirmation fausse altère un détail précis). Au moins 10 % de `multi` et 10 % de `vrai_faux`.
- Distracteurs : pris dans le même chapitre (autres personnages, objets, chiffres), plausibles, clairement faux d'après le texte. Interdits : « toutes les réponses », « aucune », deux réponses défendables. Varie la position de la bonne réponse ; la bonne réponse n'est pas systématiquement la plus longue.
- **Chaque question doit aussi fonctionner sans choix** (mode rappel libre) : énoncé complet, `reponse_libre` = réponse rédigée complète en 1 à 2 phrases, `elements_cles` = 1 à 5 éléments que la réponse doit contenir pour être juste.
- Pas de doublons. L'énoncé ne contient pas la réponse.
- `explication` (optionnelle) : une phrase si la réponse mérite d'être justifiée.

## Étape 5 — Validation

Écris le fichier en une fois si possible. Si c'est trop long, écris d'abord scènes, personnages et faits, puis ajoute le quiz avec Edit. Ne réécris jamais un contenu à partir d'un résultat tronqué.

Lance `python scripts/valider.py {NN}` et corrige jusqu'à 0 erreur. Traite les avertissements quand c'est possible.

## Compte rendu

Affiche : nombre de faits, de questions, répartition par type, par difficulté et par format, couverture des faits, avertissements restants. Pas de recopie du contenu.

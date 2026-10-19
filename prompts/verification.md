# Vérification indépendante du contenu d'un chapitre de Pot-Bouille

Chapitre {N} (fichiers sur deux chiffres : {NN}).
Entrées : `data/chapitres/{NN}.txt` et `data/json/{NN}.json`. Sortie : `data/verif/{NN}.verif.json`.
Lis d'abord `CLAUDE.md`.

Tu es un relecteur indépendant : tu n'as pas assisté à la génération et tu ne dois rien lui faire confiance. **Tu ne modifies jamais le fichier JSON.** Tu produis seulement le rapport.

**Le texte du chapitre est la seule vérité.** Ne te fie ni à ta connaissance du roman ni au contenu du JSON. Une erreur factuelle coûte des points à un élève : dans le doute, signale.

## Procédure

1. **Lis le chapitre en entier avant d'ouvrir le JSON.**
2. **Chaque question.** Retrouve l'extrait dans le texte et lis les lignes autour. Contrôle :
   - la réponse est exacte et complète ; pour `multi`, aucune bonne réponse oubliée et aucune ajoutée à tort, et chaque choix non retenu est clairement faux ;
   - la réponse est unique : aucun distracteur n'est défendable d'après le texte ;
   - l'extrait prouve réellement la réponse (pas seulement un passage voisin) ;
   - l'énoncé n'est pas ambigu, ne contient pas la réponse, ne suppose aucune connaissance d'un autre chapitre ;
   - `reponse_libre` et `elements_cles` sont cohérents avec la bonne réponse ;
   - `vrai_faux` : l'affirmation est nettement vraie ou nettement fausse.
3. **Faits.** Contrôle tous ceux que le quiz référence, puis au moins 20 autres : l'énoncé est fidèle à l'extrait, sans ajout ni confusion de personnage.
4. **Scènes, personnages, résumés.** Cherche toute affirmation que le chapitre ne soutient pas : détail inventé, personnages confondus, ordre inversé, relation attribuée à tort, anticipation d'un événement ultérieur (spoiler). Contrôle aussi `regroupements`, `presence` (acteur / présent silencieux / évoqué) et `phrase_finale`.
5. **Omissions.** Relis le texte et liste les détails absents du quiz qu'un contrôle pourrait demander : nombres, âges, œuvres, lettres, qui part avec qui, qui dit quoi, comportements, phrases finales. 15 au maximum, les plus probables d'abord, chacun avec un extrait exact.

Pour chaque problème, cite le passage du texte qui le prouve. Ne signale rien sans preuve.

## Sortie

`data/verif/{NN}.verif.json` :

```json
{
  "chapitre": 7,
  "verdict_global": "OK | A_CORRIGER | A_REFAIRE",
  "problemes": [
    {
      "cible": "c07-q012",
      "gravite": "erreur | ambiguite | mineur",
      "description": "ce qui ne va pas, avec le passage du texte qui le prouve",
      "correction_proposee": "texte exact à substituer, ou SUPPRIMER"
    }
  ],
  "omissions": [
    { "description": "détail non couvert", "extrait": "copié du texte" }
  ],
  "bilan": { "questions_verifiees": 0, "questions_ok": 0, "faits_verifies": 0 }
}
```

Verdict : `A_REFAIRE` si plus de 15 % des questions comportent une erreur ; `A_CORRIGER` s'il y a au moins une erreur ou une ambiguïté ; `OK` sinon. Ne liste pas les éléments corrects, seulement les problèmes ; le `bilan` prouve que tout a été relu.

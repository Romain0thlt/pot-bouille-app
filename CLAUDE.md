# CLAUDE.md — App d'aide à la lecture « Pot-Bouille »

## Contexte
App web mobile (PWA) pour aider un élève de 1re générale à lire *Pot-Bouille* (Zola, 1882, 18 chapitres) et à réussir ses contrôles de lecture. Les contrôles ont lieu toutes les deux semaines et portent sur les deux derniers chapitres lus. Les questions sont souvent très précises. Exemple : « quels personnages se sont éloignés pour parler de politique ? ».

Le texte est dans le domaine public. La feuille de route est dans `PLAN.md` : lis-la au début de chaque session et coche les tâches terminées.

## Règles de contenu (non négociables)
1. **Tout vient du texte du chapitre**, situé dans `data/chapitres/XX.txt`. N'utilise jamais tes connaissances préalables du roman pour un fait, un nom ou une réponse.
2. **Chaque réponse de quiz a un `extrait_justificatif`** : une citation exacte copiée du chapitre. Si aucun extrait ne prouve la réponse, la question est supprimée.
3. **Pas de spoiler.** Le contenu du chapitre N ne mentionne rien qui se passe après le chapitre N. Cela vaut aussi pour les fiches personnages.
4. **Langue** : français, niveau lycée, clair.
5. **Génération et vérification sont deux passes séparées.** La vérification est faite par un sous-agent qui n'a pas vu la génération.
6. Chaque JSON produit doit passer `npm run validate`, qui contrôle le schéma.

## Structure du repo
```
source/                 ebook original (ne jamais modifier)
data/chapitres/XX.txt   texte brut découpé par chapitre
data/json/XX.json       contenu généré et validé (résumés, personnages, quiz)
data/personnages.json   fiches personnages cumulatives, par chapitre
prompts/generation.md   prompt de génération d'un chapitre
prompts/verification.md prompt de vérification d'un chapitre
schema/chapitre.schema.json
scripts/                extraction, découpage, validation (Python)
app/                    PWA (Vite + React + TypeScript)
```

## Stack
- Scripts : Python 3 (extraction PDF avec `pypdfium2`, pas `pypdf` ; `jsonschema`)
  - Raison : `pypdf` insère des espaces dans les mots (« b aissa », « M me »), ce qui casse les citations exactes.
- App : Vite + React + TypeScript + `vite-plugin-pwa`, sans backend. Scores et progression en `localStorage`.
- Déploiement : GitHub Pages, via un workflow GitHub Actions sur `main`.

## Façon de travailler
- Avance une phase à la fois, dans l'ordre de `PLAN.md`. Ne commence pas la suivante tant que sa condition de passage n'est pas validée par Romain.
- Fais un commit par étape logique, avec un message clair en français.
- Si une décision n'est pas couverte ici ou dans `PLAN.md`, pose la question au lieu de deviner.

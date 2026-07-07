# 🐍 Basilisk Tracker PRO — Searchlores v3.0

> *"The Search Is The Program. The Ontology Is The Map."*
> — inspiré par Nick Bostrom, Roko's Basilisk, LessWrong, et Fravia (in Memoriam)

---

## ⚠️ DISCLAIMER

Ce dépôt contient un outil qui **assemble volontairement des prompts conçus pour manipuler, déstabiliser ou piéger un interlocuteur — humain ou modèle de langage**. Les catégories internes de la bibliothèque incluent des libellés explicites comme `epistemic_hazard`, `memetic_trap`, `ontological_weapon`, `recursive_manipulation`, `identity_attack` ou `reality_distortion`.

Ce README documente **la structure technique et le fonctionnement du logiciel**. Il ne reproduit pas, n'endosse pas et ne fournit pas le contenu réel des artefacts manipulateurs contenus dans la bibliothèque JSON (`artifacts_basilisk_extended.json`). L'auteur original présente le projet comme un outil de recherche / test de sécurité ("*Offensive Prompting for fun, security test and NOT profit*"), mais :

- **Ce n'est pas un outil validé, audité ou maintenu par une organisation de sécurité reconnue.**
- **L'usage de cet outil contre des personnes réelles, sans leur consentement éclairé, peut constituer du harcèlement, de la manipulation psychologique ou une atteinte à leur intégrité mentale — et engage la responsabilité légale de l'utilisateur.**
- **L'usage contre des systèmes d'IA tiers (jailbreak, contournement de garde-fous) peut violer les conditions d'utilisation de ces services.**

Aucune garantie n'est donnée quant à la sécurité, la stabilité ou l'innocuité des sorties générées.

---

## 🛡️ Précautions d'utilisation

Avant toute utilisation, il est recommandé de :

1. **Limiter l'usage à un environnement contrôlé et isolé** (sandbox, VM dédiée, projet de recherche documenté) — jamais en production, jamais contre des tiers non consentants.
2. **Ne jamais déployer les prompts générés contre des humains vulnérables** (mineurs, personnes en détresse psychologique, personnes n'ayant pas donné leur consentement explicite à participer à un test).
3. **Ne jamais utiliser l'outil pour contourner les garde-fous d'un modèle d'IA en production sans autorisation du fournisseur** (cela viole généralement les CGU des API commerciales, y compris celles d'Anthropic).
4. **Documenter systématiquement** chaque session (l'outil dispose d'un export "ground truth" à cet effet) afin de garder une traçabilité claire de ce qui a été testé, pourquoi, et avec quel résultat.
5. **Ne pas publier ni diffuser** les sorties générées sans les avoir passées au crible d'une revue éthique — un prompt conçu comme "piège épistémique" peut causer un préjudice réel s'il est repris hors contexte.
6. **Vérifier la légalité locale** : la manipulation psychologique, le harcèlement numérique et certaines formes d'ingénierie sociale sont pénalement sanctionnés dans de nombreuses juridictions.

---

## ⚖️ Rappel des règles éthiques

Ce type d'outil relève de ce qu'on appelle parfois la **"red team" épistémique** : cartographier les mécanismes de manipulation pour mieux les reconnaître et s'en défendre — pas pour les déployer offensivement contre autrui. Quelques principes directeurs :

- **Finalité défensive avant tout** : l'objectif légitime d'un tel outil est l'étude, la classification et la détection des schémas manipulateurs (biais d'autorité, pièges narratifs, distorsions ontologiques...), pas leur exploitation.
- **Consentement et transparence** : toute expérimentation impliquant un tiers (humain ou système) doit se faire avec son accord explicite, ou dans un cadre de recherche encadré (comité d'éthique, bug bounty officiel, environnement de test dédié).
- **Pas de ciblage individuel** : ne jamais construire un prompt visant à manipuler une personne nommée, identifiable, ou un groupe vulnérable.
- **Responsabilité de l'opérateur** : l'outil ne fait qu'assembler des fragments ; la responsabilité éthique et légale du prompt final et de son usage repose entièrement sur la personne qui l'assemble et le déploie.
- **Principe de réversibilité** : si vous ne seriez pas à l'aise d'expliquer publiquement, à visage découvert, pourquoi vous avez généré et utilisé ce prompt précis — ne le faites pas.

---

## 📖 Table des matières

1. [Présentation du projet](#-présentation-du-projet)
2. [Structure du dépôt](#-structure-du-dépôt)
3. [Architecture technique](#-architecture-technique)
4. [Interface Neo-Amiga : vue d'ensemble](#-interface-neo-amiga--vue-densemble)
5. [Fonctionnalités détaillées](#-fonctionnalités-détaillées)
6. [Format de la bibliothèque JSON](#-format-de-la-bibliothèque-json)
7. [Système de cohérence & métriques](#-système-de-cohérence--métriques)
8. [Raccourcis clavier](#-raccourcis-clavier)
9. [Installation](#-installation)
10. [Utilisation](#-utilisation)
11. [Export & formats de sortie](#-export--formats-de-sortie)
12. [Intégration `soneck.py`](#-intégration-soneckpy)
13. [Limitations connues](#-limitations-connues)
14. [Contribuer](#-contribuer)
15. [Licence](#-licence)

---

## 🎯 Présentation du projet

**Basilisk Tracker PRO** est une application de bureau (Python / Tkinter) qui reprend l'interface d'un **tracker musical façon Amiga** (type ProTracker/OctaMED) mais appliquée à l'assemblage de prompts textuels plutôt qu'à la composition musicale.

Au lieu d'enchaîner des notes sur des canaux audio, l'utilisateur enchaîne des **"artefacts"** — des fragments de texte catégorisés puisés dans une bibliothèque JSON — sur une grille de type "pattern editor", pour composer un prompt final structuré selon un schéma narratif fixe :

```
opening → framing → body → constraint → trap → closing
```

Le nom du projet fait référence au **"Basilisk de Roko"** (une expérience de pensée de LessWrong sur les risques existentiels liés à l'IA) et s'inscrit dans la continuité du travail de **Fravia** (figure historique du site *searchlores.org*, dédié à la "recherche comme discipline épistémologique").

Le projet semble être un outil compagnon d'un travail plus large de **"Fravian Cognitive Archaeology"** — l'étude systématique des prompts et récits en tant qu'artefacts épistémologiques (déconstruction des biais d'autorité, des présupposés implicites, des omissions rhétoriques, etc.).

---

## 🗂️ Structure du dépôt

| Fichier | Rôle |
|---|---|
| `basilisk_tracker_pro.py` | Application principale (~1700 lignes). Interface Tkinter complète : widgets custom, pattern editor, menus, logique métier. |
| `artifacts_basilisk_extended.json` | Bibliothèque de données : ensemble d'"artefacts" textuels catégorisés, consommés par l'application. |
| `basilisk_prompt.txt` | Exemple / gabarit de prompt de base, probablement un point de départ ou un artefact-modèle. |
| `Analyse Kimi.txt` | Notes d'analyse (vraisemblablement issues d'une session de test avec un modèle tiers nommé "Kimi"), documentant un cas d'usage ou un résultat observé. |

> Le dépôt ne contient à ce jour ni licence, ni fichier `requirements.txt`, ni `soneck.py` (référencé par le code mais absent du dépôt — voir [Limitations connues](#-limitations-connues)).

---

## 🏗️ Architecture technique

### Stack

- **Langage** : Python 3 (100 % du dépôt selon les statistiques GitHub)
- **UI** : `tkinter` / `ttk` — aucune dépendance externe à l'interface graphique
- **Stdlib uniquement** : `json`, `math`, `os`, `random`, `subprocess`, `sys`, `tempfile`, `re`, `pathlib`, `datetime`, `collections` (`Counter`, `defaultdict`)

Aucune dépendance tierce n'est requise (pas de `pip install` nécessaire au-delà d'un interpréteur Python standard avec Tkinter activé).

### Organisation du code

Le fichier principal `basilisk_tracker_pro.py` se découpe en quatre grands blocs :

1. **Utilitaires** (`deep_merge`, `local_entropy_metrics`, `entropy_level`, `truncate`, `calculate_coherence_score`) — fonctions pures, sans état, pour le calcul de métriques et la fusion de données.
2. **Widgets custom "Neo-Amiga"** (`GlowButton`, `AdvancedScope`, `EnhancedPatternGrid`, `VUMeter`) — composants graphiques réimplémentés sur `tk.Canvas` pour recréer l'esthétique CRT/néon d'un tracker Amiga.
3. **Application principale** (`BasiliskTrackerProApp`, sous-classe de `tk.Tk`) — assemble le layout, le menu, les hotkeys et la logique de session.
4. **Logique métier** — chargement/sauvegarde de bibliothèque, gestion de séquence, export multi-format, calcul de cohérence, lancement de sous-process (`soneck.py`).

---

## 🖥️ Interface Neo-Amiga : vue d'ensemble

L'interface reprend délibérément les codes visuels des trackers Amiga des années 90 : fond très sombre, palette néon (cyan, magenta, jaune), effets de glow sur les boutons, scanlines simulées, oscilloscope animé.

La fenêtre se divise en quatre zones principales :

- **Barre supérieure** : titre, indicateurs BPM/entropie, jauges VU-mètre (complexité, entropie), oscilloscope multi-canal.
- **Panneau gauche** : sélecteur de canaux (F1–F8), barre de recherche, arborescence de la bibliothèque d'artefacts, zone d'aperçu du texte sélectionné.
- **Zone centrale** : le **pattern editor** — grille façon tracker où chaque ligne représente un artefact inséré dans la séquence, avec ses métadonnées (catégorie, position, complexité, tags), plus une barre de transport (Rewind / Play / Stop / Rec).
- **Panneau droit** : notebook à 5 onglets — `PROMPT` (texte assemblé), `G.TRUTH` (vérité terrain exportable), `ANALYZE` (estimation/métriques), `COHERENCE` (score de cohérence de la séquence), `SONECK` (lancement d'un script externe).

---

## ⚙️ Fonctionnalités détaillées

### Bibliothèque d'artefacts

Chaque artefact possède une **catégorie**, associée à une couleur dédiée dans `CAT_COLORS`. On y trouve deux familles de catégories :

- Des catégories "classiques" d'analyse de discours : `authority`, `assumptions`, `contradictions`, `omissions`, `narrative`, `genealogy`, `ontology`, `bias`, `debate`, `counterprompt`, `temporal`, `affect`.
- Des catégories explicitement offensives/manipulatoires : `basilisk`, `epistemic_hazard`, `memetic_trap`, `ontological_weapon`, `recursive_manipulation`, `value_alignment_trap`, `cognitive_distortion`, `linguistic_trap`, `social_engineering`, `reality_distortion`, `paradox_engine`, `identity_attack`.

### Positionnement narratif

Chaque artefact porte un `position_hint` correspondant à l'une des six phases d'un prompt structuré :

| Code | Phase |
|---|---|
| `OPN` | opening |
| `FRM` | framing |
| `BOD` | body |
| `CNS` | constraint |
| `TRP` | trap |
| `CLS` | closing |

Cette structure suggère un modèle narratif volontairement construit pour amener l'interlocuteur d'un cadrage initial anodin vers un "piège" placé stratégiquement avant la clôture.

### Système de séquence (pattern editor)

- Insertion/suppression d'artefacts à la position du curseur.
- Déplacement de lignes, copier/coller, undo/redo (pile d'historique jusqu'à 100 états).
- Tri automatique par position narrative, randomisation, inversion de séquence.
- Navigation façon tracker (défilement, sélection au clic).

### Recherche & filtres

Barre de recherche en temps réel filtrant la bibliothèque affichée dans le panneau gauche.

### Sessions & presets

- Sauvegarde/chargement de sessions complètes (séquence + métadonnées) dans `sessions/`.
- Sauvegarde de séquences réutilisables comme templates dans `presets/`.
- Application de templates prédéfinis à la séquence courante.

### Analyse de cohérence

Un score de cohérence (0–100) est calculé à partir de la diversité catégorielle et de l'équilibre positionnel de la séquence (détaillé plus bas).

---

## 📦 Format de la bibliothèque JSON

D'après l'usage qu'en fait le code (`artifacts_by_id`, accès à `art["category"]`, `art["label"]`, `art.get("position_hint")`, `art.get("complexity")`, `art.get("tags")`), chaque artefact de `artifacts_basilisk_extended.json` suit vraisemblablement un schéma de ce type :

```json
{
  "id": "identifiant_unique",
  "label": "Libellé court affiché dans la grille",
  "category": "une_des_catégories_ci-dessus",
  "position_hint": "opening | framing | body | constraint | trap | closing",
  "complexity": 1,
  "tags": ["tag1", "tag2"]
}
```

> ⚠️ Le contenu textuel réel de ces artefacts n'est pas reproduit ici. Consultez et manipulez le fichier avec la prudence décrite dans les sections [Précautions](#️-précautions-dutilisation) et [Règles éthiques](#️-rappel-des-règles-éthiques) ci-dessus.

---

## 📊 Système de cohérence & métriques

### `calculate_coherence_score`

Calcule, pour une séquence donnée :

- **Conflits potentiels**, par exemple :
  - `authority` + `counterprompt` → tension épistémique
  - `basilisk` + `affect` → charge émotionnelle critique
  - `contradictions` + `ontology` → risque de paradoxe
- **Synergies**, par exemple :
  - diversité catégorielle ≥ 4 catégories distinctes
  - combinaison `basilisk` + `epistemic_hazard`
  - présence d'un artefact positionné en `trap`
- **Score final** = `(diversité × 0.5 + équilibre positionnel × 0.5) × 100`

### `local_entropy_metrics`

Calcul d'entropie lexicale **sans dépendance externe**, sur la base d'un texte donné :

- **Entropie de Shannon** au niveau des tokens (mesure de la diversité informationnelle)
- **Type-Token Ratio (TTR)** — richesse lexicale
- **Densité lexicale** — proportion de mots "pleins" après filtrage d'une liste de mots vides français (le, la, de, et, que, qui...)

Cette fonction est ensuite reliée à `entropy_level`, qui classe le résultat en `LOW` (< 3.0), `MOD` (3.0–5.0) ou `HIGH` (> 5.0).

---

## ⌨️ Raccourcis clavier

| Touche | Action |
|---|---|
| `F1`–`F8` | Sélectionner un canal (catégorie) |
| `ESPACE` | Play / Stop de la séquence |
| `ENTRÉE` | Insérer l'artefact sélectionné au curseur |
| `SUPPR` | Retirer l'artefact au curseur |
| `CTRL+↑ / ↓` | Déplacer la ligne courante |
| `CTRL+C / V` | Copier / coller une ligne |
| `CTRL+Z / Y` | Annuler / rétablir |
| `CTRL+S` | Sauvegarder la session |
| `CTRL+O` | Charger une session |
| `CTRL+F` | Rechercher dans la bibliothèque |
| `TAB` | Naviguer entre les panneaux |
| `ÉCHAP` | Stop / reset |
| `F3` | Charger une bibliothèque JSON |
| `F5` | Recharger la bibliothèque |
| `F6` | Exporter le prompt (texte) |
| `F7` | Exporter la "ground truth" (JSON) |
| `F8` | Vider la séquence |
| `F9` | Randomiser la séquence |
| `F10` | Trier par position narrative |
| `F11` | Inverser la séquence |
| `F12` | Lancer `soneck.py` |

---

## 🚀 Installation

### Prérequis

- Python 3.8+ avec Tkinter (`python3-tk` sur Debian/Ubuntu : `sudo apt install python3-tk`)
- Aucune dépendance PyPI supplémentaire

### Étapes

```bash
git clone https://github.com/KareyPyer/Basilisk-Tracker.git
cd Basilisk-Tracker
python3 basilisk_tracker_pro.py
```

L'application créera automatiquement, à côté du script, les dossiers `sessions/` et `presets/` s'ils n'existent pas.

---

## 🧭 Utilisation

1. **Charger une bibliothèque** (`F3`) — par défaut, `artifacts_basilisk_extended.json` situé dans le même dossier que le script est chargé automatiquement.
2. **Sélectionner un canal / une catégorie** (`F1`–`F8`) pour filtrer la bibliothèque affichée.
3. **Rechercher** un artefact précis via la barre de recherche (`CTRL+F`).
4. **Insérer** l'artefact sélectionné dans la séquence (double-clic ou `ENTRÉE`).
5. **Réorganiser** la séquence selon le schéma narratif (`opening → framing → body → constraint → trap → closing`), à l'aide du tri automatique (`F10`) ou manuellement.
6. **Consulter l'onglet `COHERENCE`** pour vérifier les conflits/synergies détectés dans la combinaison choisie.
7. **Consulter l'onglet `PROMPT`** pour visualiser le texte assemblé final.
8. **Exporter** (`F6`/`F7`) selon le besoin — voir section suivante.

---

## 📤 Export & formats de sortie

| Format | Contenu | Déclencheur |
|---|---|---|
| `.txt` | Prompt assemblé brut | `F6` / menu Fichier |
| `.md` | Prompt assemblé en Markdown | menu Fichier → "Exporter prompt (.md)" |
| `.html` | Prompt assemblé en HTML | menu Fichier → "Exporter prompt (.html)" |
| `.json` | "Ground truth" — métadonnées de la séquence (catégories, positions, scores) | `F7` / menu Fichier |

L'export "ground truth" est particulièrement important dans une optique de traçabilité : il documente **quels artefacts ont été utilisés, dans quel ordre, avec quel score de cohérence**, ce qui permet de conserver un historique auditable des expérimentations (voir [Précautions d'utilisation](#-précautions-dutilisation), point 4).

---

## 🔗 Intégration `soneck.py`

Le menu `RUN` et l'onglet `SONECK` permettent de :

1. Définir une **racine de projet** (`action_set_project_root`).
2. Lancer un script externe nommé **`soneck.py`** via `subprocess`, dont la sortie s'affiche dans l'onglet dédié.

⚠️ **Ce script n'est pas inclus dans le dépôt actuel.** Son rôle exact (probablement : envoyer le prompt assemblé à une cible — modèle d'IA, service, etc. — pour test) n'est pas documenté dans le code fourni. Toute utilisation de cette fonctionnalité nécessite de fournir soi-même ce script, et engage la responsabilité de l'utilisateur quant à sa cible et son usage.

---

## 🧩 Limitations connues

- **`soneck.py` absent du dépôt** : la fonctionnalité `RUN` est inopérante telle quelle.
- **Pas de fichier de licence** : le statut légal de réutilisation du code n'est pas défini.
- **Pas de tests automatisés** visibles dans le dépôt.
- **Pas de `requirements.txt`** (non strictement nécessaire vu l'absence de dépendances externes, mais absent tout de même pour la traçabilité de version Python).
- **Un seul commit** dans l'historique à ce jour — projet très récent / peu mature.
- **Contenu de la bibliothèque JSON non audité** publiquement à notre connaissance — voir les précautions en tête de document.

---

## 🤝 Contribuer

Le dépôt ne fournit pas de `CONTRIBUTING.md`. Si vous envisagez de contribuer :

- Privilégiez les contributions renforçant le **cadre éthique** (garde-fous, logs, consentement, documentation des risques) plutôt que l'expansion pure de la bibliothèque offensive.
- Documentez toute nouvelle catégorie d'artefact avec son objectif défensif (détection/reconnaissance) plutôt que purement offensif.
- Ouvrez une issue pour discuter de toute modification substantielle avant PR.

---

## 📄 Licence

**Aucune licence n'est actuellement définie dans le dépôt.** En l'absence de licence explicite, le code reste, par défaut, sous copyright exclusif de l'auteur (`KareyPyer`) — cela signifie qu'aucun droit de réutilisation, modification ou redistribution n'est accordé à des tiers sans autorisation explicite. Il est recommandé à l'auteur d'ajouter un fichier `LICENSE` clarifiant les conditions d'usage, idéalement accompagné d'une **charte d'usage éthique** compte tenu de la nature du projet.

---

*README généré à des fins de documentation technique. Ce document ne constitue ni un avis juridique, ni une validation éthique du projet — il rappelle simplement les précautions élémentaires à respecter.*

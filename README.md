# 🐍 Basilisk Tracker PRO — Searchlores v3.0

> *"The Search Is The Program. The Ontology Is The Map."* — Inspiré par Nick Bostrom, Roko's Basilisk, LessWrong, et Fravia (In Memoriam)

---

## ⚠️ **DISCLAIMER &amp; AVERTISSEMENTS**

⚠️ **Ce dépôt contient un outil conçu pour assembler des prompts à visée manipulatrice, déstabilisatrice ou piégeante.**

- **Usage strictement réservé** à la recherche, aux tests de sécurité **offensifs/défensifs**, ou à des fins éducatives **dans un cadre contrôlé et éthique**. 
- **Interdit** pour cibler des individus, des groupes vulnérables, ou des systèmes tiers sans autorisation explicite.
- **Responsabilité légale** : L'utilisateur assume l'entière responsabilité de l'usage qu'il en fait. Toute utilisation malveillante ou non autorisée peut entraîner des conséquences juridiques.
- **Pas de garantie** : Aucune garantie n'est offerte quant à la sécurité, la stabilité ou l'innocuité des sorties générées.

> *"Don't be Evil."* — **Respectez cette règle.**

---

## 📌 **À propos du projet**

**Basilisk Tracker PRO** est une application de bureau (Python/Tkinter) qui reprend l'interface d'un **tracker musical façon Amiga** (comme ProTracker ou OctaMED), mais appliquée à l'assemblage de **prompts textuels structurés**. 

Au lieu de composer des notes de musique, vous **composez des prompts** en enchaînant des **"artefacts"** (fragments de texte catégorisés) sur une grille de type *pattern editor*. Le résultat est un prompt final structuré selon un schéma narratif fixe :

```
opening → framing → body → constraint → trap → closing
```

### 🎯 **Objectifs**

- **Recherche** : Cartographier et analyser les mécanismes de manipulation épistémique (biais, pièges narratifs, distorsions ontologiques).
- **Sécurité** : Tester la robustesse des modèles de langage face à des prompts adversariaux.
- **Éducation** : Sensibiliser aux risques liés aux **"epistemic hazards"**, **"memetic traps"**, et autres **"ontological weapons"**.
- **Défense** : Développer des contre-mesures pour détecter et neutraliser ces schémas.

---

## 🗂️ **Structure du dépôt**


| Fichier/Repertoire                                                                                                             | Description                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| [`basilisk_tracker_pro.py`](https://github.com/KareyPyer/Basilisk-Tracker/blob/main/basilisk_tracker_pro.py)                   | **Application principale** (Python/Tkinter). Interface complète avec widgets custom, *pattern editor*, et logique métier.                 |
| [`artifacts_basilisk_extended.json`](https://github.com/KareyPyer/Basilisk-Tracker/blob/main/artifacts_basilisk_extended.json) | **Bibliothèque d'artefacts** : Ensemble de fragments textuels catégorisés (ex: `epistemic_hazard`, `memetic_trap`, `ontological_weapon`). |
| [`basilisk_prompt.txt`](https://github.com/KareyPyer/Basilisk-Tracker/blob/main/basilisk_prompt.txt)                           | Exemple de prompt de base.                                                                                                                |
| [`sessions/`](https://github.com/KareyPyer/Basilisk-Tracker/tree/main/sessions)                                                | Dossier pour sauvegarder/charger des **sessions** (séquences + métadonnées).                                                              |
| [`presets/`](https://github.com/KareyPyer/Basilisk-Tracker/tree/main/presets)                                                  | Dossier pour les **templates réutilisables**.                                                                                             |
| [`Groked-Basilisk.json`](https://github.com/KareyPyer/Basilisk-Tracker/blob/main/Groked-Basilisk.json)                         | Bibliothèque alternative ou complémentaire.                                                                                               |
| **Autres fichiers** (`Analyse Kimi.txt`, `Rapport Chandra.md`, etc.)                                                           | Notes d'analyse, rapports, et documents de recherche liés au projet.                                                                      |


---

## 🏗️ **Architecture technique**

### **Stack**

- **Langage** : Python 3.8+ (100% du code).
- **UI** : `tkinter` / `ttk` (aucune dépendance externe).
- **Stdlib uniquement** : `json`, `math`, `os`, `random`, `subprocess`, `sys`, `tempfile`, `re`, `pathlib`, `datetime`, `collections`.

✅ **Aucune dépendance tierce** : Pas besoin de `pip install`.

### **Fonctionnalités clés**


| Fonctionnalité               | Description                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------------- |
| **Pattern Editor**           | Grille façon *tracker Amiga* pour assembler des artefacts textuels.                            |
| **Bibliothèque d'artefacts** | Fragments textuels catégorisés (ex: `basilisk`, `epistemic_hazard`, `recursive_manipulation`). |
| **Système de cohérence**     | Calcul automatique de la **cohérence** (0–100) et détection des conflits/synergies.            |
| **Métriques d'entropie**     | Mesure de la complexité lexicale (Shannon, TTR, densité lexicale).                             |
| **Export multi-format**      | `.txt`, `.md`, `.html`, `.json` (ground truth pour traçabilité).                               |
| **Sessions &amp; Presets**   | Sauvegarde/chargement de séquences et templates.                                               |
| **Intégration `soneck.py`**  | Lancement de scripts externes (à fournir par l'utilisateur).                                   |


---

## 🖥️ **Interface Neo-Amiga**

L'interface s'inspire des **trackers musicaux des années 90** (ProTracker, OctaMED) avec :

- **Thème sombre** + palette néon (cyan, magenta, jaune).
- **Effets de glow** sur les boutons et widgets.
- **Scanlines** et **oscilloscope animé** pour un rendu rétro.

### **Zones principales**

1. **Barre supérieure** : Titre, indicateurs (BPM, entropie), jauges VU-mètre (complexité, entropie), oscilloscope.
2. **Panneau gauche** : Sélecteur de canaux (F1–F8), barre de recherche, arborescence de la bibliothèque, aperçu des artefacts.
3. **Zone centrale** : *Pattern Editor* (grille pour assembler les artefacts).
4. **Panneau droit** : Onglets (`PROMPT`, `G.TRUTH`, `ANALYZE`, `COHERENCE`, `SONECK`).

---

## 📦 **Format de la bibliothèque JSON**

Chaque **artefact** dans `artifacts_basilisk_extended.json` suit ce schéma :

```json
{
  "id": "identifiant_unique",
  "label": "Libellé court",
  "category": "catégorie (ex: epistemic_hazard, memetic_trap)",
  "position_hint": "OPN|FRM|BOD|CNS|TRP|CLS",
  "complexity": 1,
  "tags": ["tag1", "tag2"]
}
```

### **Catégories disponibles**


| Type           | Exemples                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------- |
| **Classiques** | `authority`, `assumptions`, `contradictions`, `omissions`, `narrative`, `bias`, `debate`       |
| **Offensives** | `basilisk`, `epistemic_hazard`, `memetic_trap`, `ontological_weapon`, `recursive_manipulation` |
| **Autres**     | `identity_attack`, `reality_distortion`, `paradox_engine`, `social_engineering`                |


---

## 📊 **Système de cohérence &amp; métriques**

### **Score de cohérence (0–100)**

Calculé à partir de :

- **Diversité catégorielle** (plus il y a de catégories distinctes, mieux c'est).
- **Équilibre positionnel** (répartition des artefacts dans les phases `OPN`→`CLS`).
- **Conflits/Synergies** : Certaines combinaisons sont détectées automatiquement (ex: `basilisk` + `affect` = charge émotionnelle critique).

### **Métriques d'entropie**

- **Entropie de Shannon** : Mesure de la diversité informationnelle.
- **Type-Token Ratio (TTR)** : Richesse lexicale.
- **Densité lexicale** : Proportion de mots "pleins" (après filtrage des mots vides).

---

## ⌨️ **Raccourcis clavier**


| Touche     | Action                             |
| ---------- | ---------------------------------- |
| `F1`–`F8`  | Sélectionner un canal (catégorie)  |
| `ESPACE`   | Play / Stop de la séquence         |
| `ENTRÉE`   | Insérer l'artefact sélectionné     |
| `SUPPR`    | Retirer l'artefact au curseur      |
| `CTRL+↑/↓` | Déplacer la ligne courante         |
| `CTRL+C/V` | Copier / Coller une ligne          |
| `CTRL+Z/Y` | Annuler / Rétablir                 |
| `CTRL+S`   | Sauvegarder la session             |
| `CTRL+O`   | Charger une session                |
| `CTRL+F`   | Rechercher dans la bibliothèque    |
| `TAB`      | Naviguer entre les panneaux        |
| `ÉCHAP`    | Stop / Reset                       |
| `F3`       | Charger une bibliothèque JSON      |
| `F5`       | Recharger la bibliothèque          |
| `F6`       | Exporter le prompt (.txt)          |
| `F7`       | Exporter la "ground truth" (.json) |
| `F8`       | Vider la séquence                  |
| `F9`       | Randomiser la séquence             |
| `F10`      | Trier par position narrative       |
| `F11`      | Inverser la séquence               |
| `F12`      | Lancer `soneck.py`                 |


---

## 🚀 **Installation**

### **Prérequis**

- Python 3.8+ avec **Tkinter** activé.
  - Sur **Debian/Ubuntu** : `sudo apt install python3-tk`
  - Sur **macOS** : Tkinter est inclus par défaut avec Python.
  - Sur **Windows** : Tkinter est généralement inclus avec Python.

### **Étapes**

1. Cloner le dépôt :
  ```bash
   git clone https://github.com/KareyPyer/Basilisk-Tracker.git
   cd Basilisk-Tracker
  ```
2. Lancer l'application :
  ```bash
   python3 basilisk_tracker_pro.py
  ```

✅ **Aucune dépendance supplémentaire** n'est requise.

---

## 🧭 **Utilisation**

1. **Charger une bibliothèque** (`F3`) : Par défaut, `artifacts_basilisk_extended.json` est chargé automatiquement.
2. **Sélectionner un canal/catégorie** (`F1`–`F8`) pour filtrer la bibliothèque.
3. **Rechercher un artefact** (`CTRL+F`) dans la bibliothèque.
4. **Insérer un artefact** (double-clic ou `ENTRÉE`) dans la séquence.
5. **Réorganiser la séquence** :
  - Manuellement (glisser-déposer ou `CTRL+↑/↓`).
  - Automatiquement (`F10` pour trier par position narrative).
6. **Vérifier la cohérence** : Onglet `COHERENCE` pour voir les conflits/synergies.
7. **Visualiser le prompt final** : Onglet `PROMPT`.
8. **Exporter** (`F6` pour `.txt`, `F7` pour `.json`).

---

## 📤 **Export &amp; Formats de sortie**


| Format  | Contenu                                                                                    | Déclencheur         |
| ------- | ------------------------------------------------------------------------------------------ | ------------------- |
| `.txt`  | Prompt assemblé (texte brut).                                                              | `F6` / Menu Fichier |
| `.md`   | Prompt assemblé en Markdown.                                                               | Menu Fichier        |
| `.html` | Prompt assemblé en HTML.                                                                   | Menu Fichier        |
| `.json` | **Ground Truth** : Métadonnées de la séquence (artefacts, positions, scores de cohérence). | `F7` / Menu Fichier |


> ⚠️ **L'export "Ground Truth"** est **obligatoire** pour la traçabilité des expérimentations (voir [Précautions](#-précautions-dutilisation)).

---

## 🔗 **Intégration avec `soneck.py`**

Le menu **`RUN`** et l'onglet **`SONECK`** permettent de :

1. Définir une **racine de projet**.
2. Lancer un script externe **`soneck.py`** (via `subprocess`).

⚠️ **Attention** :

- `soneck.py` **n'est pas inclus** dans le dépôt.
- Son rôle exact n'est pas documenté (probablement pour envoyer le prompt à un modèle d'IA ou un service tiers).
- **Fournissez votre propre script** et assurez-vous qu'il respecte les règles éthiques et légales.

---

## 🛡️ **Précautions d'utilisation**

Avant toute utilisation, **lisez attentivement** cette section.

### **✅ À FAIRE**

1. **Limiter l'usage** à un **environnement contrôlé et isolé** (sandbox, VM dédiée, projet de recherche documenté).
2. **Documenter systématiquement** chaque session (utilisez l'export *Ground Truth*).
3. **Vérifier la légalité locale** : La manipulation psychologique et le harcèlement numérique sont **pénalement sanctionnés** dans de nombreuses juridictions.
4. **Obtenir un consentement éclairé** pour toute expérimentation impliquant des tiers.

### **❌ À NE PAS FAIRE**

1. **Ne jamais déployer** les prompts générés contre des **humains vulnérables** (mineurs, personnes en détresse psychologique, etc.).
2. **Ne jamais utiliser** l'outil pour contourner les garde-fous d'un modèle d'IA **sans autorisation du fournisseur** (violation des CGU).
3. **Ne pas publier ni diffuser** les sorties générées sans revue éthique préalable.
4. **Ne pas cibler des individus** nommément ou des groupes vulnérables.

---

## ⚖️ **Règles éthiques**

Ce projet relève de la **"red team" épistémique** : son objectif est de **cartographier les mécanismes de manipulation pour mieux les reconnaître et s'en défendre**, **pas pour les déployer offensivement**.

### **Principes directeurs**

1. **Finalité défensive** : L'étude, la classification et la détection des schémas manipulateurs sont les seuls usages légitimes.
2. **Consentement et transparence** : Toute expérimentation impliquant un tiers doit se faire avec son **accord explicite** ou dans un cadre de recherche encadré (comité d'éthique, bug bounty officiel).
3. **Pas de ciblage individuel** : Aucun prompt ne doit viser à manipuler une personne nommée ou identifiable.
4. **Responsabilité de l'opérateur** : L'outil ne fait qu'assembler des fragments. **Vous êtes responsable** du prompt final et de son usage.
5. **Principe de réversibilité** : Si vous ne seriez pas à l'aise d'expliquer publiquement pourquoi vous avez généré ce prompt, **ne le faites pas**.

---

## 🧩 **Limitations connues**


| Limitation                    | Description                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| **`soneck.py` manquant**      | La fonctionnalité `RUN` est inopérante sans ce script.                                       |
| **Pas de licence**            | Aucune licence n'est définie (copyright par défaut).                                         |
| **Pas de tests automatisés**  | Aucun test unitaire ou d'intégration n'est fourni.                                           |
| **Pas de `requirements.txt`** | Non strictement nécessaire (pas de dépendances externes), mais manquant pour la traçabilité. |
| **Bibliothèque non auditée**  | Le contenu de `artifacts_basilisk_extended.json` n'a pas été audité publiquement.            |
| **Projet récent**             | Un seul commit à ce jour (juillet 2026). Projet en développement actif.                      |


---

## 🤝 **Contribuer**

Les contributions sont les bienvenues, **à condition de respecter les principes éthiques** du projet.

### **Comment contribuer ?**

1. **Ouvrir une *Issue*** pour discuter de votre idée avant de soumettre une PR.
2. **Privilégier les contributions défensives** :
  - Améliorer les garde-fous.
  - Ajouter des métriques de détection de risques.
  - Documenter les catégories d'artefacts avec leur objectif **défensif** (détection/reconnaissance).
3. **Éviter les contributions purement offensives** (expansion de la bibliothèque sans cadre éthique clair).

### **Exemples de contributions acceptables**

- Ajout de **nouveaux types de métriques** (ex: détection de biais, analyse de toxicité).
- Amélioration de l'**interface utilisateur** (meilleure visualisation des risques).
- **Documentation** (ex: guide d'utilisation éthique, exemples de cas d'usage défensifs).
- **Tests automatisés** pour valider la cohérence et la sécurité.

---

## 📄 **Licence**

**Aucune licence** n'est actuellement définie dans le dépôt.

- **Par défaut**, le code est sous **copyright exclusif** de l'auteur (`KareyPyer`).
- **Aucun droit de réutilisation, modification ou redistribution** n'est accordé sans autorisation explicite.

⚠️ **Recommandation** :

- L'auteur devrait ajouter un fichier **`LICENSE`** (ex: MIT, GPL) pour clarifier les conditions d'usage.
- Une **charte d'usage éthique** devrait accompagner la licence, compte tenu de la nature sensible du projet.

---

## 📚 **Ressources supplémentaires**

- **Site web** : [basilisk-tracker.netlify.app](https://basilisk-tracker.netlify.app) (lien fourni dans le dépôt).
- **Inspirations** :
  - [Roko's Basilisk](https://en.wikipedia.org/wiki/Roko%27s_basilisk) (LessWrong).
  - [Searchlores](http://searchlores.org) (Fravia, In Memoriam).
  - [Nick Bostrom](https://en.wikipedia.org/wiki/Nick_Bostrom) (risques existentiels liés à l'IA).

---

## 🙏 **Remerciements**

- À **Fravia** (1963–2009), pionnier de la "recherche comme discipline épistémologique".
- À la communauté **LessWrong** pour ses travaux sur les risques épistémiques.
- À tous ceux qui œuvrent pour une **IA éthique et responsable**.

---

> *"The Search Is The Program. The Ontology Is The Map."*  
> **Utilisez cet outil avec sagesse.**

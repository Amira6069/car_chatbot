
# 🚗 Chatbot Automobile Intelligent

Bienvenue sur le **Chatbot Automobile Intelligent**, un assistant avancé propulsé par l'IA, conçu pour comprendre vos questions sur les voitures en **Anglais**, **Français**, ou **Dialecte Tunisien**.

Contrairement aux bots basiques, ce système utilise un **Grand Modèle de Langage (LLM)** pour saisir vos intentions complexes et un **Détecteur Hors-Domaine (OOD)** pour rester concentré sur son expertise automobile.

---

## 🏗️ Architecture & Flux (Comment ça marche ?)

L'application suit une architecture robuste de type "Retrieve & Generate". Voici le trajet exact d'une requête utilisateur :

### 1. 📥 Entrée & Traitement du Langage
- **Fichier** : `app2.py` → `language_processor.py`
- **Action** : L'utilisateur parle. Le système détecte la langue.
- **Magie** : Si l'utilisateur parle en **Tunisien** (ex: *"nheb karhba rkhissa"*), c'est traduit automatiquement en Anglais (*"I want a cheap car"*) avant d'être traité.

### 2. 🛡️ Le Gardien (Détection OOD)
- **Fichier** : `ood_detector.py`
- **Action** : Avant d'utiliser des ressources coûteuses, le système vérifie : *"Est-ce que ça parle vraiment de voitures ?"*
- **Technologie** : Utilise **TF-IDF Vectorization** + **One-Class SVM**.
- **Résultat** : 
  - "Recette de pizza ?" ❌ Bloqué immédiatement.
  - "Prix d'une Toyota ?" ✅ Passe au Cerveau.

### 3. 🧠 Le Cerveau (Analyse d'Intention)
- **Fichier** : `llm_analyzer.py`
- **Technologie** : **Groq API** (Modèle Llama-3.3-70B).
- **Action** : Le LLM analyse le texte pour extraire des données structurées (JSON).
- **Exemple** : 
  - *Entrée* : "Une BMW pas chère"
  - *Sortie* : `{"intent": "search", "entities": {"make": "bmw", "sort_order": "price_asc"}}`

### 4. 🔧 Le Moteur (Exécution de la Requête)
- **Fichier** : `smart_query_builder.py`
- **Action** : Prend le JSON structuré et construit une requête **Pandas** complexe pour filtrer le fichier `data/cars2.csv`.
- **Capacités** : Gère les filtres de prix, taille, transmission, et génère un affichage détaillé type catalogue.

---

## 🚀 Installation & Lancement

1. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurer l'environnement** :
   Créez un fichier `.env` et ajoutez votre Clé API Groq :
   ```env
   GROQ_API_KEY=votre_cle_api_ici
   ```

3. **Lancer l'application** :
   ```bash
   python app2.py
   ```
   *Le serveur démarrera sur `http://127.0.0.1:5000`*

4. **Lancer les tests** :
   ```bash
   python test_chatbot.py
   ```

---

## 🧪 Scénarios de Démo (Prêts pour la Présentation)

Utilisez ces requêtes exactes pour démontrer toute la puissance de votre projet au professeur.

### 1️⃣ Recherche Budgétaire & Tri (🆕 Nouveau !)
*Objectif : Montrer que le bot comprend "pas cher" et trie les résultats.*

-   **Utilisateur** : "I want a cheap toyota" (Ou en Tunisien "nheb toyota rkhissa")
    *   **Logique** : Détecte `sort_order: price_asc`
    *   **Résultat** : Affiche les Toyota les moins chères en premier (ex: Toyota Yaris, Tercel...).


### 3️⃣ Filtres & Logique Min/Max
*Objectif : Montrer la gestion des chiffres.*

-   **Utilisateur** : "I want a BMW between 5k and 20k"
    *   **Logique** : `min_price=5000`, `max_price=20000`
    *   **Résultat** : Liste les BMW dans ce budget exact.

### 4️⃣ Multilingue & Dialecte (L'Effet Wow)
*Objectif : Montrer la traduction en temps réel.*

-   **Utilisateur** : "b9addech el golf mawjouda ?"
    *   **Interne** : Traduit en *"how much is golf available"*
    *   **Résultat** : Fiche technique et prix de la Volkswagen Golf.

### 5️⃣ Détails & Spécifications (Affichage Riche)
*Objectif : Montrer le nouvel affichage détaillé.*

-   **Utilisateur** : "give me details about audi a4"
    *   **Résultat** : Affiche une fiche complète (Prix, MPG Ville/Autoroute, Cheval-vapeur, Style...).

---

## 📁 Structure du Projet

| Fichier | Rôle |
|---------|------|
| `app2.py` | Application Principale (Serveur Flask) |
| `language_processor.py` | Traducteur (Gère le Tunisien) |
| `ood_detector.py` | Sécurité (Bloque les questions hors-sujet) |
| `llm_analyzer.py` | **Cerveau IA** : Convertit le texte en intentions JSON |
| `smart_query_builder.py` | Moteur de Recherche : Filtre et formate les données |
| `data/cars2.csv` | La Base de Données |

---
*Projet réalisé par Hejer pour le cours de Data Science Avancée.*
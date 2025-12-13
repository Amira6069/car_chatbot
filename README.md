
# 🚗 Intelligent Car Chatbot

Welcome to the **Intelligent Car Chatbot**, an advanced AI-powered assistant designed to understand natural language queries about cars, whether in **English**, **French**, or **Tunisian Dialect**.

Unlike simple rule-based bots, this system uses a **Large Language Model (LLM)** to understand complex intents and an **Out-Of-Domain (OOD) Detector** to stay focused on its expertise.

---

## 🏗️ Architecture & Flow (How it Works)

The application follows a robust "Retrieve & Generate" pipeline. Here is the exact journey of a user query:

### 1. 📥 Input & Language Processing
- **File**: `app2.py` → `language_processor.py`
- **Action**: The user speaks. The system detects the language.
- **Magic**: If the user speaks **Tunisian Dialect** (e.g., *"nheb karhba rkhissa"*), it is automatically translated to standardized English (*"I want a cheap car"*) before processing.

### 2. 🛡️ The Guardian (OOD Detection)
- **File**: `ood_detector.py`
- **Action**: Before using expensive resources, the system checks: *"Is this actually about cars?"*
- **Tech**: Uses **TF-IDF Vectorization** + **One-Class SVM**.
- **Outcome**: 
  - "Chicken recipe?" ❌ Blocked immediately.
  - "Toyota price?" ✅ Passed to the Brain.

### 3. 🧠 The Brain (Intent Analysis)
- **File**: `llm_analyzer.py`
- **Tech**: **Groq API** (Llama-3.3-70B model).
- **Action**: The LLM analyzes the English text to extract structured data (JSON).
- **Example**: 
  - *Input*: "BMW under 20k"
  - *Output*: `{"intent": "search", "entities": {"make": "bmw", "max_price": 20000}}`

### 4. 🔧 The Engine (Query Execution)
- **File**: `smart_query_builder.py`
- **Action**: Takes the structured JSON and builds a **Pandas** query to filter the dataset (`data/cars2.csv`).
- **Logic**: It handles sorting, filtering (min/max price, year), and specific requests like "Fuel Economy".

---

## 🚀 Setup & Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```

3. **Run the Application**:
   ```bash
   python app2.py
   ```
   *The server will start at `http://127.0.0.1:5000`*

4. **Testing (Unit Tests)**:
   ```bash
   python test_bot.py
   ```

---

## 🧪 Demo Scenarios (Ready for Presentation)

Use these queries to demonstrate the full capabilities of the bot to your professor.

### 1️⃣ Basic Search & OOD (The Basics)
*Target: Show that the bot works and stays on topic.*

-   **User**: "Hello my friend"
    *   **Response**: *Rejected (Out-Of-Domain).*
-   **User**: "Show me all Toyota cars"
    *   **Response**: *Returns a list of Toyota cars.*

### 2️⃣ Multilingual & Tunisian Dialect (The "Wow" Factor)
*Target: Show the translation pipeline.*

-   **User**: "b9addech el golf mawjouda ?" (Combien coûte la Golf ?)
    *   **Internal**: Translated to *"how much is golf available"*
    *   **Response**: *Detailed price and specs for Volkswagen Golf.*

### 3️⃣ Advanced Filtering (The Technical Part)
*Target: Show the Min/Max logic we implemented.*

-   **User**: "I want a BMW between 5k and 20k"
    *   **Logic**: `min_price=5000`, `max_price=20000`
    *   **Response**: *Lists BMWs within that specific budget.*

### 4️⃣ Specific Specs & Formatting
*Target: Show entity extraction precision.*

-   **User**: "How much fuel does a Toyota Previa consume?"
    *   **Logic**: Detects `fuel_efficiency=True`
    *   **Response**: *Focuses specifically on City/Highway MPG.*

### 5️⃣ Comparison
*Target: Show complex multi-entity handling.*

-   **User**: "Compare BMW M6 and Toyota Camry"
    *   **Response**: *Side-by-side technical comparison.*

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `app2.py` | Main Flask application (Controller) |
| `language_processor.py` | Handes Dialect/Language translation |
| `ood_detector.py` | Filters irrelevant queries (Security) |
| `llm_analyzer.py` | **The AI Brain**: Extracts intents & entities |
| `smart_query_builder.py` | Query Engine: Filters the CSV data |
| `data/cars2.csv` | The Database |

---
*Created by Hejer for the Advanced Data Science Project.*
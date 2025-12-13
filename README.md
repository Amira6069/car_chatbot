
# 🚗 Intelligent Automotive Chatbot

Welcome to the **Intelligent Automotive Chatbot**, an advanced AI-powered assistant designed to understand your car questions in **English**, **French**, or **Tunisian Dialect**.

Unlike basic bots, this system uses a **Large Language Model (LLM)** to grasp complex intents and an **Out-Of-Domain (OOD) Detector** to stay focused on its automotive expertise.

---

## 🏗️ Architecture & Flow (How it works?)

The application follows a robust "Retrieve & Generate" architecture. Here is the exact journey of a user request:

### 1. 📥 Input & Language Processing
- **File**: `app2.py` → `language_processor.py`
- **Action**: The user speaks. The system detects the language.
- **Magic**: If the user speaks in **Tunisian** (e.g., *"nheb karhba rkhissa"*), it is automatically translated to English (*"I want a cheap car"*) before being processed.

### 2. 🛡️ The Guardian (OOD Detection)
- **File**: `ood_detector.py`
- **Action**: Before using expensive resources, the system checks: *"Is this really about cars?"*
- **Technology**: Uses **TF-IDF Vectorization** + **One-Class SVM**.
- **Result**: 
  - "Pizza recipe?" ❌ Blocked immediately.
  - "Price of a Toyota?" ✅ Passes to the Brain.

### 3. 🧠 The Brain (Intent Analysis)
- **File**: `llm_analyzer.py`
- **Technology**: **Groq API** (Llama-3.3-70B Model).
- **Action**: The LLM analyzes the text to extract structured data (JSON).
- **Example**: 
  - *Input*: "A cheap BMW"
  - *Output*: `{"intent": "search", "entities": {"make": "bmw", "sort_order": "price_asc"}}`

### 4. 🔧 The Engine (Query Execution)
- **File**: `smart_query_builder.py`
- **Action**: Takes the structured JSON and builds a complex **Pandas** query to filter the `data/cars2.csv` file.
- **Capabilities**: Handles price, size, transmission filters, and generates a detailed catalog-style display.

---

## 🚀 Installation & Launch

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure usage environment**:
   Create a `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

3. **Launch the application**:
   ```bash
   python app2.py
   ```
   *The server will start on `http://127.0.0.1:5000`*

4. **Run tests**:
   ```bash
   python test_chatbot.py
   ```

---

## 🧪 Demo Scenarios (Ready for Presentation)

Use these exact requests to demonstrate the full power of your project to the professor.

### 1️⃣ Budget Search & Sort (🆕 New!)
*Objective: Show that the bot understands "cheap" and sorts results.*

-   **User**: "I want a cheap toyota" (Or in Tunisian "nheb toyota rkhissa")
    *   **Logic**: Detects `sort_order: price_asc`
    *   **Result**: Displays the cheapest Toyotas first (e.g., Toyota Yaris, Tercel...).


### 3️⃣ Filters & Min/Max Logic
*Objective: Show number handling.*

-   **User**: "I want a BMW between 5k and 20k"
    *   **Logic**: `min_price=5000`, `max_price=20000`
    *   **Result**: Lists BMWs within this exact budget.

### 4️⃣ Multilingual & Dialect (The Wow Effect)
*Objective: Show real-time translation.*

-   **User**: "b9addech el golf mawjouda ?"
    *   **Internal**: Translated to *"how much is golf available"*
    *   **Result**: Spec sheet and price of the Volkswagen Golf.

### 5️⃣ Details & Specifications (Rich Display)
*Objective: Show the new detailed display.*

-   **User**: "give me details about audi a4"
    *   **Result**: Displays a full sheet (Price, MPG City/Highway, Horsepower, Style...).

---

## 📁 Project Structure

| File | Role |
|---------|------|
| `app2.py` | Main Application (Flask Server) |
| `language_processor.py` | Translator (Handles Tunisian) |
| `ood_detector.py` | Security (Blocks off-topic questions) |
| `llm_analyzer.py` | **AI Brain**: Converts text to JSON intents |
| `smart_query_builder.py` | Search Engine: Filters and formats data |
| `data/cars2.csv` | The Database |

---
*Project realized by Hejer for the Advanced Data Science course.*
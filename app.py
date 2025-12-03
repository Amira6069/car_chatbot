import streamlit as st
from language_processor import LanguageProcessor
from intent_classifier import IntentClassifier
from query_handler import QueryHandler
from external_handler import ExternalHandler

# Page configuration
st.set_page_config(
    page_title="Car Chatbot",
    page_icon="🚗",
    layout="wide"
)

# Initialize components
@st.cache_resource
def load_components():
    lang_processor = LanguageProcessor()
    intent_classifier = IntentClassifier()
    query_handler = QueryHandler('data/cars.csv')
    external_handler = ExternalHandler()
    return lang_processor, intent_classifier, query_handler, external_handler

# Sidebar
with st.sidebar:
    st.title("🚗 Car Chatbot")
    st.markdown("---")
    st.markdown("### Features:")
    st.markdown("✓ Multilingual (EN/AR/TN)")
    st.markdown("✓ Car prices & specs")
    st.markdown("✓ Availability check")
    st.markdown("✓ Model comparison")
    st.markdown("---")
    
    page = st.radio("Navigate:", ["💬 Chat", "📊 Car Catalog", "ℹ️ About"])

# Load components
lang_processor, intent_classifier, query_handler, external_handler = load_components()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# CHAT PAGE
if page == "💬 Chat":
    st.title("💬 Car Chatbot Assistant")
    st.caption("Ask me about car prices, availability, specs, or comparisons!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question... (English, Arabic, or Tunisian)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process message
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                # Step 1-3: Language Processing
                english_text, detected_lang = lang_processor.process(prompt)
                
                if detected_lang != 'en':
                    st.caption(f"🌍 Detected: {detected_lang.upper()} → Translated to English")
                
                # Step 4: Intent Classification with OCSVM
                intent = intent_classifier.classify(english_text)
                
                # Display OCSVM result
                if not intent_classifier.is_car_related(english_text):
                    st.caption("🔍 OCSVM: Question classified as OUT-OF-DOMAIN (general)")
                else:
                    st.caption(f"🔍 OCSVM: Question classified as IN-DOMAIN (car-related) → Intent: {intent}")
                
                # Step 5: Query Processing or External Handling
                if intent == 'general':
                    response = external_handler.handle_general_question(english_text)
                else:
                    # Extract car names
                    car_names = intent_classifier.extract_car_name(english_text)
                    
                    # Route to appropriate handler
                    if intent == 'price':
                        response = query_handler.get_price(car_names)
                    elif intent == 'availability':
                        response = query_handler.get_availability(car_names)
                    elif intent == 'model' or intent == 'general_car':
                        response = query_handler.get_specs(car_names)
                    elif intent == 'comparison':
                        response = query_handler.compare_cars(car_names)
                    else:
                        response = "I can help with car prices, availability, specs, and comparisons. Please ask about a specific car!"
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# CAR CATALOG PAGE
elif page == "📊 Car Catalog":
    st.title("📊 Available Cars")
    
    if query_handler.df is not None:
        st.dataframe(query_handler.df.head(20), use_container_width=True)
        st.caption(f"Showing {len(query_handler.df)} cars in inventory")
    else:
        st.error("Dataset not loaded. Please add cars.csv to data/ folder")

# ABOUT PAGE
elif page == "ℹ️ About":
    st.title("ℹ️ About This Chatbot")
    
    st.markdown("""
    ### 🎯 What can I do?
    
    This chatbot can help you with:
    - **Car Prices**: Ask "How much is a Toyota Corolla?"
    - **Availability**: Ask "Is BMW X5 available?"
    - **Specifications**: Ask "Tell me about Honda Civic specs"
    - **Comparisons**: Ask "Compare Toyota Camry and Honda Accord"
    
    ### 🌍 Languages Supported
    - English
    - Arabic (العربية)
    - Tunisian Dialect (تونسي)
    
    ### 🔄 How it works
    1. You ask a question in any supported language
    2. System detects and translates to English (3-step process)
    3. **OCSVM classifies if question is car-related or general**
    4. If car-related: further classifies intent (price, availability, specs, etc.)
    5. Searches our car database and returns relevant information
    6. If general: redirects to external service
    
    ### 🤖 What is OCSVM?
    **One-Class SVM (Support Vector Machine)** is a machine learning algorithm for anomaly detection:
    - **Trained on car-related questions** (normal/in-domain)
    - **Identifies outliers** (general questions that are out-of-domain)
    - **Improves accuracy** compared to simple keyword matching
    - Automatically learns patterns in car questions
    
    ### ⚠️ Limitations
    - Only answers car-related questions from our database
    - General questions are redirected to external services
    """)
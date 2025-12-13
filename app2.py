from flask import Flask, render_template, request, jsonify
import traceback
import os

app = Flask(__name__)

print("="*60)
print("🚀 Starting Intelligent Car Chatbot...")
print("="*60)

# Initialize all components
lang_proc = None
llm_analyzer = None
query_builder = None
external_handler = None
ood_detector = None

# 1. Language Processor
try:
    print("Loading language processor...")
    from language_processor import LanguageProcessor
    lang_proc = LanguageProcessor()
    print("✅ Language processor loaded")
except Exception as e:
    print(f"❌ Language processor error: {e}")
    traceback.print_exc()

# 2. LLM Analyzer (NEW - replaces intent_classifier)
try:
    print("Loading LLM analyzer...")
    from llm_analyzer import LLMAnalyzer
    llm_analyzer = LLMAnalyzer()
    print("✅ LLM analyzer loaded")
except Exception as e:
    print(f"❌ LLM analyzer error: {e}")
    print("   ⚠️  Make sure GROQ_API_KEY is set in .env file!")
    traceback.print_exc()

# 3. Smart Query Builder (NEW - replaces query_handler)
try:
    print("Loading smart query builder...")
    from smart_query_builder import SmartQueryBuilder
    query_builder = SmartQueryBuilder('data/cars2.csv')
    print("✅ Smart query builder loaded")
except Exception as e:
    print(f"❌ Query builder error: {e}")
    traceback.print_exc()

# 4. External Handler (EXISTING - keep as is)
try:
    print("Loading external handler...")
    from external_handler import ExternalHandler
    external_handler = ExternalHandler()
    print("✅ External handler loaded")
except Exception as e:
    print(f"❌ External handler error: {e}")
    traceback.print_exc()

# 5. OOD Detector (EXISTING - keep as is)
try:
    print("Loading OOD detector...")
    from ood_detector import OODDetector
    ood_detector = OODDetector(dataset_path='data/cars2.csv')
    print("✅ OOD detector loaded")
except Exception as e:
    print(f"⚠️  OOD detector error: {e}")
    traceback.print_exc()

print("="*60)
if all([lang_proc, llm_analyzer, query_builder]):
    print("✅ CORE COMPONENTS READY!")
else:
    print("⚠️  SOME COMPONENTS FAILED")
print("="*60 + "\n")

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        print(f"\n{'='*60}")
        print(f"📝 User: '{user_message}'")
        
        if not user_message:
            return jsonify({'error': 'No message'}), 400
        
        if not all([lang_proc, llm_analyzer, query_builder]):
            return jsonify({'error': 'System not ready'}), 500
        
        # STEP 1: Language Processing
        english_text, detected_lang = lang_proc.process(user_message)
        print(f"✅ Translated: '{english_text}' (lang: {detected_lang})")
        
        # STEP 2: OOD Detection
        if ood_detector:
            try:
                in_domain, ood_score = ood_detector.is_in_domain(english_text)
                print(f"🔎 OOD: score={ood_score:.3f}, in_domain={in_domain}")
                
                if not in_domain:
                    print("⚠️  OUT-OF-DOMAIN detected")
                    response = external_handler.handle_general_question(english_text)
                    
                    return jsonify({
                        'response': response,
                        'detected_language': str(detected_lang),
                        'translated_to': english_text if detected_lang != 'en' else None,
                        'intent': 'OUT-OF-DOMAIN',
                        'ood_score': ood_score
                    })
            except Exception as e:
                print(f"⚠️  OOD check failed: {e}")
        
        # STEP 3: LLM Analysis
        try:
            llm_analysis = llm_analyzer.analyze_query(english_text)
            print(f"🧠 Intent: {llm_analysis['intent']}")
            
            # Handle LLM Failure
            if llm_analysis['intent'] == 'error':
                 return jsonify({
                    'response': f"⚠️ **System Error:** I'm having trouble connecting to my brain.\n\n`{llm_analysis.get('error', 'Unknown Error')}`\n\nPlease check your API Key.",
                    'detected_language': str(detected_lang),
                    'intent': 'SYSTEM_ERROR'
                })
        except Exception as e:
            print(f"❌ LLM failed: {e}")
            return jsonify({
                'error': 'LLM analysis failed. Check GROQ_API_KEY.',
                'details': str(e)
            }), 500
        
        # STEP 4: Query Database
        try:
            response = query_builder.query(llm_analysis)
            print(f"✅ Response ready ({len(response)} chars)")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            traceback.print_exc()
            response = "Sorry, error processing your query."
        
        print("="*60 + "\n")
        
        return jsonify({
            'response': response,
            'detected_language': str(detected_lang),
            'translated_to': english_text if detected_lang != 'en' else None,
            'intent': f"IN-DOMAIN → {llm_analysis['intent']}",
            'entities': llm_analysis.get('entities', {})
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear():
    return jsonify({'message': 'Cleared'})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ready' if all([lang_proc, llm_analyzer, query_builder]) else 'not_ready',
        'components': {
            'language_processor': lang_proc is not None,
            'llm_analyzer': llm_analyzer is not None,
            'query_builder': query_builder is not None,
            'external_handler': external_handler is not None,
            'ood_detector': ood_detector is not None
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Flask server starting...")
    print("🌐 URL: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)

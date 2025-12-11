from flask import Flask, render_template, request, jsonify
import traceback

app = Flask(__name__)

print("="*60)
print("🚀 Starting Car Chatbot...")
print("="*60)

lang_proc = None
intent_clf = None
query_handler = None
external_handler = None
ood_detector = None

try:
    print("Loading language processor...")
    from language_processor import LanguageProcessor
    lang_proc = LanguageProcessor()
    print("✅ Language processor loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

try:
    print("Loading intent classifier...")
    from intent_classifier import IntentClassifier
    intent_clf = IntentClassifier()
    print("✅ Intent classifier loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

try:
    print("Loading query handler...")
    from query_handler import QueryHandler
    query_handler = QueryHandler('data/cars.csv')
    print("✅ Query handler loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

try:
    print("Loading external handler...")
    from external_handler import ExternalHandler
    external_handler = ExternalHandler()
    print("✅ External handler loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

try:
    print("Loading OOD detector...")
    from ood_detector import OODDetector
    ood_detector = OODDetector(dataset_path='data/cars.csv')
    print("✅ OOD detector loaded")
except Exception as e:
    print(f"❌ OOD Error: {e}")
    traceback.print_exc()

print("="*60)
if all([lang_proc, intent_clf, query_handler, external_handler]):
    print("✅ ALL COMPONENTS LOADED!")
else:
    print("⚠️  SOME COMPONENTS FAILED")
print("="*60 + "\n")

chat_history = []
last_car_context = None  # Store context for "yes" responses

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_car_context
    
    try:
        user_message = request.json.get('message', '').strip()
        print(f"\n{'='*60}")
        print(f"📝 User: '{user_message}'")
        
        if not user_message:
            return jsonify({'error': 'No message'}), 400
        
        if not all([lang_proc, intent_clf, query_handler, external_handler]):
            return jsonify({'error': 'System not ready'}), 500
        
        # CRITICAL: Check for context continuation FIRST (before language processing)
        lower_msg = user_message.lower()
        
        if last_car_context:
            print(f"🔄 Context exists: {last_car_context['Name']}")
            
            # Check if user wants specs (yes, sure, ok, etc.)
            yes_words = ['yes', 'yeah', 'yep', 'sure', 'ok', 'oui', 'aywa', 'yah', 'specs', 'specification', 'details', 'info', 'more']
            if any(word in lower_msg for word in yes_words):
                print("✅ User wants specs - using context")
                
                car_data = last_car_context
                response = f"📋 **Detailed Specifications for {car_data['Name']}:**\n\n"
                response += f"💰 **Price:** ${car_data['Price']:,}\n"
                response += f"📅 **Year:** {car_data['Year']}\n"
                response += f"⚙️ **Engine:** {car_data['Horsepower']} HP\n"
                response += f"⛽ **Fuel:** {car_data['Fuel_Type']}\n"
                response += f"🔧 **Transmission:** {car_data['Transmission']}\n"
                response += f"📊 **Mileage:** {car_data['Mileage']} MPG\n"
                response += f"🎨 **Color:** {car_data['Color']}\n"
                response += f"🚗 **Type:** {car_data['Body_Type']}\n"
                response += f"🚪 **Doors:** {car_data['Doors']}\n"
                response += f"💺 **Seats:** {car_data['Seats']}\n\n"
                
                # Check if image exists
                if car_data.get('Image_URL'):
                    response += f"Would you like to see a picture of the {car_data['Name']}? (Say 'picture' or 'photo')"
                
                return jsonify({
                    'response': response,
                    'intent': 'specs_continuation',
                    'car_data': car_data
                })
            
            # Check if user wants picture
            picture_words = ['picture', 'pic', 'photo', 'image', 'show', 'see', 'taswira', 'soura']
            if any(word in lower_msg for word in picture_words):
                print("✅ User wants picture - using context")
                
                car_data = last_car_context
                
                if car_data.get('Image_URL'):
                    response = f"📸 **Here's the {car_data['Name']}:**"
                    
                    last_car_context = None  # Clear context after showing picture
                    
                    return jsonify({
                        'response': response,
                        'intent': 'picture',
                        'car_data': car_data,
                        'image_url': car_data['Image_URL']
                    })
                else:
                    response = f"Sorry, I don't have a picture of the {car_data['Name']} available."
                    return jsonify({
                        'response': response,
                        'intent': 'no_image'
                    })
            
            # If user asks something else, clear context and process normally
            if len(user_message.split()) > 2:  # If it's a real question (not just "no" or "nah")
                print("🔄 New question detected - clearing context")
                last_car_context = None
        
        # Normal processing for new questions
        print("🔄 Processing new question...")
        
        # Language Processing
        english_text, detected_lang = lang_proc.process(user_message)
        print(f"✅ Translated: '{english_text}' (lang: {detected_lang})")

        # OOD Detection (conservative)
        try:
            if ood_detector:
                in_domain, ood_score = ood_detector.is_in_domain(english_text)
                print(f"🔎 OOD score: {ood_score} → in_domain={in_domain}")
                if not in_domain:
                    # If explicit car names are present, prefer in-domain
                    car_names_tmp = intent_clf.extract_car_name(english_text)
                    if car_names_tmp:
                        print("⚠ OOD predicted but explicit car names present — keeping in-domain")
                    else:
                        print("⚠ OOD detected by model — routing to external handler")
                        response = external_handler.handle_general_question(english_text)
                        intent_info = "OUT-OF-DOMAIN (OOD_MODEL)"
                        last_car_context = None
                        return jsonify({
                            'response': response,
                            'detected_language': str(detected_lang),
                            'translated_to': english_text if detected_lang != 'en' else None,
                            'intent': intent_info
                        })
        except Exception as e:
            print(f"⚠ OOD check failed: {e}")

        # Intent Classification
        is_car_related = intent_clf.is_car_related(english_text)
        intent = intent_clf.classify(english_text)
        print(f"✅ Intent: {intent}, Car: {is_car_related}")
        
        # Generate Response
        if intent == 'general' or not is_car_related:
            response = external_handler.handle_general_question(english_text)
            intent_info = "OUT-OF-DOMAIN"
            last_car_context = None
        else:
            car_names = intent_clf.extract_car_name(english_text)
            
            if intent == 'price':
                response, car_data = query_handler.get_price(car_names)
                if car_data:
                    last_car_context = car_data
                    print(f"💾 Context saved: {car_data['Name']}")
            elif intent == 'availability':
                response, car_data = query_handler.get_availability(car_names)
                if car_data:
                    last_car_context = car_data
                    print(f"💾 Context saved: {car_data['Name']}")
            elif intent == 'model' or intent == 'general_car':
                response, car_data = query_handler.get_specs(car_names)
                if car_data:
                    last_car_context = car_data
                    print(f"💾 Context saved: {car_data['Name']}")
            elif intent == 'comparison':
                response, car_data = query_handler.compare_cars(car_names)
                last_car_context = None
            else:
                response = "I can help with prices, availability, specs, and comparisons!"
                last_car_context = None
            
            intent_info = f"IN-DOMAIN → {intent}"
        
        print(f"✅ Response ready")
        print("="*60 + "\n")
        
        return jsonify({
            'response': response,
            'detected_language': str(detected_lang),
            'translated_to': english_text if detected_lang != 'en' else None,
            'intent': intent_info
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear():
    global last_car_context
    chat_history.clear()
    last_car_context = None
    return jsonify({'message': 'Cleared'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Flask starting...")
    print("🌐 URL: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)


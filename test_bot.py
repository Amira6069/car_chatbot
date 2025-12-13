print("="*60)
print("Testing each component individually...")
print("="*60)

# Test 1: Language Processor
print("\n1️⃣ Testing language_processor.py...")
try:
    from language_processor import LanguageProcessor
    lp = LanguageProcessor()
    test_result = lp.process("Hello")
    print("   ✅ Language Processor works!")
except Exception as e:
    print(f"   ❌ Language Processor FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Intent Classifier
print("\n2️⃣ Testing intent_classifier.py...")
try:
    from intent_classifier import IntentClassifier
    ic = IntentClassifier()
    test_result = ic.classify("toyota price")
    print("   ✅ Intent Classifier works!")
except Exception as e:
    print(f"   ❌ Intent Classifier FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Query Handler
print("\n3️⃣ Testing query_handler.py...")
try:
    from query_handler import QueryHandler
    qh = QueryHandler('data/cars2.csv')
    print("   ✅ Query Handler works!")
except Exception as e:
    print(f"   ❌ Query Handler FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: External Handler
print("\n4️⃣ Testing external_handler.py...")
try:
    from external_handler import ExternalHandler
    eh = ExternalHandler()
    test_result = eh.handle_general_question("weather")
    print("   ✅ External Handler works!")
except Exception as e:
    print(f"   ❌ External Handler FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Testing complete!")
print("="*60)
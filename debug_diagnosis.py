
import os
import sys
import traceback
from dotenv import load_dotenv

# Load env vars
load_dotenv()

print("="*60)
print("🔍 DIAGNOSTIC TOOL")
print("="*60)

# Check API Key presence
key = os.getenv('GROQ_API_KEY')
if not key:
    print("❌ GROQ_API_KEY is MISSING in .env")
elif key == 'your_groq_api_key_here':
    print("❌ GROQ_API_KEY is set to PLACEHOLDER")
else:
    print(f"✅ GROQ_API_KEY found (length: {len(key)})")

# Test LLM Analyzer
print("\n🧠 Testing LLM Analyzer...")
try:
    from llm_analyzer import LLMAnalyzer
    analyzer = LLMAnalyzer()
    
    query = "i want all toyota cars"
    print(f"   Query: '{query}'")
    
    # We want to see the RAW exception if it fails, so we might need to bypass the try/catch in analyze_query
    # But analyze_query prints the error. Let's capture stdout or just rely on what we can see.
    result = analyzer.analyze_query(query)
    
    print(f"   Result: {result}")
    
    if result.get('entities') == {}:
        print("   ⚠️  Entities are EMPTY -> This causes the 'all cars' fallback behavior.")
        
except Exception as e:
    print(f"   ❌ LLM CRASHED: {e}")
    traceback.print_exc()

# Test OOD Detector
print("\n🛡️  Testing OOD Detector...")
try:
    from ood_detector import OODDetector
    ood = OODDetector(dataset_path='data/cars2.csv')
    
    queries = ["hello my friend how are u ?", "is bmw available ?", "weather in paris"]
    
    for q in queries:
        is_in, score = ood.is_in_domain(q)
        print(f"   Query: '{q}' -> In-Domain: {is_in} (Score: {score:.4f}, Threshold: {ood.threshold:.4f})")
        
except Exception as e:
    print(f"   ❌ OOD CRASHED: {e}")
    traceback.print_exc()

print("\n" + "="*60)

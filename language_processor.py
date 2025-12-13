from langdetect import detect, DetectorFactory, LangDetectException
from deep_translator import GoogleTranslator
import re

DetectorFactory.seed = 0

class LanguageProcessor:
    def __init__(self):
        print("✅ Language Processor initialized (with Tunisian dialect support)")
        
        # Tunisian dialect and Arabic word mappings
        self.word_map = {
            # Tunisian dialect (Darija)
            'mawjouda': 'available', 'mawjoud': 'available', 
            'kayen': 'available', 'kayna': 'available',
            'fama': 'there is', 'chkoun': 'who', 
            'chnouwa': 'what', 'chnowa': 'what',
            'kifech': 'how', 'chhal': 'how much', 
            'b9addech': 'how much', 'b9adech': 'how much',
            'barcha': 'many', 'yeser': 'very', 
            'karhba': 'car', 'siyara': 'car', 'karhabti': 'my car',
            'thamen': 'price', 's3ar': 'price', 'taman': 'price',
            'behi': 'good', 'mezyen': 'good', 'mliha': 'good',
            'nheb': 'I want', 'nhoub': 'I want', 'bech': 'want to',
            'wala': 'or', 'ama': 'but',
            
            # French (common in Tunisia)
            'disponible': 'available', 'prix': 'price', 
            'combien': 'how much', 'voiture': 'car',
            'cherche': 'search', 'veux': 'want',
            
            # Arabic
            'موجودة': 'available', 'موجود': 'available',
            'سيارة': 'car', 'ثمن': 'price', 'كم': 'how much',
            'اريد': 'I want', 'ابحث': 'search',
        }
    
    def preprocess(self, text):
        """
        Preprocess text by replacing Tunisian/Arabic words with English
        """
        result = text.lower()
        
        # Replace words from dictionary
        for foreign, english in self.word_map.items():
            # Use word boundaries to avoid partial matches
            result = re.sub(
                r'\b' + re.escape(foreign) + r'\b', 
                english, 
                result, 
                flags=re.IGNORECASE
            )
        
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def process(self, text):
        """
        Main processing pipeline:
        1. Detect language
        2. Preprocess (replace Tunisian words)
        3. Translate if needed
        
        Returns: (english_text, detected_language)
        """
        print(f"  🔍 Original: '{text}'")
        
        # Step 1: Try to detect language
        try:
            detected_lang = detect(text)
        except LangDetectException:
            detected_lang = 'unknown'
        except Exception:
            detected_lang = 'unknown'
        
        print(f"  🌍 Detected: {detected_lang}")
        
        # Step 2: Preprocess (replace Tunisian/Arabic words)
        processed = self.preprocess(text)
        
        if processed != text.lower():
            print(f"  ✏️  Preprocessed: '{processed}'")
        
        # Step 3: If not English, translate
        if detected_lang not in ['en', 'unknown']:
            try:
                # Use deep-translator (stable)
                translator = GoogleTranslator(source=detected_lang, target='en')
                translated = translator.translate(processed)
                print(f"  🌐 Translated: '{translated}'")
                return translated, detected_lang
            except Exception as e:
                print(f"  ⚠️  Translation failed: {e}, using preprocessed text")
                return processed, detected_lang
        
        # If English or unknown, return preprocessed version
        return processed, detected_lang if detected_lang != 'unknown' else 'en'


# Test the module
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING LANGUAGE PROCESSOR WITH TUNISIAN DIALECT")
    print("="*60 + "\n")
    
    lp = LanguageProcessor()
    
    test_cases = [
        # English
        "Find me a Toyota under 30000",
        
        # French
        "Je veux un Toyota",
        "Combien coûte cette voiture?",
        
        # Tunisian dialect
        "chhal thamen el karhba?",
        "fama toyota mawjouda?",
        "nheb toyota b9addech?",
        "barcha siyarat mezyen",
        
        # Mixed Tunisian-French
        "disponible wala kayen toyota?",
        
        # Arabic
        "اريد سيارة تويوتا",
        "كم ثمن السيارة؟",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test}")
        print('='*60)
        result, lang = lp.process(test)
        print(f"\n✅ Final Result:")
        print(f"   Text: '{result}'")
        print(f"   Language: {lang}")
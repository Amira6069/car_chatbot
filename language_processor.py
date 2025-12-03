from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import re

DetectorFactory.seed = 0

class LanguageProcessor:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='en')
        
        self.word_map = {
            'mawjouda': 'available', 'mawjoud': 'available', 
            'kayen': 'available', 'kayna': 'available',
            'fama': 'there is', 'chkoun': 'who', 
            'chnouwa': 'what', 'chnowa': 'what',
            'kifech': 'how', 'chhal': 'how much', 
            'b9addech': 'how much',
            'barcha': 'many', 'yeser': 'very', 
            'karhba': 'car', 'siyara': 'car',
            'thamen': 'price', 's3ar': 'price',
            'disponible': 'available', 'prix': 'price', 
            'combien': 'how much',
            'موجودة': 'available', 'موجود': 'available',
            'سيارة': 'car', 'ثمن': 'price',
        }
    
    def preprocess(self, text):
        result = text.lower()
        for foreign, english in self.word_map.items():
            result = re.sub(r'\b' + re.escape(foreign) + r'\b', english, result, flags=re.IGNORECASE)
        result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    def process(self, text):
        print(f"\n🔍 Original: '{text}'")
        
        try:
            lang = detect(text)
        except:
            lang = 'unknown'
        
        processed = self.preprocess(text)
        
        if lang not in ['en', 'unknown']:
            try:
                translated = self.translator.translate(processed)
                return translated, lang
            except:
                pass
        
        return processed, lang
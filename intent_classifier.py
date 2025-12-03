import re

class IntentClassifier:
    def __init__(self):
        self.intents = {
            'price': ['price', 'cost', 'how much', 'chhal', 'thamen', 'prix', 'combien'],
            'availability': ['available', 'stock', 'buy', 'have', 'got', 'there', 'mawjouda', 'kayen', 'fama', 'disponible'],
            'model': ['specs', 'specification', 'features', 'about', 'tell', 'info', 'details'],
            'comparison': ['compare', 'difference', 'vs', 'better', 'best', 'which'],
        }
        
        self.car_brands = ['toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'volkswagen', 'nissan', 'hyundai', 'kia', 'mazda', 'chevrolet', 'tesla', 'lexus', 'porsche']
        self.car_models = ['corolla', 'camry', 'civic', 'accord', 'focus', 'mustang', 'x5', 'x3', 'x7', 'c-class', 'e-class', 'a4', 'q5', 'golf', 'rav4', 'cr-v']
    
    def is_car_related(self, text):
        text_lower = text.lower()
        
        for brand in self.car_brands:
            if brand in text_lower:
                print(f"  ✅ Found '{brand}' → CAR")
                return True
        
        for model in self.car_models:
            if model in text_lower:
                print(f"  ✅ Found '{model}' → CAR")
                return True
        
        print(f"  ❌ GENERAL")
        return False
    
    def classify(self, text):
        if not self.is_car_related(text):
            return 'general'
        
        text_lower = text.lower()
        
        for intent, keywords in self.intents.items():
            for kw in keywords:
                if kw in text_lower:
                    print(f"  🎯 {intent.upper()}")
                    return intent
        
        return 'general_car'
    
    def extract_car_name(self, text):
        text_lower = text.lower()
        found = []
        
        for brand in self.car_brands:
            if brand in text_lower:
                found.append(brand)
        
        for model in self.car_models:
            if model in text_lower:
                found.append(model)
        
        return list(dict.fromkeys(found)) if found else None
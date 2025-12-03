class ExternalHandler:
    def __init__(self):
        self.categories = {
            'shopping': {
                'keywords': ['buy', 'shop', 'clothes', 'shoes', 'fashion'],
                'links': [
                    ('Amazon', 'https://www.amazon.com'),
                    ('Shein', 'https://www.shein.com'),
                ]
            },
            'weather': {
                'keywords': ['weather', 'temperature', 'rain'],
                'links': [
                    ('Weather.com', 'https://weather.com'),
                ]
            },
        }
    
    def detect_category(self, question):
        q_lower = question.lower()
        for category, data in self.categories.items():
            for keyword in data['keywords']:
                if keyword in q_lower:
                    return category
        return 'general'
    
    def handle_general_question(self, question):
        category = self.detect_category(question)
        
        response = "🤖 **I specialize in car information!**\n\n"
        
        if category != 'general':
            response += f"**For {category}, try:**\n\n"
            for name, url in self.categories[category]['links']:
                response += f"• [{name}]({url})\n"
        else:
            response += "**For general questions:**\n\n"
            response += "• [ChatGPT](https://chat.openai.com)\n"
            response += "• [Google](https://www.google.com)\n"
        
        response += "\n**I can help with:**\n✓ Prices ✓ Availability ✓ Specs"
        
        return response
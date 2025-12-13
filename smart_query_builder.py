import pandas as pd
import numpy as np

class SmartQueryBuilder:
    """
    Converts LLM analysis into intelligent database queries.
    Compatible with cars2.csv structure (Make, Model, MSRP, etc.)
    """
    
    def __init__(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path)
            # Normalize column names
            self.df.columns = self.df.columns.str.strip()
            
            # Create lowercase versions for matching
            self.df['make_lower'] = self.df['Make'].str.lower().str.strip()
            self.df['model_lower'] = self.df['Model'].str.lower().str.strip()
            self.df['style_lower'] = self.df['Vehicle Style'].str.lower().str.strip()
            
            print(f"✅ Smart Query Builder loaded {len(self.df)} cars")
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            raise
    
    def query(self, llm_analysis):
        """
        Main query method - routes to appropriate handler.
        """
        intent = llm_analysis.get('intent', 'search')
        entities = llm_analysis.get('entities', {})
        
        print(f"\n🔍 Query: intent={intent}, entities={entities}")
        
        if intent == 'compare':
            return self._handle_comparison(entities)
        elif intent == 'specs':
            return self._handle_specs(entities)
        elif intent == 'list_all':
            return self._handle_list_all(entities)
        else:
            return self._handle_search(entities)
    
    def _filter_dataframe(self, entities):
        """Apply filters based on entities"""
        df_filtered = self.df.copy()
        
        # Filter by make
        if entities.get('make'):
            make = entities['make'].lower()
            # Handle variations: mercedes, mercedes-benz
            if 'mercedes' in make:
                df_filtered = df_filtered[df_filtered['make_lower'].str.contains('mercedes', na=False)]
            else:
                df_filtered = df_filtered[df_filtered['make_lower'].str.contains(make, na=False)]
            print(f"   ✓ Make filter: {make} → {len(df_filtered)} results")
        
        # Filter by model
        if entities.get('model'):
            model = entities['model'].lower()
            df_filtered = df_filtered[df_filtered['model_lower'].str.contains(model, na=False)]
            print(f"   ✓ Model filter: {model} → {len(df_filtered)} results")
        
        # Filter by price (MSRP column)
        if entities.get('min_price'):
            df_filtered = df_filtered[df_filtered['MSRP'] >= entities['min_price']]
            print(f"   ✓ Min price: ${entities['min_price']:,} → {len(df_filtered)} results")
        
        if entities.get('max_price'):
            df_filtered = df_filtered[df_filtered['MSRP'] <= entities['max_price']]
            print(f"   ✓ Max price: ${entities['max_price']:,} → {len(df_filtered)} results")
        
        # Filter by vehicle style
        if entities.get('vehicle_style'):
            style = entities['vehicle_style'].lower()
            df_filtered = df_filtered[df_filtered['style_lower'].str.contains(style, na=False)]
            print(f"   ✓ Style filter: {style} → {len(df_filtered)} results")
        
        # Filter by year
        if entities.get('min_year'):
            df_filtered = df_filtered[df_filtered['Year'] >= entities['min_year']]
        
        if entities.get('max_year'):
            df_filtered = df_filtered[df_filtered['Year'] <= entities['max_year']]
        
        return df_filtered
    
    def _handle_search(self, entities):
        """Handle search queries"""
        df_filtered = self._filter_dataframe(entities)
        
        if len(df_filtered) == 0:
            return "😔 Sorry, no cars match your criteria. Try adjusting your filters!"
        
        # Sort logic
        sort_order = entities.get('sort_order', 'default')
        if sort_order == 'price_asc':
            df_filtered = df_filtered.sort_values('MSRP', ascending=True)
            print("   ✓ Sorting by Lowest Price")
        elif sort_order == 'price_desc':
            df_filtered = df_filtered.sort_values('MSRP', ascending=False)
            print("   ✓ Sorting by Highest Price")
        elif sort_order == 'newest':
            df_filtered = df_filtered.sort_values('Year', ascending=False)
        elif entities.get('fuel_efficiency'):
            df_filtered = df_filtered.sort_values('highway MPG', ascending=False)
        else:
            # Default sort: Recent + Price (balanced)
            df_filtered = df_filtered.sort_values(['Year', 'MSRP'], ascending=[False, True])
        
        # Top results
        # If "cheap" was requested (price_asc), show top 3 specifically
        limit = 3 if sort_order == 'price_asc' else 5
        top_results = df_filtered.head(limit)
        
        response = f"🚗 **Found {len(df_filtered)} cars!** Here are the best options:\n\n"
        
        for idx, row in top_results.iterrows():
            response += f"### {int(row['Year'])} {row['Make'].title()} {row['Model'].title()}\n"
            response += f"💰 **Price:** ${int(row['MSRP']):,}\n"
            response += f"📏 **Size:** {row['Vehicle Size']} | **Style:** {row['Vehicle Style']}\n"
            response += f"⚙️ **Engine:** {int(row['Engine HP'])} HP ({row['Engine Cylinders']} cyl)\n"
            response += f"🕹️ **Transmission:** {row['Transmission Type']}\n"
            response += f"⛽ **MPG:** {int(row['city mpg'])} city / {int(row['highway MPG'])} hwy\n\n"
            response += f"---\n"
        
        if len(df_filtered) > limit:
            response += f"\n_...and {len(df_filtered) - limit} more results._"
        
        return response
    
    def _handle_list_all(self, entities):
        """Handle list all queries"""
        df_filtered = self._filter_dataframe(entities)
        
        if len(df_filtered) == 0:
            return "😔 No cars found."
        
        df_filtered = df_filtered.sort_values(['Make', 'Model', 'Year'])
        
        response = f"📋 **Found {len(df_filtered)} cars!**\n\n"
        
        if len(df_filtered) <= 20:
            for idx, row in df_filtered.iterrows():
                response += f"• {int(row['Year'])} {row['Make'].title()} {row['Model'].title()} - ${int(row['MSRP']):,}\n"
        else:
            top_results = df_filtered.head(15)
            for idx, row in top_results.iterrows():
                response += f"• {int(row['Year'])} {row['Make'].title()} {row['Model'].title()} - ${int(row['MSRP']):,}\n"
            
            response += f"\n_...and {len(df_filtered) - 15} more._"
        
        return response
    
    def _handle_specs(self, entities):
        """Handle specs queries"""
        df_filtered = self._filter_dataframe(entities)
        
        if len(df_filtered) == 0:
            return "😔 Sorry, couldn't find that car."
        
        # Get most recent model
        car = df_filtered.sort_values('Year', ascending=False).iloc[0]
        
        response = f"📊 **{int(car['Year'])} {car['Make'].title()} {car['Model'].title()} Specifications:**\n\n"
        
        if entities.get('fuel_efficiency'):
            response += f"⛽ **Fuel Economy:**\n"
            response += f"   • City: {int(car['city mpg'])} MPG\n"
            response += f"   • Highway: {int(car['highway MPG'])} MPG\n\n"
        
        response += f"💰 **Price:** ${int(car['MSRP']):,}\n"
        response += f"⚙️ **Engine:** {int(car['Engine HP'])} HP, {int(car['Engine Cylinders'])} cylinders\n"
        response += f"🔧 **Transmission:** {car['Transmission Type']}\n"
        response += f"📏 **Size:** {car['Vehicle Size']}\n"
        response += f"🚗 **Style:** {car['Vehicle Style']}\n"
        
        if len(df_filtered) > 1:
            response += f"\n_Found {len(df_filtered)} variants. Showing latest model._"
        
        return response
    
    def _handle_comparison(self, entities):
        """Handle comparison queries"""
        models_to_compare = entities.get('models_to_compare', [])
        
        if len(models_to_compare) < 2:
            return "🤔 Please specify at least 2 cars to compare!"
        
        cars = []
        for model_name in models_to_compare:
            model_lower = model_name.lower()
            matches = self.df[self.df['model_lower'].str.contains(model_lower, na=False)]
            
            if len(matches) > 0:
                car = matches.sort_values('Year', ascending=False).iloc[0]
                cars.append(car)
            else:
                return f"😔 Sorry, couldn't find '{model_name}' in database."
        
        if len(cars) < 2:
            return "😔 Couldn't find enough cars to compare."
        
        response = f"⚖️ **Comparison: {' vs '.join([f'{c['Make'].title()} {c['Model'].title()}' for c in cars])}**\n\n"
        
        for car in cars:
            response += f"**{int(car['Year'])} {car['Make'].title()} {car['Model'].title()}:**\n"
            response += f"   💰 Price: ${int(car['MSRP']):,}\n"
            response += f"   ⛽ MPG: {int(car['city mpg'])} city / {int(car['highway MPG'])} highway\n"
            response += f"   ⚙️ Engine: {int(car['Engine HP'])} HP\n"
            response += f"   🚗 Type: {car['Vehicle Style']}\n\n"
        
        # Winner analysis
        cheapest = min(cars, key=lambda x: x['MSRP'])
        most_powerful = max(cars, key=lambda x: x['Engine HP'])
        most_efficient = max(cars, key=lambda x: x['highway MPG'])
        
        response += "🏆 **Winners:**\n"
        response += f"   • Best Price: {cheapest['Make'].title()} {cheapest['Model'].title()} (${int(cheapest['MSRP']):,})\n"
        response += f"   • Most Powerful: {most_powerful['Make'].title()} {most_powerful['Model'].title()} ({int(most_powerful['Engine HP'])} HP)\n"
        response += f"   • Most Fuel Efficient: {most_efficient['Make'].title()} {most_efficient['Model'].title()} ({int(most_efficient['highway MPG'])} MPG)\n"
        
        return response
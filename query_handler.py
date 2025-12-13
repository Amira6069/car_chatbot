import pandas as pd
import os

class QueryHandler:
    def __init__(self, dataset_path='data/cars2.csv'):
        if os.path.exists(dataset_path):
            self.df = pd.read_csv(dataset_path)
            print(f"✓ Dataset: {len(self.df)} cars")
            
            # Check if Image_URL column exists
            if 'Image_URL' in self.df.columns:
                print(f"✓ Images available: {self.df['Image_URL'].notna().sum()} cars have images")
            else:
                print(f"⚠ No Image_URL column found")
        else:
            print("⚠ Dataset not found!")
            self.df = None
    
    def search_car(self, car_names):
        if self.df is None or not car_names:
            return None
        
        results = pd.DataFrame()
        for car_name in car_names:
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    try:
                        mask = self.df[col].str.contains(car_name, case=False, na=False)
                        results = pd.concat([results, self.df[mask]])
                    except:
                        continue
        
        return results.drop_duplicates() if not results.empty else None
    
    def get_price(self, car_names):
        if not car_names:
            return "Please specify which car.", None
        
        results = self.search_car(car_names)
        if results is None or results.empty:
            return f"Sorry, couldn't find {' '.join(car_names)}.", None
        
        car = results.iloc[0]
        car_dict = car.to_dict()
        
        response = f"💰 **{car_dict['Name']}**\n\n"
        response += f"**Price:** ${car_dict['Price']:,}\n"
        response += f"**Year:** {car_dict['Year']}\n\n"
        response += "Would you like to see detailed specifications? (Say 'yes')"
        
        return response, car_dict
    
    def get_availability(self, car_names):
        if not car_names:
            return "Please specify which car.", None
        
        results = self.search_car(car_names)
        if results is None or results.empty:
            return f"Sorry, {' '.join(car_names)} not in inventory.", None
        
        car = results.iloc[0]
        car_dict = car.to_dict()
        
        response = f"✅ **Yes! The {car_dict['Name']} is available!**\n\n"
        response += f"💰 **Price:** ${car_dict['Price']:,}\n"
        response += f"📅 **Year:** {car_dict['Year']}\n\n"
        response += "Would you like to see detailed specifications? (Say 'yes')"
        
        return response, car_dict
    
    def get_specs(self, car_names):
        if not car_names:
            return "Please specify which car.", None
        
        results = self.search_car(car_names)
        if results is None or results.empty:
            return f"Sorry, couldn't find {' '.join(car_names)}.", None
        
        car = results.iloc[0]
        car_dict = car.to_dict()
        
        response = f"📋 **{car_dict['Name']} Specifications:**\n\n"
        
        # Show key specs first
        important_specs = ['Price', 'Year', 'Horsepower', 'Fuel_Type', 'Transmission', 'Mileage', 'Color', 'Body_Type', 'Doors', 'Seats']
        
        for spec in important_specs:
            if spec in car_dict and pd.notna(car_dict[spec]):
                response += f"• **{spec}:** {car_dict[spec]}\n"
        
        # Add any remaining specs
        for col in car.index:
            if col not in important_specs and col not in ['Name', 'Brand', 'Model', 'Image_URL'] and pd.notna(car[col]):
                response += f"• **{col}:** {car[col]}\n"
        
        # Check if image is available
        if 'Image_URL' in car_dict and pd.notna(car_dict['Image_URL']) and car_dict['Image_URL']:
            response += "\n\nWould you like to see a picture? (Say 'picture' or 'photo')"
        
        return response, car_dict
    
    def compare_cars(self, car_names):
        if not car_names or len(car_names) < 2:
            return "Please mention 2 cars to compare.", None
        
        results = self.search_car(car_names)
        if results is None or len(results) < 2:
            return "Couldn't find enough cars.", None
        
        response = "⚖️ **Comparison:**\n\n"
        
        for idx, row in results.head(2).iterrows():
            response += f"**{row['Name']}**\n"
            response += f"  💰 Price: ${row['Price']:,}\n"
            response += f"  📅 Year: {row['Year']}\n"
            if 'Horsepower' in row and pd.notna(row['Horsepower']):
                response += f"  ⚡ Power: {row['Horsepower']} HP\n"
            if 'Mileage' in row and pd.notna(row['Mileage']):
                response += f"  ⛽ Mileage: {row['Mileage']} MPG\n"
            response += "\n"
        
        return response, None
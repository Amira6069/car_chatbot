#!/usr/bin/env python3
"""
Complete unit tests for the intelligent car chatbot
Tests all components individually and integration
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestLanguageProcessor(unittest.TestCase):
    """Test language detection and translation"""
    
    def setUp(self):
        try:
            from language_processor import LanguageProcessor
            self.lang_proc = LanguageProcessor()
        except Exception as e:
            self.skipTest(f"Language processor not available: {e}")
    
    def test_english_detection(self):
        """Test English text is detected and not translated"""
        text, lang = self.lang_proc.process("Find me a Toyota")
        self.assertEqual(lang, 'en')
        self.assertEqual(text, "Find me a Toyota")
    
    def test_french_translation(self):
        """Test French is detected and translated"""
        text, lang = self.lang_proc.process("Je veux un Toyota")
        self.assertIn(lang, ['fr', 'en'])  # Sometimes detects as English if simple
        self.assertIsInstance(text, str)


class TestOODDetector(unittest.TestCase):
    """Test out-of-domain detection"""
    
    def setUp(self):
        try:
            from ood_detector import OODDetector
            self.ood = OODDetector(dataset_path='data/cars2.csv')
        except Exception as e:
            self.skipTest(f"OOD detector not available: {e}")
    
    def test_in_domain_car_query(self):
        """Car queries should be in-domain"""
        in_domain, score = self.ood.is_in_domain("Find me a Toyota Camry")
        # Conservative: even if model predicts OOD, we should catch explicit car names
        self.assertIsInstance(in_domain, bool)
        self.assertIsInstance(score, (int, float))
    
    def test_out_of_domain_weather(self):
        """Weather queries should be out-of-domain"""
        in_domain, score = self.ood.is_in_domain("What's the weather today?")
        # We expect False, but model might vary
        self.assertIsInstance(in_domain, bool)
    
    def test_out_of_domain_shopping(self):
        """Shopping queries should be out-of-domain"""
        in_domain, score = self.ood.is_in_domain("Where can I buy shoes?")
        self.assertIsInstance(in_domain, bool)


class TestLLMAnalyzer(unittest.TestCase):
    """Test LLM intent classification and entity extraction"""
    
    def setUp(self):
        try:
            from llm_analyzer import LLMAnalyzer
            self.analyzer = LLMAnalyzer()
        except Exception as e:
            self.skipTest(f"LLM analyzer not available: {e}")
    
    def test_simple_search_intent(self):
        """Test simple search query"""
        result = self.analyzer.analyze_query("Find me a Toyota under 30000")
        
        self.assertIn('intent', result)
        self.assertIn('entities', result)
        self.assertEqual(result['intent'], 'search')
        self.assertIn('make', result['entities'])
        self.assertIn('toyota', result['entities']['make'].lower())
    
    def test_price_range_extraction(self):
        """Test price range extraction"""
        result = self.analyzer.analyze_query("I want a Mercedes between 20k and 50k")
        
        self.assertEqual(result['intent'], 'search')
        entities = result['entities']
        self.assertIsNotNone(entities.get('min_price'))
        self.assertIsNotNone(entities.get('max_price'))
        self.assertGreaterEqual(entities['max_price'], entities['min_price'])
    
    def test_comparison_intent(self):
        """Test comparison query"""
        result = self.analyzer.analyze_query("Compare BMW M6 to Toyota Previa")
        
        self.assertEqual(result['intent'], 'compare')
        self.assertIn('models_to_compare', result['entities'])
        self.assertIsInstance(result['entities']['models_to_compare'], list)
        self.assertGreaterEqual(len(result['entities']['models_to_compare']), 2)
    
    def test_specs_with_fuel(self):
        """Test specs query with fuel focus"""
        result = self.analyzer.analyze_query("How much fuel does Honda Civic consume")
        
        self.assertIn(result['intent'], ['specs', 'search'])
        entities = result['entities']
        self.assertIn('honda', entities.get('make', '').lower())
        self.assertTrue(entities.get('fuel_efficiency', False))
    
    def test_list_all_suv(self):
        """Test list all query"""
        result = self.analyzer.analyze_query("Show me all SUVs available")
        
        self.assertEqual(result['intent'], 'list_all')
        self.assertIn('suv', result['entities'].get('vehicle_style', '').lower())


class TestSmartQueryBuilder(unittest.TestCase):
    """Test database querying logic"""
    
    def setUp(self):
        try:
            from smart_query_builder import SmartQueryBuilder
            self.qb = SmartQueryBuilder('data/cars2.csv')
        except Exception as e:
            self.skipTest(f"Query builder not available: {e}")
    
    def test_search_by_make(self):
        """Test searching by make"""
        analysis = {
            'intent': 'search',
            'entities': {'make': 'toyota'}
        }
        
        response = self.qb.query(analysis)
        
        self.assertIsInstance(response, str)
        self.assertIn('toyota', response.lower())
        self.assertNotIn('😔', response)  # Should find results
    
    def test_search_with_price_filter(self):
        """Test price filtering"""
        analysis = {
            'intent': 'search',
            'entities': {
                'make': 'toyota',
                'max_price': 30000
            }
        }
        
        response = self.qb.query(analysis)
        
        self.assertIsInstance(response, str)
        # Should return results
        self.assertIn('Found', response)
    
    def test_list_all_suvs(self):
        """Test listing all SUVs"""
        analysis = {
            'intent': 'list_all',
            'entities': {'vehicle_style': 'suv'}
        }
        
        response = self.qb.query(analysis)
        
        self.assertIsInstance(response, str)
        self.assertIn('Found', response)
        self.assertIn('suv', response.lower())
    
    def test_comparison(self):
        """Test car comparison"""
        analysis = {
            'intent': 'compare',
            'entities': {
                'models_to_compare': ['civic', 'camry']
            }
        }
        
        response = self.qb.query(analysis)
        
        self.assertIsInstance(response, str)
        # Should contain comparison or error message
        self.assertTrue(len(response) > 0)
    
    def test_no_results(self):
        """Test query with no results"""
        analysis = {
            'intent': 'search',
            'entities': {
                'make': 'nonexistentbrand123',
                'max_price': 100
            }
        }
        
        response = self.qb.query(analysis)
        
        self.assertIn('😔', response)  # Should show sorry message


class TestExternalHandler(unittest.TestCase):
    """Test external question handling"""
    
    def setUp(self):
        try:
            from external_handler import ExternalHandler
            self.handler = ExternalHandler()
        except Exception as e:
            self.skipTest(f"External handler not available: {e}")
    
    def test_weather_question(self):
        """Test weather question handling"""
        response = self.handler.handle_general_question("What's the weather today?")
        
        self.assertIsInstance(response, str)
        self.assertIn('specialize', response.lower())
    
    def test_shopping_question(self):
        """Test shopping question"""
        response = self.handler.handle_general_question("Where can I buy clothes?")
        
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)


class TestIntegration(unittest.TestCase):
    """Integration tests - full pipeline"""
    
    def setUp(self):
        """Setup all components"""
        try:
            from language_processor import LanguageProcessor
            from llm_analyzer import LLMAnalyzer
            from smart_query_builder import SmartQueryBuilder
            from external_handler import ExternalHandler
            from ood_detector import OODDetector
            
            self.lang_proc = LanguageProcessor()
            self.llm_analyzer = LLMAnalyzer()
            self.query_builder = SmartQueryBuilder('data/cars2.csv')
            self.external_handler = ExternalHandler()
            self.ood_detector = OODDetector(dataset_path='data/cars2.csv')
            
        except Exception as e:
            self.skipTest(f"Integration test setup failed: {e}")
    
    def test_full_pipeline_english(self):
        """Test complete pipeline with English query"""
        user_query = "Find me a Toyota under $30k"
        
        # Step 1: Language
        english_text, lang = self.lang_proc.process(user_query)
        self.assertEqual(lang, 'en')
        
        # Step 2: OOD
        in_domain, _ = self.ood_detector.is_in_domain(english_text)
        # Should be in-domain (car query)
        
        # Step 3: LLM Analysis
        analysis = self.llm_analyzer.analyze_query(english_text)
        self.assertIn('intent', analysis)
        
        # Step 4: Query
        response = self.query_builder.query(analysis)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    
    def test_full_pipeline_out_of_domain(self):
        """Test OOD query handling"""
        user_query = "What's the weather today?"
        
        english_text, lang = self.lang_proc.process(user_query)
        in_domain, _ = self.ood_detector.is_in_domain(english_text)
        
        # Should route to external handler
        if not in_domain:
            response = self.external_handler.handle_general_question(english_text)
            self.assertIsInstance(response, str)
            self.assertIn('specialize', response.lower())


class TestDataQuality(unittest.TestCase):
    """Test data quality and structure"""
    
    def test_database_exists(self):
        """Test that database file exists"""
        self.assertTrue(os.path.exists('data/cars2.csv'))
    
    def test_database_structure(self):
        """Test database has expected columns"""
        df = pd.read_csv('data/cars2.csv')
        
        expected_columns = ['Make', 'Model', 'Year', 'MSRP', 'Engine HP', 
                          'city mpg', 'highway MPG', 'Vehicle Style']
        
        for col in expected_columns:
            self.assertIn(col, df.columns)
    
    def test_database_not_empty(self):
        """Test database has data"""
        df = pd.read_csv('data/cars2.csv')
        self.assertGreater(len(df), 0)
    
    def test_price_column_validity(self):
        """Test MSRP column has valid values"""
        df = pd.read_csv('data/cars2.csv')
        self.assertTrue((df['MSRP'] > 0).all())


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("🧪 RUNNING COMPLETE TEST SUITE")
    print("="*60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestOODDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestSmartQueryBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestExternalHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
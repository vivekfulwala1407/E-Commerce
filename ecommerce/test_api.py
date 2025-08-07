# #!/usr/bin/env python3
# """
# Improved E-commerce API Test Script
# This script comprehensively tests all API endpoints with better error handling
# """

# import requests
# import json
# import sys
# import time

# # Configuration
# BASE_URL = "http://127.0.0.1:8000/api"

# class EcommerceAPITester:
#     def __init__(self):
#         self.session = requests.Session()
#         self.products = []
#         self.cart_items = []
#         self.test_results = []
        
#     def print_step(self, step, description):
#         print(f"\n{'='*70}")
#         print(f"STEP {step}: {description}")
#         print('='*70)
    
#     def print_result(self, test_name, success, message, data=None, response_code=None):
#         status = "✅ PASSED" if success else "❌ FAILED"
#         print(f"{status}: {test_name}")
#         print(f"   Message: {message}")
#         if response_code:
#             print(f"   HTTP Status: {response_code}")
#         if data and isinstance(data, dict):
#             print(f"   Response: {json.dumps(data, indent=4)}")
#         print("-" * 50)
        
#         self.test_results.append({
#             'name': test_name,
#             'success': success,
#             'message': message,
#             'response_code': response_code
#         })
    
#     def test_server_connection(self):
#         """Test if server is running"""
#         self.print_step(0, "Testing Server Connection")
        
#         try:
#             response = self.session.get("http://127.0.0.1:8000/", timeout=5)
#             if response.status_code == 200:
#                 data = response.json()
#                 self.print_result("Server Connection", True, "Server is running", data, response.status_code)
#                 return True
#             else:
#                 self.print_result("Server Connection", False, f"Server returned HTTP {response.status_code}", None, response.status_code)
#                 return False
#         except requests.exceptions.ConnectionError:
#             self.print_result("Server Connection", False, "Cannot connect to server. Make sure Django server is running on http://127.0.0.1:8000/")
#             return False
#         except Exception as e:
#             self.print_result("Server Connection", False, f"Connection error: {str(e)}")
#             return False
    
#     def test_products_api(self):
#         """Test getting all products"""
#         self.print_step(1, "Testing Product Listing API")
        
#         try:
#             response = self.session.get(f"{BASE_URL}/products/", timeout=10)
#             data = response.json()
            
#             if response.status_code == 200:
#                 self.products = data.get('products', [])
#                 message = f"Successfully retrieved {len(self.products)} products"
#                 self.print_result("Product Listing", True, message, data, response.status_code)
#                 return True
#             else:
#                 self.print_result("Product Listing", False, "Failed to get products", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Product Listing", False, f"Exception: {str(e)}")
#             return False
    
#     def test_add_to_cart(self):
#         """Test adding products to cart"""
#         self.print_step(2, "Testing Add to Cart API")
        
#         if not self.products:
#             self.print_result("Add to Cart", False, "No products available to add to cart")
#             return False
        
#         # Test adding first product
#         product = self.products[0]
#         payload = {
#             "product_id": product["id"],
#             "quantity": 2
#         }
        
#         try:
#             response = self.session.post(
#                 f"{BASE_URL}/cart/add/",
#                 headers={"Content-Type": "application/json"},
#                 json=payload,  # Use json parameter instead of data
#                 timeout=10
#             )
#             data = response.json()
            
#             if response.status_code == 200:
#                 message = f"Successfully added {product['name']} to cart"
#                 self.print_result("Add to Cart", True, message, data, response.status_code)
#                 return True
#             else:
#                 self.print_result("Add to Cart", False, "Failed to add to cart", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Add to Cart", False, f"Exception: {str(e)}")
#             return False
    
#     def test_view_cart(self):
#         """Test viewing cart contents"""
#         self.print_step(3, "Testing View Cart API")
        
#         try:
#             response = self.session.get(f"{BASE_URL}/cart/", timeout=10)
#             data = response.json()
            
#             if response.status_code == 200:
#                 self.cart_items = data.get('cart', [])
#                 message = f"Successfully retrieved cart with {len(self.cart_items)} items"
#                 self.print_result("View Cart", True, message, data, response.status_code)
#                 return True
#             else:
#                 self.print_result("View Cart", False, "Failed to get cart", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("View Cart", False, f"Exception: {str(e)}")
#             return False
    
#     def test_update_cart(self):
#         """Test updating cart item quantity"""
#         self.print_step(4, "Testing Update Cart API")
        
#         if not self.cart_items:
#             self.print_result("Update Cart", False, "No cart items to update")
#             return False
        
#         cart_item = self.cart_items[0]
#         item_id = cart_item["id"]
#         new_quantity = 3
        
#         payload = {"quantity": new_quantity}
        
#         try:
#             response = self.session.post(
#                 f"{BASE_URL}/cart/update/{item_id}/",
#                 headers={"Content-Type": "application/json"},
#                 json=payload,
#                 timeout=10
#             )
#             data = response.json()
            
#             if response.status_code == 200:
#                 message = f"Successfully updated quantity to {new_quantity}"
#                 self.print_result("Update Cart", True, message, data, response.status_code)
#                 return True
#             else:
#                 self.print_result("Update Cart", False, "Failed to update cart", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Update Cart", False, f"Exception: {str(e)}")
#             return False
    
#     def test_checkout(self):
#         """Test checkout process"""
#         self.print_step(5, "Testing Checkout API")
        
#         try:
#             response = self.session.post(f"{BASE_URL}/checkout/", timeout=10)
#             data = response.json()
            
#             if response.status_code == 200:
#                 message = "Checkout completed successfully"
#                 self.print_result("Checkout", True, message, data, response.status_code)
#                 return True
#             else:
#                 self.print_result("Checkout", False, "Checkout failed", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Checkout", False, f"Exception: {str(e)}")
#             return False
    
#     def test_admin_add_product(self):
#         """Test admin add product API"""
#         self.print_step(6, "Testing Admin Add Product API")
        
#         payload = {
#             "name": "API Test Product",
#             "price": 79.99,
#             "stock": 15,
#             "description": "This product was added via API test script"
#         }
        
#         try:
#             response = self.session.post(
#                 f"{BASE_URL}/admin/product/add/",
#                 headers={"Content-Type": "application/json"},
#                 json=payload,
#                 timeout=10
#             )
            
#             if response.status_code == 200:
#                 try:
#                     data = response.json()
#                     message = "Product added successfully via admin API"
#                     self.print_result("Admin Add Product", True, message, data, response.status_code)
#                     return True
#                 except json.JSONDecodeError:
#                     # Handle case where response is not JSON
#                     message = f"Product added (non-JSON response): {response.text[:100]}"
#                     self.print_result("Admin Add Product", True, message, None, response.status_code)
#                     return True
#             else:
#                 try:
#                     data = response.json()
#                 except:
#                     data = {"raw_response": response.text}
#                 self.print_result("Admin Add Product", False, "Failed to add product", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Admin Add Product", False, f"Exception: {str(e)}")
#             return False
    
#     def test_admin_modify_product(self):
#         """Test admin modify product API"""
#         self.print_step(7, "Testing Admin Modify Product API")
        
#         if not self.products:
#             self.print_result("Admin Modify Product", False, "No products to modify")
#             return False
        
#         product = self.products[0]
#         product_id = product["id"]
        
#         payload = {
#             "name": f"Modified {product['name']}",
#             "price": 99.99,
#             "description": "This product was modified via API test"
#         }
        
#         try:
#             response = self.session.post(
#                 f"{BASE_URL}/admin/product/modify/{product_id}/",
#                 headers={"Content-Type": "application/json"},
#                 json=payload,
#                 timeout=10
#             )
            
#             if response.status_code == 200:
#                 try:
#                     data = response.json()
#                     message = "Product modified successfully"
#                     self.print_result("Admin Modify Product", True, message, data, response.status_code)
#                     return True
#                 except json.JSONDecodeError:
#                     message = f"Product modified (non-JSON response): {response.text[:100]}"
#                     self.print_result("Admin Modify Product", True, message, None, response.status_code)
#                     return True
#             else:
#                 try:
#                     data = response.json()
#                 except:
#                     data = {"raw_response": response.text}
#                 self.print_result("Admin Modify Product", False, "Failed to modify product", data, response.status_code)
#                 return False
#         except Exception as e:
#             self.print_result("Admin Modify Product", False, f"Exception: {str(e)}")
#             return False
    
#     def run_all_tests(self):
#         """Run all tests in sequence"""
#         print("🚀 Starting Comprehensive E-commerce API Tests")
#         print(f"🌐 Testing against: {BASE_URL}")
#         print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
#         # Check server connection first
#         if not self.test_server_connection():
#             print("\n❌ Cannot proceed with tests - server is not accessible")
#             return
        
#         # Run all tests
#         test_functions = [
#             ("Product Listing", self.test_products_api),
#             ("Add to Cart", self.test_add_to_cart),
#             ("View Cart", self.test_view_cart),
#             ("Update Cart", self.test_update_cart),
#             ("Checkout", self.test_checkout),
#             ("Admin Add Product", self.test_admin_add_product),
#             ("Admin Modify Product", self.test_admin_modify_product),
#         ]
        
#         for test_name, test_func in test_functions:
#             try:
#                 test_func()
#                 time.sleep(0.5)  # Small delay between tests
#             except Exception as e:
#                 self.print_result(test_name, False, f"Test crashed: {str(e)}")
        
#         # Final summary
#         self.print_final_summary()
    
#     def print_final_summary(self):
#         """Print comprehensive test summary"""
#         self.print_step("FINAL", "Comprehensive Test Results Summary")
        
#         passed = sum(1 for result in self.test_results if result['success'])
#         total = len(self.test_results)
        
#         print(f"📊 OVERALL RESULTS:")
#         print(f"   ✅ Passed: {passed}")
#         print(f"   ❌ Failed: {total - passed}")
#         print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
#         print()
        
#         print("📋 DETAILED RESULTS:")
#         for i, result in enumerate(self.test_results, 1):
#             status = "✅ PASSED" if result['success'] else "❌ FAILED"
#             print(f"   {i:2d}. {status}: {result['name']}")
#             if not result['success']:
#                 print(f"       ➤ {result['message']}")
        
#         print()
#         if passed == total:
#             print("🎉 CONGRATULATIONS! All tests passed!")
#             print("🚀 Your e-commerce API is fully functional!")
#         else:
#             print("⚠️  Some tests failed. Check the detailed results above.")
#             print("💡 Most common issues:")
#             print("   • Make sure Django server is running")
#             print("   • Check that you have products in your database")
#             print("   • Verify your URLs.py configuration")

# def main():
#     print("🛍️  E-commerce API Comprehensive Tester")
#     print("=" * 50)
#     print("This script will test all your API endpoints")
#     print("Make sure your Django server is running at: http://127.0.0.1:8000/")
#     print()
    
#     response = input("Press Enter to start testing, or 'q' to quit: ").strip().lower()
#     if response == 'q':
#         print("👋 Test cancelled by user")
#         return
    
#     tester = EcommerceAPITester()
#     tester.run_all_tests()

# if __name__ == "__main__":
#     main()
#!/usr/bin/env python3
"""
ტესტირების სკრიპტი კომენტარების ფუნქციონალისთვის
"""

import requests
import json

# აპლიკაციის URL
BASE_URL = "http://localhost:5000"

def test_add_comment():
    """კომენტარის დამატების ტესტი"""
    print("🧪 ვტესტავთ კომენტარის დამატებას...")
    
    # ჯერ უნდა გავიაროთ ავტორიზაცია (ეს მაგალითია)
    login_data = {
        'name': 'test_user',
        'password': 'test_password'
    }
    
    # სცადეთ კომენტარის დამატება
    comment_data = {
        'content': 'ეს არის ტესტის კომენტარი'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/add_comment/1", 
            json=comment_data, 
            headers=headers
        )
        
        print(f"სტატუსი: {response.status_code}")
        print(f"პასუხი: {response.text}")
        
        if response.status_code == 200:
            print("✅ კომენტარის დამატება მუშაობს!")
        else:
            print("❌ პრობლემაა კომენტარის დამატებასთან")
            
    except Exception as e:
        print(f"❌ შეცდომა: {e}")

def test_reactions():
    """რეაქციების ტესტი"""
    print("🧪 ვტესტავთ რეაქციებს...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/react/1/like", 
            headers=headers
        )
        
        print(f"სტატუსი: {response.status_code}")
        print(f"პასუხი: {response.text}")
        
        if response.status_code == 200:
            print("✅ რეაქციები მუშაობს!")
        else:
            print("❌ პრობლემაა რეაქციებთან")
            
    except Exception as e:
        print(f"❌ შეცდომა: {e}")

if __name__ == "__main__":
    print("🚀 იწყება ტესტირება...")
    test_add_comment()
    test_reactions()
    print("✅ ტესტირება დასრულდა!")

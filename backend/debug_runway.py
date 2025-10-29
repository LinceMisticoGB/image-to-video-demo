import requests
import os
from dotenv import load_dotenv

load_dotenv()

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
RUNWAY_API_URL = "https://api.dev.runwayml.com/v1"

def debug_runway_connection():
    print("🔍 Debugging RunwayML Connection...")
    print(f"API Key present: {'Yes' if RUNWAY_API_KEY else 'No'}")
    if RUNWAY_API_KEY:
        print(f"API Key starts with: {RUNWAY_API_KEY[:10]}...")
    
    # Headers CORRECTOS con X-Runway-Version
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": "2024-11-06"
    }
    
    try:
        print("\n1. Testing models endpoint...")
        response = requests.get(f"{RUNWAY_API_URL}/models", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Models endpoint accessible - API KEY VÁLIDA!")
            models = response.json()
            if 'data' in models:
                print("   Available models:")
                for model in models['data']:
                    model_id = model.get('id', 'Unknown')
                    model_name = model.get('name', 'No name')
                    print(f"     - {model_id}: {model_name}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Check generations endpoint
    try:
        print("\n2. Testing generations endpoint...")
        response = requests.get(f"{RUNWAY_API_URL}/generations", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Generations endpoint accessible")
            generations = response.json()
            print(f"   Total generations: {len(generations.get('data', []))}")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Test a simple generation with a real image
    try:
        print("\n3. Testing generation capability...")
        
        # Crear una imagen simple de prueba
        from PIL import Image, ImageDraw
        import base64
        from io import BytesIO
        
        # Crear imagen de prueba 512x512
        img = Image.new('RGB', (512, 512), color='blue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([100, 100, 400, 400], fill='red')
        
        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        payload = {
            "model": "gen3a_turbo",
            "input": {
                "prompt": "A beautiful landscape with mountains and rivers",
                "image": f"data:image/png;base64,{img_str}",
                "duration": 3,
                "motion": "medium"
            }
        }
        
        print("   🔄 Enviando solicitud de generación...")
        response = requests.post(f"{RUNWAY_API_URL}/generations", headers=headers, json=payload, timeout=60)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Generation test successful!")
            result = response.json()
            print(f"   🔍 Response keys: {list(result.keys())}")
            if "output" in result and len(result["output"]) > 0:
                video_url = result["output"][0].get("url")
                print(f"   🎥 Video URL: {video_url}")
            elif "data" in result and len(result["data"]) > 0:
                video_url = result["data"][0].get("url")
                print(f"   🎥 Video URL: {video_url}")
        elif response.status_code == 402:
            print("   💳 Error 402: No credits available - Necesitas cargar créditos en RunwayML")
        elif response.status_code == 422:
            error_data = response.json()
            print(f"   ❌ Validation error: {error_data}")
        else:
            error_data = response.json()
            print(f"   ❌ Error: {error_data}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    debug_runway_connection()
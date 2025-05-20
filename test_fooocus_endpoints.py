import requests

base_url = "http://localhost:7865"

# 1. Prueba GET a /info y /config
def test_info_config():
    for endpoint in ["/info", "/config"]:
        try:
            r = requests.get(base_url + endpoint)
            print(f"GET {endpoint} -> Status: {r.status_code}")
            print(r.text[:500] + ("..." if len(r.text) > 500 else ""))
        except Exception as e:
            print(f"Error GET {endpoint}: {e}")

# 2. Prueba POST a /api/predict/, /api/txt2img/, /api/generate/
def test_api_endpoints():
    endpoints = ["/api/predict/", "/api/txt2img/", "/api/generate/", "/run/predict/", "/run/txt2img/", "/run/generate/"]
    payload = {"data": ["a test prompt"]}
    headers = {"Content-Type": "application/json"}
    for endpoint in endpoints:
        try:
            r = requests.post(base_url + endpoint, json=payload, headers=headers)
            print(f"POST {endpoint} -> Status: {r.status_code}")
            print(r.text[:500] + ("..." if len(r.text) > 500 else ""))
        except Exception as e:
            print(f"Error POST {endpoint}: {e}")

if __name__ == "__main__":
    print("--- Test GET /info y /config ---")
    test_info_config()
    print("\n--- Test POST /api/* y /run/* ---")
    test_api_endpoints()

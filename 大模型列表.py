import requests

# ====================== 你只填这里 ======================
API_KEY = "YOUR API KEYS"
API_BASE = "https://api-inference.modelscope.cn"  # 魔塔官方域名
# ======================================================

def list_available_models():
    url = f"{API_BASE}/v1/models"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("=== 魔塔API 可用模型列表 ===")
        for model in data.get("data", []):
            print("- " + model["id"])
    except Exception as e:
        print("获取模型列表失败：", str(e))

if __name__ == "__main__":
    list_available_models()
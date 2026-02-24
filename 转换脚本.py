import os
import base64
import requests

# ====================== 【使用时仅需修改这3处】 ======================
API_KEY = "YOUR API KEYS"          # 替换成你的API Key
IMAGE_FOLDER = r"图片/"   # 你的日记照片文件夹路径
OUTPUT_FILE = "转文字结果.txt"   # 最终输出的文本文件名
BATCH_SIZE = 3                      # 每次最多识别的图片数量
# ==============================================================

# 魔塔OpenAI兼容接口地址
API_BASE = "https://api-inference.modelscope.cn/v1"
# 最优手写识别模型
MODEL_NAME = "Qwen/Qwen3-VL-8B-Instruct" #替换成你要用到的模型
# 支持的图片格式
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

def image_to_base64(image_path):
    """将图片转为base64编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def recognize_batch(batch_images):
    """批量识别一组图片（最多3张）"""
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建提示词，明确要求按顺序输出每张图片的内容
    prompt = f"""
你是专业的中文手写文字识别助手，现在需要识别{len(batch_images)}张图片中的手写日记内容：
1. 逐行完整转录所有文字，严格按手写排版顺序输出
2. 仅输出识别到的纯文字，不添加任何解释、总结、标点修改
3. 字迹工整度一般，遇到模糊/潦草的字尽量按字形合理推测
4. 不要遗漏任何一行内容，包括备注、批注类小字
5. 输出格式要求：
   - 每张图片的识别结果用分隔符 "===== 图片N: 文件名 =====" 开头
   - 例如：
     ===== 图片1: IMG001.jpg =====
     这里是第一张图片的文字...
     ===== 图片2: IMG002.jpg =====
     这里是第二张图片的文字...
    """.strip()

    # 构建消息内容：先放提示词，再依次放入所有图片
    content = [{"type": "text", "text": prompt}]
    for img_path in batch_images:
        b64_data = image_to_base64(img_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}
        })

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.05,
        "max_tokens": 16384  # 增大上下文以容纳多张图片的结果
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"【批量识别失败】：{str(e)}"

def main():
    # 获取并排序所有图片
    image_files = sorted([
        f for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith(IMAGE_EXTS)
    ])
    total_images = len(image_files)
    
    if total_images == 0:
        print("⚠️ 未在指定文件夹找到图片文件！")
        return

    print(f"✅ 共找到 {total_images} 张日记图片，按 {BATCH_SIZE} 张/批进行识别...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 按批次处理图片
        for i in range(0, total_images, BATCH_SIZE):
            batch_names = image_files[i:i+BATCH_SIZE]
            batch_paths = [os.path.join(IMAGE_FOLDER, name) for name in batch_names]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (total_images + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"正在处理第 {batch_num}/{total_batches} 批：{len(batch_names)} 张图片")
            print(f"包含文件：{', '.join(batch_names)}")

            # 调用批量识别
            batch_result = recognize_batch(batch_paths)
            
            # 写入结果
            f.write(f"========== 第 {batch_num} 批识别结果 ==========\n")
            f.write(batch_result + "\n\n")
            f.flush()
            print("✅ 本批处理完成，结果已写入文件。\n")

    print(f"\n🎉 全部识别完成！结果已保存到：{os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()
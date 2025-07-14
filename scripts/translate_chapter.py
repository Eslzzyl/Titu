import os
import glob
import openai
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TRANSLATE_MODEL_API_BASE_URL,
    TRANSLATE_MODEL_API_KEY,
    TRANSLATE_MODEL_NAME,
    TRANSLATE_MODEL_TEMPERATURE,
)

# 初始化OpenAI客户端
client = openai.OpenAI(
    base_url=TRANSLATE_MODEL_API_BASE_URL, api_key=TRANSLATE_MODEL_API_KEY
)

# 设置并行请求的最大线程数
MAX_WORKERS = 1


def get_text_files(directory):
    """获取指定目录下的所有文本文件"""
    files_path = os.path.join(directory, "*.txt")
    return glob.glob(files_path)


def translate_text(text):
    """使用OpenAI SDK将文本翻译成英文"""
    try:
        response = client.chat.completions.create(
            model=TRANSLATE_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following text from Chinese to English. Maintain the original formatting as much as possible.",
                },
                {"role": "user", "content": text},
            ],
            temperature=TRANSLATE_MODEL_TEMPERATURE,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"翻译出错: {e}")
        return None


def process_file(file_path, output_dir):
    """处理单个文件的翻译，用于并行执行"""
    filename = os.path.basename(file_path)
    print(f"处理文件: {filename}")

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 翻译内容
        translated_text = translate_text(content)

        if translated_text:
            # 保存翻译后的内容到单独的文件
            translated_file_path = os.path.join(output_dir, f"translated_{filename}")
            with open(translated_file_path, "w", encoding="utf-8") as f:
                f.write(translated_text)

            print(f"文件 {filename} 翻译完成")
            return filename, translated_text
        else:
            print(f"文件 {filename} 翻译失败")
            return None

    except Exception as e:
        print(f"处理文件 {filename} 时出错: {e}")
        return None


def main():
    # 输入和输出路径
    input_dir = "./temp/chapters/"
    output_dir = "./temp/translated/"
    combined_output = "./temp/combined_translation.txt"

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有文本文件
    text_files = get_text_files(input_dir)
    print(f"找到 {len(text_files)} 个文件需要翻译")

    translated_contents = []

    # 使用线程池并行处理翻译任务
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_file, file_path, output_dir): file_path
            for file_path in text_files
        }

        # 处理完成的任务
        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                filename, translated_text = result
                translated_contents.append(
                    f"--- {filename} ---\n\n{translated_text}\n\n"
                )

    # 合并所有翻译内容
    if translated_contents:
        with open(combined_output, "w", encoding="utf-8") as f:
            f.write("\n".join(translated_contents))
        print(f"所有翻译内容已合并到 {combined_output}")

    print("翻译过程完成")


if __name__ == "__main__":
    main()

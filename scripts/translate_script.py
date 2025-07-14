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
MAX_WORKERS = 2


def get_script_files(directory):
    """获取指定目录下的所有脚本文件"""
    files_path = os.path.join(directory, "*.rpy")
    return glob.glob(files_path)


def translate_text(text):
    """使用OpenAI SDK将文本翻译成英文"""
    try:
        response = client.chat.completions.create(
            model=TRANSLATE_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator specializing in game scripts. Translate the following script from Chinese to English. Only translate dialogues and narration, keep other content unchanged.",
                },
                {"role": "user", "content": text},
            ],
            temperature=TRANSLATE_MODEL_TEMPERATURE,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"翻译出错: {e}")
        return None


def process_script(file_path, output_dir):
    """处理单个脚本文件的翻译，用于并行执行"""
    filename = os.path.basename(file_path)
    print(f"处理脚本: {filename}")

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 翻译内容
        translated_text = translate_text(content)

        if translated_text:
            # 保存翻译后的内容到输出目录
            translated_file_path = os.path.join(output_dir, f"translated_{filename}")
            with open(translated_file_path, "w", encoding="utf-8") as f:
                f.write(translated_text)

            print(f"脚本 {filename} 翻译完成")
            return True
        else:
            print(f"脚本 {filename} 翻译失败")
            return False

    except Exception as e:
        print(f"处理脚本 {filename} 时出错: {e}")
        return False


def main():
    # 输入和输出路径
    input_dir = "./temp/scripts/"
    output_dir = "./temp/translated_scripts/"

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有脚本文件
    script_files = get_script_files(input_dir)
    print(f"找到 {len(script_files)} 个脚本需要翻译")

    successful_translations = 0

    # 使用线程池并行处理翻译任务
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_script, file_path, output_dir): file_path
            for file_path in script_files
        }

        # 处理完成的任务
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            filename = os.path.basename(file_path)
            try:
                result = future.result()
                if result:
                    successful_translations += 1
            except Exception as e:
                print(f"翻译脚本 {filename} 时发生异常: {e}")

    print(
        f"翻译过程完成。成功翻译 {successful_translations}/{len(script_files)} 个脚本文件"
    )


if __name__ == "__main__":
    main()

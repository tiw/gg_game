import os
import re
import json
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import words as nltk_words
from nltk.corpus import wordnet
from dotenv import load_dotenv
from dashscope import Generation

# 下载必要的NLTK数据
def download_nltk_data():
    resources = ['punkt', 'words', 'wordnet']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"下载 NLTK 资源: {resource}")
            nltk.download(resource, quiet=True)

# 确保NLTK数据被下载
# download_nltk_data()

# 加载环境变量
load_dotenv()

# 初始化dashscope客户端
Generation.api_key = os.getenv("DASHSCOPE_API_KEY")

# 获取英语常用词集合
english_words = set(w.lower() for w in nltk_words.words())

def get_word_definition(word):
    # 获取WordNet英文定义
    synsets = wordnet.synsets(word)
    english_definition = synsets[0].definition() if synsets else "无英文定义"

    # 获取通义千问中文定义
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=f"请简洁地解释英语单词'{word}'的含义:",
            max_tokens=50
        )
        if response.status_code == 200:
            chinese_definition = response.output.text.strip()
        else:
            chinese_definition = "无法获取中文定义"
    except Exception as e:
        print(f"获取单词定义时出错: {e}")
        chinese_definition = "获取中文定义失败"

    return f"英文: {english_definition}\n中文: {chinese_definition}"

def load_progress(book_title):
    progress_file = f"books/{book_title}_progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"current_position": 0, "last_read_date": None}

def save_progress(book_title, progress):
    progress_file = f"books/{book_title}_progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f)

def is_difficult_word(word, sentence):
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=f"对于小学生来说,在以下句子中,'{word}'是否是一个难词？请只回答'是'或'否'：\n\n{sentence}",
            max_tokens=10
        )
        if response.status_code == 200:
            return response.output.text.strip().lower() == '是'
        else:
            print(f"判断难词时出错: {response.status_code}")
            return False
    except Exception as e:
        print(f"判断难词时出错: {e}")
        return False

def analyze_text(text):
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=f"请分析以下文本,找出对小学生来说的难词,并给出这些词的中文和英文解释。格式如下:\n难词1: 中文解释 | 英文解释\n难词2: 中文解释 | 英文解释\n\n文本:\n{text}",
            max_tokens=1000
        )
        if response.status_code == 200:
            return response.output.text.strip()
        else:
            print(f"分析文本时出错: {response.status_code}")
            return "无法获取分析结果"
    except Exception as e:
        print(f"分析文本时出错: {e}")
        return "分析文本失败"

def find_start_of_content(content):
    # 查找正文开始的标记
    content_patterns = [
        r"\bCHAPTER I\.?\b",
        r"\bCHAPTER 1\.?\b",
        r"\bCHAPTER ONE\.?\b",
        r"\bI\.?\b",  # 匹配罗马数字 I
        r"\b1\.?\b",  # 匹配阿拉伯数字 1
    ]
    
    for pattern in content_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # 找到章节标记后，向前查找最近的段落开始
            paragraph_start = content.rfind('\n\n', 0, match.start())
            if paragraph_start != -1:
                return paragraph_start + 2  # +2 to skip the newline characters
            else:
                return match.start()
    
    # 如果没有找到 "Chapter I" 或类似标记，返回 0（从头开始）
    print("警告：未找到 'Chapter I' 或类似的章节标记。从文件开头开始阅读。")
    return 0

def read_book(book_path):
    book_title = os.path.splitext(os.path.basename(book_path))[0]
    with open(book_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    progress = load_progress(book_title)
    current_position = progress["current_position"]
    
    today = datetime.now().date().isoformat()
    if progress["last_read_date"] != today:
        current_position = 0
    
    if current_position == 0:
        current_position = find_start_of_content(content)
    
    paragraphs = content[current_position:].split('\n\n')
    daily_content = ""
    paragraphs_read = 0
    
    while len(daily_content) < 200 and paragraphs_read < len(paragraphs):
        daily_content += paragraphs[paragraphs_read] + "\n\n"
        paragraphs_read += 1
    
    print(f"今天的阅读内容 ({len(word_tokenize(daily_content))} 词):\n")
    print(daily_content)
    print()
    
    print("难词分析:")
    analysis_result = analyze_text(daily_content)
    print(analysis_result)
    print()
    
    progress["current_position"] = current_position + len(daily_content)
    progress["last_read_date"] = today
    save_progress(book_title, progress)

def main():
    books_dir = "books"
    if not os.path.exists(books_dir):
        print(f"'{books_dir}' 目录不存在。请确保书籍文件夹名称正确。")
        return

    books = [f for f in os.listdir(books_dir) if f.endswith('.txt')]
    if not books:
        print(f"在 '{books_dir}' 目录下没有找到.txt文件。请确保书籍文件在正确的位置。")
        return

    print("可用的书籍:")
    for i, book in enumerate(books, 1):
        print(f"{i}. {book}")
    
    while True:
        try:
            choice = int(input("请选择一本书 (输入数���): ")) - 1
            if 0 <= choice < len(books):
                read_book(os.path.join(books_dir, books[choice]))
                break
            else:
                print("无效的选择，请重新输入。")
        except ValueError:
            print("请输入有效的数字。")

if __name__ == "__main__":
    main()

import os
import re
import json
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import words as nltk_words
from nltk.corpus import wordnet

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
download_nltk_data()

# 设置每天阅读的单词数
DAILY_WORD_COUNT = 200

# 获取英语常用词集合
english_words = set(w.lower() for w in nltk_words.words())

def get_word_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        return synsets[0].definition()
    return "No definition found"

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

def is_difficult_word(word):
    return word.lower() not in english_words and len(word) > 3

def analyze_sentence(sentence):
    words = word_tokenize(sentence)
    difficult_words = [(word, get_word_definition(word)) for word in words if is_difficult_word(word)]
    return difficult_words

def read_book(book_path):
    book_title = os.path.splitext(os.path.basename(book_path))[0]
    with open(book_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    progress = load_progress(book_title)
    current_position = progress["current_position"]
    
    today = datetime.now().date().isoformat()
    if progress["last_read_date"] != today:
        current_position = 0
    
    words = word_tokenize(content[current_position:])
    daily_content = " ".join(words[:DAILY_WORD_COUNT])
    sentences = sent_tokenize(daily_content)
    
    print(f"今天的阅读内容 ({len(word_tokenize(daily_content))} 词):\n")
    for sentence in sentences:
        print(sentence)
        difficult_words = analyze_sentence(sentence)
        if difficult_words:
            print("难词:")
            for word, definition in difficult_words:
                print(f"  {word}: {definition}")
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
            choice = int(input("请选择一本书 (输入数字): ")) - 1
            if 0 <= choice < len(books):
                read_book(os.path.join(books_dir, books[choice]))
                break
            else:
                print("无效的选择，请重新输入。")
        except ValueError:
            print("请输入有效的数字。")

if __name__ == "__main__":
    main()

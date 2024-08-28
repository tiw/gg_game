from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from nltk.tokenize import word_tokenize
from dashscope import Generation
from dotenv import load_dotenv

# 导入之前的函数
from reader_assis import load_progress, save_progress, find_start_of_content

app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 初始化dashscope客户端
Generation.api_key = os.getenv("DASHSCOPE_API_KEY")

def analyze_text(text):
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=f"请分析以下文本,找出对小学生来说的难词,并给出这些词的中文和英文解释。格式如下:\n英文单词: 中文解释 | 英文解释\n英文单词: 中文解释 | 英文解释\n\n文本:\n{text}",
            max_tokens=1000
        )
        if response.status_code == 200:
            result = response.output.text.strip()
            print("通义千问返回的分析结果：", result)  # 添加调试信息
            return result
        else:
            print(f"分析文本时出错: {response.status_code}")
            return "无法获取分析结果"
    except Exception as e:
        print(f"分析文本时出错: {e}")
        return "分析文本失败"

@app.route('/')
def index():
    books = [f for f in os.listdir('books') if f.endswith('.txt')]
    return render_template('index.html', books=books)

@app.route('/read', methods=['POST'])
def read():
    book_title = request.form['book']
    book_path = os.path.join('books', book_title)
    
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
    
    word_count = len(word_tokenize(daily_content))
    
    analysis_result = analyze_text(daily_content)
    
    progress["current_position"] = current_position + len(daily_content)
    progress["last_read_date"] = today
    save_progress(book_title, progress)
    
    response_data = {
        'content': daily_content,
        'word_count': word_count,
        'analysis': analysis_result
    }
    print("发送给前端的数据：", response_data)  # 添加调试信息
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

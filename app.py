import json
from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from dashscope import Generation
from dotenv import load_dotenv
import re
import uuid

# 导入之前的函数
from reader_assis import load_progress, save_progress, find_start_of_content
import nltk
nltk.download('punkt')
app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 初始化dashscope客户端
Generation.api_key = os.getenv("DASHSCOPE_API_KEY")

def analyze_text(text):
    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=f"""请分析以下文本，找出对小学生来说的难词，并给出这些词的中文解释、英文解释和例句。
            请以JSON格式返回结果，格式如下：
            {{
                "words": [
                    {{
                        "word": "英文单词",
                        "chinese_explanation": "中文解释",
                        "english_explanation": "explain in english",
                        "example": "例句"
                    }},
                    // 更词...
                ]
            }}
            
            文本:
            {text}""",
            max_tokens=1500
        )
        if response.status_code == 200:
            result = response.output.text.strip()
            print("通义千问返回的分析结果：", result)
            
            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                for i, word_info in enumerate(data['words']):
                    word_info['id'] = f"word_{i}"
                return data
            else:
                return {"error": f"无法从返回结果中提取JSON: {result[:100]}..."}
        else:
            print(f"分析文本时出错: {response.status_code}")
            return {"error": f"无法获取分析结果: {response.status_code}"}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return {"error": f"JSON解析错误: {e}"}
    except Exception as e:
        print(f"分析文本时出错: {e}")
        return {"error": f"分析文本失败: {str(e)}"}

@app.route('/')
def index():
    books = [f for f in os.listdir('books') if f.endswith('.txt')]
    return render_template('index.html', books=books)

@app.route('/read', methods=['POST'])
def read():
    book_title = request.form['book']
    book_path = os.path.join('books', book_title)
    
    with open(book_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = clean_text(content)

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
    
    word_count = len(simple_word_tokenize(daily_content))
    
    if not daily_content.strip():
        analysis_result = {"error": "没有可分析的内容"}
    else:
        analysis_result = analyze_text(daily_content)
    
    if "error" in analysis_result:
        print(f"分析结果出错: {analysis_result['error']}")

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

# 添加这个简单的分词函数
def simple_word_tokenize(text):
    return text.split()

def clean_text(text):
    # 只保留ASCII字符和换行符
    text = ''.join(char for char in text if ord(char) < 128 or char == '\n')
    
    # # 使用正则表达式移除多余的空白字符，但保留段落结构
    # text = re.sub(r'\s+', ' ', text)
    # text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 清理每个段落,但保留段落结构
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        # 移除段落内的多余空格，但保留行首和行尾的空格
        cleaned_paragraph = '\n'.join([line.strip() for line in paragraph.split('\n')])
        
        if cleaned_paragraph:
            cleaned_paragraphs.append(cleaned_paragraph)
    
    # 使用两个换行符重新连接段落
    return '\n\n'.join(cleaned_paragraphs)

if __name__ == '__main__':
    app.run(debug=True)

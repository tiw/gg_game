import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from dashscope import Generation
from dotenv import load_dotenv
import re
import uuid
import sqlite3
import hashlib
import logging
from logging.handlers import RotatingFileHandler

# 创建日志目录（如果不存在）
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 设置日志
log_file = os.path.join(log_dir, 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 导入之前的函数
from reader_assis import find_start_of_content

# 检查 NLTK 数据是否已下载
nltk_data_path = os.path.expanduser("~/nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
    print("首次运行，正在下载 NLTK 数据...")
    nltk.download('punkt', quiet=True)
    print("NLTK 数据下载完成。")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 请更改为一个安全的随机字符串

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# 加载环境变量
load_dotenv()

# 初始化dashscope客户端
Generation.api_key = os.getenv("DASHSCOPE_API_KEY")

def clean_and_parse_json(json_string):
    # 使用正则表达式提取JSON部分
    json_match = re.search(r'\{[\s\S]*\}', json_string)
    if json_match:
        json_str = json_match.group(0)
        # 移除多余的逗号
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # 确保所有的键都有双引号
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return {"error": f"无法解析分析结果: {e}"}
    else:
        return {"error": "无法从返回结果中提取JSON"}

# 初始化数据库
def init_db():
    conn = sqlite3.connect('cache.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_cache
                 (content_hash TEXT PRIMARY KEY, analysis TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def get_cached_analysis(content_hash):
    conn = sqlite3.connect('cache.db')
    c = conn.cursor()
    c.execute("SELECT analysis FROM analysis_cache WHERE content_hash = ?", (content_hash,))
    result = c.fetchone()
    conn.close()
    if result:
        logger.info(f"从缓存中获取分析结果: {content_hash[:10]}...")
        try:
            cached_data = json.loads(result[0])
            if "words" in cached_data and isinstance(cached_data["words"], list):
                logger.info(f"成功从缓存中读取数据: {content_hash[:10]}...")
                return cached_data
            else:
                logger.error(f"缓存数据格式错误: {content_hash[:10]}...")
        except json.JSONDecodeError:
            logger.error(f"缓存数据解析错误: {content_hash[:10]}...")
    else:
        logger.info(f"缓存中未找到数据: {content_hash[:10]}...")
    return None

def save_analysis_to_cache(content_hash, analysis):
    if "words" not in analysis or not isinstance(analysis["words"], list):
        logger.error(f"尝试缓存格式错误的数据: {content_hash[:10]}...")
        return
    
    conn = sqlite3.connect('cache.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO analysis_cache (content_hash, analysis) VALUES (?, ?)",
                  (content_hash, json.dumps(analysis)))
        conn.commit()
        logger.info(f"成功保存分析结果到缓存: {content_hash[:10]}...")
    except sqlite3.Error as e:
        logger.error(f"保存缓存时出错: {e}")
    finally:
        conn.close()

def analyze_text(text):
    content_hash = hashlib.md5(text.encode()).hexdigest()
    
    cached_result = get_cached_analysis(content_hash)
    if cached_result:
        logger.info(f"使用缓存的分析结果: {content_hash[:10]}...")
        return cached_result

    logger.info(f"缓存未命中，正在查询 qwen: {content_hash[:10]}...")
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
                    // 更多词...
                ]
            }}
            
            文本:
            {text}""",
            max_tokens=1500
        )
        if response.status_code == 200:
            result = response.output.text.strip()
            logger.info(f"qwen 返回的分析结果：{result[:100]}...")
            
            data = clean_and_parse_json(result)
            if "error" not in data and "words" in data and isinstance(data["words"], list):
                for i, word_info in enumerate(data['words']):
                    word_info['id'] = f"word_{i}"
                save_analysis_to_cache(content_hash, data)
                logger.info(f"成功分析并缓存结果: {content_hash[:10]}...")
                return data
            else:
                logger.error(f"分析结果格式错误: {data.get('error', '未知错误')}")
                return {"error": "分析结果格式错误"}
        else:
            logger.error(f"分析文本时出错: {response.status_code}")
            return {"error": f"无法获取分析结果: {response.status_code}"}
    except Exception as e:
        logger.error(f"分析文本时出错: {e}")
        return {"error": f"分析文本失败: {str(e)}"}

@app.route('/')
@login_required
def index():
    books = [f for f in os.listdir('books') if f.endswith('.txt')]
    return render_template('index.html', books=books)

@app.route('/read', methods=['POST'])
@login_required
def read():
    data = request.json
    if not data or 'book' not in data:
        return jsonify({"error": "No book specified"}), 400
    
    book_title = data['book']
    book_path = os.path.join('books', book_title)
    
    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    with open(book_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = clean_text(content)

    progress = load_progress(book_title, current_user.id)
    current_position = progress["current_position"]
    
    today = datetime.now().date().isoformat()
    if progress["last_read_date"] != today:
        current_position = 0
    
    if current_position == 0:
        current_position = find_start_of_content(content)
    
    paragraphs = content[current_position:].split('\n\n')
    daily_content = ""
    paragraphs_read = 0
    analysis_results = []
    
    while len(daily_content) < 200 and paragraphs_read < len(paragraphs):
        paragraph = paragraphs[paragraphs_read].strip()
        daily_content += paragraph + "\n\n"
        paragraphs_read += 1
        
        # 分析每个段落
        if paragraph:
            analysis_result = analyze_text(paragraph)
            analysis_results.append(analysis_result)
    
    word_count = len(simple_word_tokenize(daily_content))
    
    if not daily_content.strip():
        analysis_result = {"error": "没有可分析的内容"}
    else:
        analysis_result = analysis_results
    
    if isinstance(analysis_result, list) and any("error" in result for result in analysis_result):
        logger.error(f"分析结果出错: {[result['error'] for result in analysis_result if 'error' in result]}")

    progress["current_position"] = current_position + len(daily_content)
    progress["last_read_date"] = today
    save_progress(book_title, progress, current_user.id)
    
    response_data = {
        'content': daily_content,
        'word_count': word_count,
        'analysis': analysis_result
    }
    logger.info(f"发送给前端的数据：{str(response_data)[:200]}...")  # 添加调试信息
    return jsonify(response_data)

# 添加这个简单的分词函数
def simple_word_tokenize(text):
    return text.split()

def clean_text(text):
    # 只保留ASCII字符和换行符
    text = ''.join(char for char in text if ord(char) < 128 or char == '\n')
    
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

@app.route('/evaluate_summary', methods=['POST'])
def evaluate_summary():
    data = request.json
    original_text = data.get('original_text')
    summary = data.get('summary')

    if not original_text or not summary:
        return jsonify({"error": "缺少原文或复述内容"}), 400

    try:
        # 第一次调用：评价复述
        evaluation_response = Generation.call(
            model='qwen-turbo',
            prompt=f"""请评价以下复述内容，并给出改进建议。

原文：
{original_text}

复述：
{summary}

请从以下几个方面进行评价：
1. 内容准确性
2. 主要观点的覆盖程度
3. 语言表达的流畅性
4. 逻辑结构

请以JSON格式返回结果，格式如下：
{{
    "evaluation": "总体评价",
    "accuracy": "内容准确性评价",
    "coverage": "主要观点覆盖程度评价",
    "fluency": "语言表达流畅性评价",
    "structure": "逻辑结构评价",
    "suggestions": "改进建议"
}}
""",
            max_tokens=1000
        )

        if evaluation_response.status_code != 200:
            return jsonify({"error": f"无法获取评价结果: {evaluation_response.status_code}"}), 500

        evaluation_result = clean_and_parse_json(evaluation_response.output.text.strip())

        # 确保所有必要的字段都存在
        required_fields = ['evaluation', 'accuracy', 'coverage', 'fluency', 'structure', 'suggestions']
        for field in required_fields:
            if field not in evaluation_result:
                evaluation_result[field] = "评价生成中，请稍后再试"

        # 第二次调用：生成范文
        example_response = Generation.call(
            model='qwen-turbo',
            prompt=f"""基于以下原文和评价意见，请生成一个优秀的英文复述范文。

原文：
{original_text}

评价意见：
{evaluation_result['suggestions']}

请用英文生成一个简洁、准确、流畅的复述范文，确保涵盖原文的主要观点，并改进了之前复述中的不足。
""",
            max_tokens=1000
        )

        if example_response.status_code != 200:
            evaluation_result['example_summary'] = "评价生成中，请稍后再试"
        else:
            evaluation_result['example_summary'] = example_response.output.text.strip()

        return jsonify(evaluation_result)

    except Exception as e:
        return jsonify({"error": f"评价复述失败: {str(e)}"}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            conn.close()
            flash('用户名已存在')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1]))
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录')
    return redirect(url_for('index'))

def load_progress(book_title, user_id):
    progress_file = f'progress_{user_id}_{book_title}.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {"current_position": 0, "last_read_date": ""}

def save_progress(book_title, progress, user_id):
    progress_file = f'progress_{user_id}_{book_title}.json'
    with open(progress_file, 'w') as f:
        json.dump(progress, f)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

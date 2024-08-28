import requests
import os

def download_book(book_id, title):
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    response = requests.get(url)
    
    if response.status_code == 200:
        # 清理文件名
        filename = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{filename}.txt"
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"已下载: {filename}")
    else:
        print(f"下载 {title} (ID: {book_id}) 时出错: HTTP状态码 {response.status_code}")

def get_popular_kids_books():
    # 这里我们手动指定一些适合儿童的书籍ID和标题
    books = [
        (11, "Alice's Adventures in Wonderland"),
        (12, "Through the Looking-Glass"),
        (13, "The Jungle Book"),
        (14, "The Wonderful Wizard of Oz"),
        (15, "Grimms' Fairy Tales"),
        (16, "Peter Pan"),
        (17, "Pinocchio"),
        (18, "The Adventures of Tom Sawyer"),
        (19, "The Adventures of Huckleberry Finn"),
        (20, "Treasure Island")
    ]
    return books

def main():
    if not os.path.exists('books'):
        os.makedirs('books')
    os.chdir('books')
    
    books = get_popular_kids_books()
    for book_id, title in books:
        download_book(book_id, title)

if __name__ == "__main__":
    main()

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath("main.py"):
            # 当main.py文件被修改时，重启程序
            restart_program()

def restart_program():
    # 关闭当前正在运行的pgzrun进程（这里假设pgzrun是你直接在命令行中运行的，如果是IDE可能需要其他方式关闭）
    subprocess.run(["pkill", "-f", "pgzrun"])  
    # 等待一小段时间确保进程完全关闭
    time.sleep(1)
    # 重新运行main.py
    subprocess.run(["pgzrun", "main.py"])

if __name__ == "__main__":
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath("main.py")), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)  # 主线程保持运行，以便观察者可以继续监视文件变化
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
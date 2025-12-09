import sys
import json
import os

# 检测是否在 Web 环境 (Pygbag/Emscripten)
IS_WEB = sys.platform == "emscripten"

if IS_WEB:
    # 在 Pygbag 环境下，platform 模块会被注入 window 对象
    from platform import window

def save_game(data, filename="save.json"):
    """
    保存游戏数据
    :param data: 字典格式的游戏数据
    :param filename: 文件名 (在 Web 端作为 localStorage 的 key)
    """
    try:
        json_str = json.dumps(data)
        
        if IS_WEB:
            # Web 端：存入 LocalStorage
            window.localStorage.setItem(filename, json_str)
            print(f"[Web] Game saved to LocalStorage: {filename}")
        else:
            # 桌面端：存入本地文件
            with open(filename, "w") as f:
                f.write(json_str)
            print(f"[Desktop] Game saved to file: {filename}")
            
    except Exception as e:
        print(f"Save failed: {e}")

def load_game(filename="save.json", default_data=None):
    """
    加载游戏数据
    :param filename: 文件名
    :param default_data: 如果没有存档，返回的默认数据
    :return: 字典格式的游戏数据
    """
    if default_data is None:
        default_data = {}

    try:
        if IS_WEB:
            # Web 端：从 LocalStorage 读取
            json_str = window.localStorage.getItem(filename)
            # localStorage 返回 None 表示 key 不存在
            if json_str is None:
                print("[Web] No save found, using default.")
                return default_data
            return json.loads(json_str)
        else:
            # 桌面端：从本地文件读取
            if not os.path.exists(filename):
                print("[Desktop] No save file found, using default.")
                return default_data
            
            with open(filename, "r") as f:
                return json.load(f)
                
    except Exception as e:
        print(f"Load failed: {e}, using default.")
        return default_data

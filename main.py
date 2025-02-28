import requests
import inquirer
import threading
import sys
import time
import json

from config.config import API_KEY, API_ENDPOINT
from presets.cat import cat_preset
from presets.azuki import azuki_preset
from presets.javascript import javascript_preset


# TODOs
# 1. 简单的交互菜单（开始新对话、退出、切换模式、调整参数、导出数据等）
# 2. 多种颜色高亮（不同角色）
# 3. Markdown 支持
# 4. 多行输入支持
# 5. 折叠
# 6. 排版优化
# 7. 群聊
# 8. 保存聊天数据


# Global Context
messages = []
selected_preset_name = "DeepSeek"

# Spinner
def spinning_cursor(stop_event):
    spinner = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r正在思考 {spinner[idx % len(spinner)]} ")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)  # Spin speed
    sys.stdout.write("\r" + " " * 20 + "\r")  # Clear
    sys.stdout.flush()

# Character Preset
presets = {
    "无预设": None,
    "乖巧的猫咪": cat_preset,
    "红豆": azuki_preset,
    "Javascript": javascript_preset
}

# Character Select
def select_preset():
    questions = [
        inquirer.List(
            "preset",
            message="请选择一个预设角色",
            choices=list(presets.keys()),
        )
    ]
    answers = inquirer.prompt(questions)
    return answers["preset"]

# DeepSeek Chat
def invoke_deepseek_chat(user_message):
    global messages  # declare messages

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages.append({"role": "user", "content": user_message}) # user messages

    body = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 1.5,
        "stream": False
    }

    # TEST Print Req
    #print("Req:")
    #print(json.dumps(body, ensure_ascii=False, indent=2))

    # Spinner Controller
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinning_cursor, args=(stop_event,))

    try:
        spinner_thread.start()

        response = requests.post(API_ENDPOINT, headers=headers, json=body)

        stop_event.set()
        spinner_thread.join()

        if response.status_code != 200:
            print(f"\nAPI 请求失败: {response.status_code} - {response.text}")
            return None

        # TEST Print Res
        #print("API Res：", response.text)

        # JSON parser
        json_response = response.json()
        assistant_reply = json_response["choices"][0]["message"]["content"]

        messages.append({"role": "assistant", "content": assistant_reply}) # AI messages

        return assistant_reply
    
    except Exception as e:
        stop_event.set()
        spinner_thread.join()
        print(f"\n请求发生错误: {e}")
        return None


# MAIN Main
def main():
    global selected_preset_name  # declare preset name
    print("欢迎使用 DeepSeek—— 地铺戏磕，启动！我是 AI，我是最强 AI！")

    selected_preset = select_preset()
    if selected_preset != "无预设":
        messages.append(presets[selected_preset])
        selected_preset_name = selected_preset

    print("地铺戏磕已启动！（输入 'exit' 退出）")

    while True:
        user_input = input("我: ")

        if user_input.lower() == "exit":
            print("退出对话")
            break

        response = invoke_deepseek_chat(user_input)
        if response:
            print(f"{selected_preset_name}: {response}")

if __name__ == "__main__":
    main()
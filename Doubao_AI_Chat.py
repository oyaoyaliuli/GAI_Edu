import os
import sys
from openai import OpenAI
import time
import csv
import numpy as np

API_list = []
Stu_list = []
user_name = ""
user_API = ""
user_Num = ""
''''
doubao-seed-1-6-lite-251015   
doubao-seed-1-6-251015 
doubao-seed-1-6-flash-250828  

'''

def getPath(relative_path):
    # 判断是否为frozen状态(即为打包运行状态)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)# 返回真实路径


# 读取API列表整个文件并打印
with open(getPath(os.path.join("res","doubao_API_list.csv")), mode='r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        API_list.append(row)
        # print(row)  # 每行作为列表输出
# print(API_list)

# 读取学生信息列表整个文件并打印
with open(getPath(os.path.join('res','Stu_list.csv')), mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        Stu_list.append(row)

#开启对话
print("================== 基于豆包的AI对话助手 ==================")
print("输入 'exit' 或 'quit' 退出对话\n")
user_Num = input("请输入你的学号(访客请输入机器序号):")
T_stu = np.array(Stu_list).T.tolist()[0]
while True: # 根据用户输入设置相应的问候语和API
    if user_Num in T_stu:
        user_name = Stu_list[T_stu.index(user_Num)][1] + "同学"
        user_API = API_list[int((Stu_list[T_stu.index(user_Num)][0])[-2:])-1][1]
        break
    elif 0 < int(user_Num) <= 60:
        user_name = "访客-" + user_Num
        user_API = API_list[int(user_Num)-1][1]
        break
    else:
        user_Num = input("输入错误！请重新输入正确的学号或机器序号：")

# 初始化豆包客户端
client = OpenAI(
    api_key=user_API,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 初始化空的对话历史
conversation_history = []

while True:
    # 获取用户输入
    user_input = input(user_name+",请输入: ")
    # 检查退出命令
    if user_input.lower() in ['exit', 'quit', '退出']:
        print("感谢使用，再见！")
        break
    # 添加用户消息到对话历史
    conversation_history.append({"role": "user", "content": user_input})
    try:
        # 显示思考提示
        thinking_indicator = "正在思考..."
        print(f"\n{thinking_indicator}", end='', flush=True)
        # 发送请求到豆包模型
        start_time = time.time()
        response = client.chat.completions.create(
            model="doubao-seed-1-6-251015",  # 豆包模型名称
            messages=conversation_history,
            max_tokens=2048,
            temperature=1
        )
        # 计算响应时间
        response_time = time.time() - start_time
        # 清除思考提示
        print("\r" + " " * (2 * len(thinking_indicator)) + "\r", end='', flush=True)
        # 获取助手回复
        assistant_reply = response.choices[0].message.content
        print(f"\nAI助手: {assistant_reply}")
        print(f"(响应时间: {response_time:.2f}秒)\n")
        # 添加助手回复到对话历史
        conversation_history.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        # 清除思考提示
        print("\r" + " " * len(thinking_indicator) + "\r", end='', flush=True)
        print(f"\n发生错误: {e}\n")
        # 出错时移除最后一条用户消息

        conversation_history.pop()

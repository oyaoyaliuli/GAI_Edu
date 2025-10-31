import os
import sys
import requests
from openai import OpenAI
import time
import csv
import numpy as np

'''
模型列表：

'''


API_list = []
Stu_list = []
user_name = ""  # 学生姓名
user_API = ""  # 分配给该学生的API
user_Num = ""  # 学生学号
user_class = ""  # 学生所在班级

# 多行输入函数
def My_input():
    lines = []
    while True:
        line = input()
        if line in ["END", "end", "End"]:
            break
        elif line in ['exit', 'quit']:
            return "exit"
        lines.append(line)

    text = "\n".join(lines)
    return text

# 获取学生信息表和API文件路径
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
print("================== 基于豆包的AI绘图助手 ==================")
print("输入 'exit' 或 'quit' 退出对话\n")
user_Num = input("请输入你的学号(访客请输入机器序号):")
T_stu = np.array(Stu_list).T.tolist()[0]
while True: # 根据用户输入设置相应的问候语和API
    if user_Num in T_stu:
        user_name = Stu_list[T_stu.index(user_Num)][1] + "同学"
        user_API = API_list[int((Stu_list[T_stu.index(user_Num)][0])[-2:])-1][1]
        user_class = user_Num[4:6]
        break
    elif 0 < int(user_Num) <= 60:
        user_name = "访客_" + user_Num + "  "
        user_API = API_list[int(user_Num)-1][1]
        user_class = ''
        break
    else:
        user_Num = input("输入错误！请重新输入正确的学号或机器序号：")


# 初始化客户端
client = OpenAI(
    # 默认路径
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    #  测试API
    # api_key="test_API",
    # 根据学生的学号分配 API Key。
    api_key=user_API,
)

while True:
    # 获取用户输入
    # user_input = input(user_name+",请输入: ")
    print(user_name.strip()+",请输入(以 'END' 单独一行作为结束): ")
    user_input = My_input()
    # 检查退出命令
    if user_input.lower() in ['exit', 'quit', '退出']:
        print("感谢使用，再见！")
        break
    # 添加用户消息到对话历史

    try:
        # 显示思考提示
        drawing_indicator = "正在生成..."
        print(f"\n{drawing_indicator}", end='', flush=True)
        # 发送请求到模型
        start_time = time.time()
        imagesResponse = client.images.generate(
            model="doubao-seedream-4-0-250828",
            prompt=user_input,
            size="5504x3040",
            response_format="url",
            extra_body={
                "watermark": True,
            },
        )
        # 计算响应时间
        response_time = time.time() - start_time
        # 清除思考提示
        print("\r" + 2 * len(drawing_indicator) * ' ' + "\r", end='', flush=True)
        # 获取图片URL
        image_url = imagesResponse.data[0].url
        print("\nAI绘图助手: 图片生成成功!正在下载...")
        # 下载图片
        try:
            # 获取图片内容
            img_response = requests.get(image_url)
            img_response.raise_for_status()  # 检查请求是否成功
            # 生成文件名（简单起见，使用时间戳）
            filename = user_class + user_name[:-2] + "_" + time.strftime("%Y%m%d%H%M%S") + ".jpg"
            # 保存图片
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            print(f"图片: {filename}  已下载并保存至当前文件夹下")
            print(f"(响应时间: {response_time:.2f}秒)\n")
        except Exception as download_error:
            print(f"\n下载图片时出错: {download_error}\n")

    except Exception as e:
        # 清除思考提示
        print("\r" + " " * len(drawing_indicator) + "\r", end='', flush=True)
        print(f"\n发生错误: {e}\n")


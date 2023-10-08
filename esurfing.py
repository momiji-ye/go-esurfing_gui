import os
import subprocess
from datetime import datetime


def login(account: str, password: str, wlanacip: str = "", wlanusermac: str = ""):
    # 获取当前Python文件所在的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # print("文件目录：", current_directory)

    if wlanusermac == "":
        command = ".\go-esurfing.exe login -a %s -p %s -n %s" % (account, password, wlanacip)
    else:
        command = ".\go-esurfing.exe login -a %s -p %s -n %s -m %s" % (account, password, wlanacip, wlanusermac)
    result = subprocess.run(command, shell=True, text=True, capture_output=True, encoding="utf-8",
                            cwd=current_directory)
    # 获取当前时间
    current_time = datetime.now()

    # 格式化当前时间为字符串
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # # 输出当前时间
    # print(f"当前时间是：{formatted_time}")
    # print("success login!")

    return result.stderr

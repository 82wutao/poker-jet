# 基本环境
1 下载并安装python3，https://www.python.org/downloads/windows/  
2 将python目录加入path 环境变量，可从cmd执行python 命令  
3 下载代码     ？？？？？？？？？？？？？？？？
# 开发环境
1 在代码根目录创建虚拟环境，并激活
```py
python3 -m venv poker-jet
.\poker-jet\Scripts\activate.bat
```
2 添加依赖包
```py
.\poker-jet\Scripts\pip3 install flask
```
3 启动应用
```shell
.\poker-jet\Scripts\python.exe  main.py
```
from flask import Flask
from flask import jsonify
from flask import request
import json

import typing as t
import os

app = Flask(__name__)



def dict_to_response(d:t.Any):
    return jsonify(d)

def mkdir_if_noexisted(path:str):
    if not os.path.exists(path):
        os.mkdir(path)
    if os.path.isfile(path):
        raise "the path is a file"

def read_file(file_path:str)->str:
    with open(file_path, "r", encoding='utf-8') as rd:
        return rd.readline()
        
def write_file(file_path:str,cont:str):
    with open(file_path, "w", buffering=1024, encoding='utf-8') as wr:
        wr.write(cont)
def append_file(file_path:str,cont:str):
    with open(file_path, "a", buffering=1024, encoding='utf-8') as wr:
        wr.write(cont)

@app.route('/health')
def hello_world():
    return dict_to_response({"status":0,"modules":{"db":"ok"}})

@app.route('/list-charts')
def list_charts():
    return dict_to_response([{"name":"king"},{"name":"queen"}])

@app.route('/post-chart',methods=['POST'])
def post_chart():
    data=request.get_data(as_text=True)
    mkdir_if_noexisted("./charts")
    write_file("./charts/a.json",data)
    return 'Hello, World!'

@app.route('/chart/<id>')
def chart(id):
    chart=read_file(f"./charts/{id}.json") 
    return json.loads(chart)


@app.route('/login')
def login():
    return 'Hello, World!'
@app.route('/register')
def register():
    return 'Hello, World!'


app.run(debug=True,port=8090)
#coding:utf-8
from pymongo import MongoClient
from flask import Flask, request, session, redirect, \
    render_template, url_for, flash,jsonify
from werkzeug import secure_filename
import os
import random
import string


#这里写宏和配置信息
g_server_ip='192.168.65.137'
g_server_port=27017
g_db_name='test'  #库名表名先用自己的
g_tb_name='table_one'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])#允许上传的类型
basedir = os.path.abspath(os.path.dirname(__file__))
#-----------------

#获取mongodb客户端
client = MongoClient(g_server_ip,g_server_port)
#获取所要操作的数据库
db = client[g_db_name]
#-----------------

app = Flask(__name__)


#默认配置
app.config.update(dict(
    DEBUG = True,
    SECRET_KEY = 'development',
    USERNAME = 'admin',
    PASSWORD = 'adadad'
))

app.config['UPLOAD_FOLDER']='static/tmp'#上传文件目录



@app.route('/test_it')
def web_show(param='name',word='ak'): #这里不知道怎么传参数，能解决的就帮忙解决一下
    show='<center>'
    try:
        results=db.person.find({param:word})
        for result in results:            
            show=show+str(result)
            show=show+'<p>'
    except:
        return show
    show=show+'</center>'
    return show
    

#正则表达式，用来将查询结果的字段和值分开显示
#def show_column():
    





@app.route('/')
def main_redirect():
    return redirect(url_for('login'))
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''登录'''
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show'))

@app.route('/show')
def show():
    #待实现
    return render_template('showdb.html')

@app.route('/add', methods=['POST'])
def add_document():
    #添加，待实现
    return redirect(url_for('show'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def insert_format(data):
    db.person.save({data})


@app.route('/upload',methods=['GET','POST'],strict_slashes=False)
def upload():
    #上传文件导入数据
    if request.method=='POST':
        file_dir=os.path.join(basedir,app.config['UPLOAD_FOLDER'])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        f=request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname=secure_filename(f.filename)
            ext = fname.rsplit('.',1)[1]  # 获取文件后缀
            #随机生成文件名
            tempname=("".join(random.sample(['z','y','x','w','v',\
                                             'u','t','s'],5)).replace(' '\
                                                                      ,''))
            new_filename=tempname+'.'+ext  # 修改了上传的文件名
            f.save(os.path.join(file_dir,new_filename))  #保存文件到upload目录
            file_insert(new_filename)
            return "上传成功"
        else:
            return "上传失败"

@app.route('/insert_data')
def main_upload():
    for line in db.person.find().limit(1):
        #返回一行数据
        pass

    columns=[]
    for i in line:
        columns.append(i)
    
    return render_template('upload.html',columns=columns)

#读取上传文本导入数据库
def file_insert(filename):
    ext = filename.rsplit('.',1)[1]  # 获取文件后缀
    fenge=' '
    if ext=='txt':
        fenge=' '
    else:
        fenge=','
    path='static\\tmp\\'+filename
    #print(os.path.exists(path))
    if (not os.path.exists(path)):
        #print('no file')
        return
    fp=open(path,'r')
    for line in fp:
        linedata={}
        line=line.strip('\n')
        group=line.split(fenge)    
        for key in group:
            data=key.split(':')
            linedata[data[0]]=data[1]
        #print(linedata)
        db.person.save(linedata)
    db.person.find()
    fp.close()
    os.remove(path)
    

#查询函数，param为查询字段，word为查询的值
def search(param,word):
   try:
       results=db.person.find({param:word})
       for result in results:
           print(result)
   except:
       print('没有结果')


if __name__=='__main__':
    
    #file_insert('wxsuv.txt')
    #search('name','ak')
    app.run()
    


#coding:utf-8
from pymongo import MongoClient
from flask import Flask, request, session, redirect, \
    render_template, url_for, flash, jsonify, abort
from werkzeug import secure_filename
from flask_restful import Api, Resource
import os
import random
import string
import re
from module.base_import import command_import

#这里写宏和配置信息
g_server_ip='192.168.65.137'	#mongodb数据库地址
g_server_port=27017		#数据库端口
g_db_name='test'  		#数据库名
g_tb_name='table_one'		#数据表名
ALLOWED_EXTENSIONS = ['txt', 'csv']#允许上传的类型
#-----------------


#-----------------

app = Flask(__name__)

#默认配置
#flask app config
debug = True,
secret_key = 'development',
upload_dir = 'static/tmp'

app.config.update(dict(
    DEBUG = True,
    SECRET_KEY = secret_key,
    UPLOAD_FOLDER = upload_dir
))
# app.config.from_object('config.py')
# app.config['UPLOAD_FOLDER']='static/tmp'#上传文件目录


'''
#这里导入自定义模块
import s_config
from module.remote_import import upload,import_one,main_upload
import module.base_import
import module.analysis
'''
basedir = os.path.abspath(os.path.dirname(__file__))

#获取mongodb客户端
client = MongoClient(g_server_ip,g_server_port)
#获取所要操作的数据库
db = client[g_db_name]












#接受上传文件并导入数据，删除上传文件
@app.route('/upload',methods=['GET','POST'],strict_slashes=False)
def upload(): 
    if request.method=='POST':
        file_dir=os.path.join(basedir,app.config['UPLOAD_FOLDER'])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        # 从表单的file字段获取文件，myfile为该表单的name值
        f=request.files['file']  
        # 判断是否是允许上传的文件类型
        if f and allowed_file(f.filename):  
            fname=secure_filename(f.filename)
            # 获取文件后缀
            ext = fname.rsplit('.',1)[1]  
            #随机生成文件名
            tempname=("".join(random.sample(['z','y','x','w','v',\
                                             'u','t','s'],5)).replace(\
                                                 ' ',''))
            # 修改了上传的文件名
            new_filename=tempname+'.'+ext
            #保存文件到upload目录
            f.save(os.path.join(file_dir,new_filename))  

            #txt以' '分开，csv以','分开
            fenge=' '
            if ext=='txt':
                fenge=' '
            else:
                fenge=','

            #判断文件是否成功保存
            path='static\\tmp\\'+new_filename
            if (not os.path.exists(path)):
                #print('no file')
                return

            #读取文件转换格式插入数据库
            fp=open(path,'r')
            for line in fp:
                if line=='\n':
                    continue
                linedata={}
                line=line.strip('\n')
                group=line.split(fenge)    
                for key in group:
                    data=key.split(':')
                    linedata[data[0]]=data[1]
                #print(linedata)
                db.person.save(linedata)

            #关闭文件，删除文件
            fp.close()
            os.remove(path)
            return "<center><h1><br><br>上传成功</h1></center>"
        else:
            return "<center><h1><br><br>上传失败</h1></center>"

#快速导入
@app.route('/insert_one',methods=['GET','POST'],strict_slashes=False)
def insert_one():
    if request.method == 'POST':
        for line in db.person.find().limit(1):
            pass
    
        linedata={}
        for i in line:
            if i=='_id':
                continue
            linedata[i]=request.form[i]
        db.person.save(linedata)
        return '<center><h1><br><br>导入成功</h1></center>'

#命令导入
@app.route('/command',methods=['GET','POST'],strict_slashes=False)
def cmd_insert():
    if request.method=='POST':
        cmd=request.form['command']

    command=cmd.split(' ')
    result='<center><h1><br><br>'+command_import(command)+'</h1></center>'
    return result

#信息导入主页面
@app.route('/insert_data')
def main_upload():


    #columns为所有列名的列表
    columns=('name','email','password','passwordhash','xtime')
    return render_template('upload.html',columns=columns)














class Person(Resource):
    '''人员类'''
    def get(self, name=None, email=None):
        #data用于存储获取到的信息
        data = []

        if name and email:
            persons_info = db.person.find({"name": name, "email": email}, {"_id": 0})
        
        elif name:
            persons_info = db.person.find({"name": name}, {"_id": 0})
        
        elif email:
            persons_info = db.person.find({"email": email}, {"_id": 0})
            
        else:
            persons_info = db.person.find({}, {"_id": 0, "update_time": 0}).limit(10)
            for person in persons_info:
                data.append(person)

            return jsonify({"response": data})
 
        if persons_info:
            for person in persons_info:
                data.append(person)

            return jsonify({"status": "ok", "data": data})
        else:
            return {"response": "no person found for {} {}".format(name, email)}

    def post(self):
        '''
        以json格式进行提交文档
        '''
        data = request.get_json()
        if not data:
            return {"response": "ERROR DATA"}
        else:
            name = data.get('name')
            email = email.get('email')

            if name and email:
                if db.person.find_one({"name": name, "email": email}, {"_id": 0}):
                    return {"response": "{{} {} already exists.".format(name, email)}
                else:
                    db.person.insert(data)
            else:
                return redirect(url_for("person"))
    
    def put(self, name, email):
        '''
        根据name和email进行定位更新数据
        '''
        data = request.get_json()
        db.person.update({'name': name, 'email': email},{'$set': data})
        return redirect(url_for("person"))

    def delete(self, email):
        '''
        email作为唯一值, 对其进行删除
        '''
        db.person.remove({'email': email})
        return redirect(url_for("person"))

#添加api资源
api = Api(app)
api.add_resource(Person, "/api", endpoint="person")
api.add_resource(Person, "/api/name/<string:name>", endpoint="name")
api.add_resource(Person, "/api/email/<string:email>", endpoint="email")

@app.route('/')
def main_redirect():
    '''初始页面定向'''
    return redirect(url_for('searchinfo'))
        
def allowed_file(filename):
    '''允许上传的文件类型'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS





#查询信息
@app.route('/searchinfo', methods = ['POST', 'GET'])
def searchinfo():
    if request.method == 'POST':
        
        line = []
        for line in db.person.find().limit(1):
            #返回一行数据
            pass

        #columns为所有列名的列表
        columns=[]
        for i in line:
            columns.append(i)        
        columns.sort()

        if request.form.get('type') in ['name', 'email', 'password', 'passwordHash']:
            found = db.person.find({request.form.get('type'):request.form.get('inputinfo')})
            if found:
                flash('successed')
            else:
                flash('failed')
            
            infos = []
            for doc in found:
                infos.append(doc)
                
            return render_template('searchinfo.html', infos=infos, columns=columns)

        else:
            flash('Erorr')
            return render_template('searchinfo.html')
            
    if request.method == 'GET':
        return render_template('searchinfo.html')







#邮箱后缀分析函数,查询数据库返回所有邮箱后缀及所占比的字典
def analysis_email():
    wei=[]
    count={}
    results= db.person.find({},{"email":1,"_id":0})
    for result in results:
        if 'email' in result:
            #print(result['email'])
            m=re.search('@.+?\.com',result['email'])
            if m:
                email=m.group()
                #print(type(m.group()))
                if not email in wei:
                    wei.append(m.group())
                    count[email]=1
                else:
                    count[email]+=1
    counts=0
    emails={}
    for i in count:
        counts+=count[i]
    for i in count:
        #emails[i]=(str(round(((count[i]/counts)*100)%101,1))+'%')
        emails[i]=round(count[i]/counts,3)
    print(emails)
    return emails

#来源分析函数,查询数据库返回所有来源及所占比的字典
def analysis_source():
    wei=[]
    count={}
    results= db.person.find({},{"source":1,"_id":0})
    for result in results:
        if 'source' in result:
            source=result['source']
            if not source in wei:
                wei.append(source)
                count[source]=1
            else:
                count[source]+=1
    counts=0
    sources={}
    for i in count:
        counts+=count[i]
    for i in count:
        #sources[i]=(str(round(((count[i]/counts)*100)%101,1))+'%')
        sources[i]=round(count[i]/counts,3)
    return sources

#泄露时间分析函数,查询数据库返回所有泄露时间及所占比的字典
def analysis_xtime():
    wei=[]
    count={}
    results= db.person.find({},{"xtime":1,"_id":0})
    for result in results:
        if 'xtime' in result:
            xtime=result['xtime']
            if not xtime in wei:
                wei.append(xtime)
                count[xtime]=1
            else:
                count[xtime]+=1
    counts=0
    xtimes={}
    for i in count:
        counts+=count[i]
    for i in count:
        #xtimes[i]=(str(round(((count[i]/counts)*100)%101,1))+'%')
        xtimes[i]=round(count[i]/counts,3)
    return xtimes



@app.route('/analysis')
def analysis():
    emails=analysis_email()
    sources=analysis_source()
    xtimes=analysis_xtime()
    
    return render_template('analysis.html',emails=emails,sources=sources,\
                           xtimes=xtimes)



    
if __name__=='__main__':


    #file_insert('wxsuv.txt')
    #search('name','ak')
    app.run()
    #print(analysis_source())
    

    


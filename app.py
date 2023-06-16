import io
from operator import truediv
import os
import json
from PIL import Image, ImageDraw
import cv2
from numpy import asarray
import numpy as np
import torch
from flask import Flask, jsonify, url_for, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from crop import func
from retina_net import detect
from retina_net_multifiles import detectmult
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from user import User
from visualization import Visualization
import os
from io import BytesIO
import uuid

app = Flask(__name__)

RESULT_FOLDER = os.path.join('imagens')
app.config['RESULT_FOLDER'] = RESULT_FOLDER
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/flask_login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ktlan:1234@localhost/flask_login'
app.config['SECRET_KEY'] = 'secret'
# login_manager = LoginManager(app)
db = SQLAlchemy(app)

def find_model():
    for f  in os.listdir():
        if f.endswith(".pt"):
            return f
    print("please place a model file in this directory!")
    
model_name = find_model()
model =torch.hub.load("WongKinYiu/yolov7", 'custom',model_name)

model.eval()

def get_prediction(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    imgs = [img]  # batched list of images
# Inference
    results = model(imgs)  # includes NMS
    
    
    return results
@app.route('/image', methods=['POST'])
def image():
    jsdata = request.form['javascript_data']
    print(jsdata)
@app.route('/processing', methods=['POST'])
def predict():

    if request.method == 'POST':
        total_array = []
        crd = request.form['coordinates']
        if len(crd) == 0:
            return render_template('errorpage.html',error = 'SELECIONE AS COORDENADAS NA IMAGEM')

        file = request.files['img']
        cowNumber = request.form['cowNumber']
        if cowNumber == '':
            return render_template('errorpage.html',error = 'DIGITE O NÚMERO DE ANIMAIS NA IMAGEM')
        filename = request.files['img'].filename
        im = func(crd,filename)
        print("AAAAAAAA")
        print(type(im))
        # filename = secure_filename(file.filename)
        num_retina = detect(filename)
        img_bytes = file.read()
        num_yolo = 0
        with open(im, "rb") as image:
            print(type(image))
            f = image.read()
            print(type(f))
            results = get_prediction(f)            
            for i in results.pandas().xyxy[0]['class']:
                if i == 19:
                    num_yolo = num_yolo + 1      
            
            results.save(save_dir='static')
        closest = ''
        if num_retina == num_yolo:
            closest = "BOTH"
        else:
            total_array.append(int(num_retina))
            total_array.append(int(num_yolo))
            val=closest_value(total_array,int(cowNumber))
            if val == num_yolo:
                closest = "YOLO"
            else:
                closest = "RETINANET"
        # filename = 'aaaa.jpg'
        # file.save(os.path.join(app.config['RESULT_FOLDER'], filename))
        # img = os.path.join(app.config['RESULT_FOLDER'], filename)
        # return render_template('result.html',result_image = filename,model_name = model_name)
        return render_template('result.html',num_yolo = num_yolo, num_retina = num_retina, cowNumber = cowNumber, closest = closest)

    # return render_template('index.html')

@app.route('/processingmanyfiles', methods=['GET','POST'])
def processingmanyfiles():
    retina_array = []
    yolo_array = []
    array_numbers = []
    retina_number_array = []
    yolo_number_array = []
    num_yolo = 0
    if request.method == 'POST':
        d = request.files
        files = list(d.lists())
        cowNumber = request.form['cowNumber']
        if cowNumber == '':
            return render_template('errorpage.html',error = 'DIGITE O NÚMERO DE ANIMAIS NA IMAGEM')

        for img in files:
            for a in img[1:len(img)]:
                for b in a:
                    num_yolo = 0
                    img = Image.open(b).convert('RGB')
                    retina = detectmult(img)
                    print("RETINA ARRAY")
                    retina_number_array.append(retina[0])
                    retina_array.append(retina)

                    numpydata = asarray(img)
                    
                    cv2.imwrite("./static/" + b.filename, numpydata)

                    with open("./static/" + b.filename, "rb") as image:
                        f = image.read()
                        results = get_prediction(f)  
                        print(results.pandas().xyxy[0]['class'])
                        for i in results.pandas().xyxy[0]['class']:
                            if i == 19:
                                num_yolo = num_yolo + 1              
                        guid = uuid.uuid4()
                        results.save(save_dir='static')
                        os.rename('./static/image0.jpg','./static/' + str(guid) + ".jpg")     
                        yolo_number_array.append(num_yolo)                   
                        yolo_array.append((num_yolo,'./static/' + str(guid) + ".jpg"))
                        
        retina_total = 0
        yolo_total = 0
        retina_image_array = []
        total_array = []
        yolo_image_array = []
        for x in retina_array:
            retina_total = retina_total + x[0]
            retina_image_array.append(x[1])
        print(retina_total)

        print("YOLO ARRAY")
        print(yolo_array)

        for y in yolo_array:
            yolo_total = yolo_total + y[0]
            yolo_image_array.append(y[1])

        print(yolo_total)
        closest = ''
        total_array.append(int(retina_total))
        total_array.append(int(yolo_total))
        val=closest_value(total_array,int(cowNumber))
        if retina_total == yolo_total:
            closest = "BOTH"
        else:
            if val == yolo_total:
                closest = "YOLO"
            else:
                closest = "RETINANET"

        return render_template('resultmulti.html',retina_total = retina_total, yolo_total = yolo_total, retina_image_array = retina_image_array, yolo_image_array = yolo_image_array, closest = closest,
                               yolo_number_array = yolo_number_array, retina_number_array = retina_number_array)

        


                    

                    
                    



    return render_template('processingmanyfiles.html')

@app.route('/processing', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['GET'])
def homeindex():
    return redirect(url_for('login'))

@app.route('/listuser', methods=['GET'])
def listuser():
    query = f"SELECT * FROM users"
    with db.engine.connect() as conn:
        result = conn.execute(text(query))
        results_as_dict = result.mappings().all()
        print(results_as_dict)
    return render_template('listuser.html', dictionary = results_as_dict)

@app.route('/savevisualization/<info>',  methods=['POST'])
def savevisualization(info):
    print(info)
    iduser = session['id']
    print(iduser)
    guid = uuid.uuid4()
    if info == 'retina':
        os.rename(r'./static/r.jpg',r'./static/'+ str(guid) + '.jpg')
    else:
        os.rename(r'./static/image0.jpg',r'./static/'+ str(guid) + '.jpg')
        
    visualization = Visualization(link = str(guid) + '.jpg',users_id=iduser)
    db.session.add(visualization)
    db.session.commit()
    return redirect(url_for('listuser'), code=201)

@app.route('/seevisualization',  methods=['GET'])
def seevisualization():

    iduser = session['id']
    print(iduser)
    query = f"SELECT * FROM visualization WHERE users_id = {iduser}"
    with db.engine.connect() as conn:
        result = conn.execute(text(query))
        results_as_dict = result.mappings().all()
        print(results_as_dict)
    return render_template('seevisualization.html', dictionary = results_as_dict)

    
@app.route('/deleteuser/<id>',  methods=['GET','POST'])
def deleteuser(id):
    
    print("CAIU AQUIIIIIIIII")
    obj = db.session.query(User).filter(User.id_users==id).first()
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('listuser'))


@app.route('/edituser/<id>',  methods=['GET','POST'])
def edituser(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if request.form.get('isAdmin') != None:
            user_type = 'ADMIN'
        else:
            user_type = 'COMUM'
        user = db.session.query(User).filter(User.id_users==id).first()
        user.name = name
        user.email = email
        user.password = password
        user.user_type = user_type
        db.session.commit()
        return redirect(url_for('listuser'))

    query = f"SELECT * FROM users WHERE id_users = {id}"
    with db.engine.connect() as conn:
        result = conn.execute(text(query))
        results_as_dict = result.mappings().all()
        print(results_as_dict)
    return render_template('edituser.html', dictionary = results_as_dict)

@app.route('/register', methods=['GET','POST'])
def register(): 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        print(request.form)
        if request.form.get('isAdmin') != None:
            user_type = 'ADMIN'
        else:
            user_type = 'COMUM'
        if name and email and password:        
            print(name)
            user = User(name, email, password,user_type)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('listuser'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        query = f"SELECT * FROM users where email = '{email}'"
        if query:
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                results_as_dict = result.first()
                
                if results_as_dict:               
                    teste = results_as_dict._asdict()
                    session['user_type'] = teste['user_type']
                    session['id'] = teste['id_users']
    
                    return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session['user_type'] = ''
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

def closest_value(input_list, input_value):

  arr = np.asarray(input_list)

  i = (np.abs(arr - input_value)).argmin()

  return arr[i]

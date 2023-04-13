import io
from operator import truediv
import os
import json
from PIL import Image
import torch
from flask import Flask, jsonify, url_for, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from crop import func
from retina_net import detect
from flask_login import LoginManager, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from user import User

app = Flask(__name__)

RESULT_FOLDER = os.path.join('imagens')
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/flask_login'
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

        crd = request.form['coordinates']
        file = request.files['img']
        filename = request.files['img'].filename
        im = func(crd,filename)
        # filename = secure_filename(file.filename)
        num_retina = detect(filename)
        img_bytes = file.read()
        
        with open(im, "rb") as image:
            f = image.read()
            results = get_prediction(f)            

            num_yolo = len(results.pandas().xyxy[0]['class'])
            results.save(save_dir='static')
       
        # filename = 'aaaa.jpg'
        # file.save(os.path.join(app.config['RESULT_FOLDER'], filename))
        # img = os.path.join(app.config['RESULT_FOLDER'], filename)
        # return render_template('result.html',result_image = filename,model_name = model_name)
        return render_template('result.html',num_yolo = num_yolo, num_retina = num_retina)

    # return render_template('index.html')

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

@app.route('/deleteuser/<id>',  methods=['GET','POST'])
def deleteuser(id):
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
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("AAAAAAAAAA")
        query = f"SELECT * FROM users where email = '{email}'"
        print(query)
        if query:
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                results_as_dict = result.mappings().all()
                print(results_as_dict[0].user_type)
                if results_as_dict:               
                    session['name'] = results_as_dict[0].user_type
                    return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session['name'] = ''
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

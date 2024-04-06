from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import pymysql
from for_model import model_pred
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import sys
import os
import json
import matplotlib.pyplot as plt
import matplotlib

app = Flask(__name__)
app.secret_key = 'kmj'

db = pymysql.connect(host='127.0.0.1', user='root', password='1214', db='user')
cursor = db.cursor()

def line_graph(x,positive,negative,names):
    plt.rc('font',family='Malgun Gothic')
    plt.plot(x,positive,marker = 'o',label='positive')
    plt.plot(x,negative,marker = 'o',label='negative')
    plt.title('{}의 감정상태 변화'.format(names))
    plt.grid()
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig('static/img/line_plot.png')

# 사용자의 uersname과 password를 input으로 받는다.
# form action을 통해 login_check로 redirect한다.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email and password:
            sql = "select * from user_info where email = %s"
            cursor.execute(sql,email)
            result = cursor.fetchone()
        
            if email == result[2] and password == result[1]:
                return redirect(url_for('enter'))
            else:
                return render_template("login.html")
            
    return render_template('login.html')

@app.route('/enter')
def enter():
    return render_template('enter.html')

@app.route('/signup')
def signup():
    username2 = request.args.get('username2')
    password2 = request.args.get('pwd2')
    email2 = request.args.get('email2')

    if username2 and password2 and email2:
        sql = "INSERT INTO user_info (username, pwd, email) VALUES (%s, %s, %s)"
        cursor.execute(sql,(username2, password2, email2))

        data = cursor.fetchall()
    
        if not data:
            db.commit()
            return render_template("login.html")
    
    else:
        return render_template("signup.html", error_message="Please fill in all fields")
        
    return render_template('signup.html')

@app.route('/manage',methods=['GET','POST'])
def manage():   
    if request.method == 'POST':
        names = request.form['names']
        numbers = request.form['numbers']

        if names and numbers:
            sql = "SELECT distinct * FROM user.consult_info2;"
            cursor.execute(sql)
            result = cursor.fetchall()

            matplotlib.use('Agg')

            x = [str(i[2]) for i in result]
            positive = [float(i[-1]) for i in result]
            negative = [100-float(i[-1]) for i in result]

            line_graph(x,positive,negative,names)

    return render_template('manage.html')

@app.route('/consulting')
def consulting():
    name = request.args.get('student_name')
    num = request.args.get('student_num')
    day = request.args.get('consult_date')
    text = request.args.get('consultation')
    consult_type = request.args.get('subject')
    
    if name and num and day and text:
        with open('for_korean.json', 'r') as f:
            word_index = json.load(f)

        okt = Okt()
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
        tokenizer = Tokenizer()

        tokenizer.word_index = word_index

        loaded_model = load_model('best_model.h5')

        pred = model_pred(text)
        sql = "INSERT INTO consult_info2 (student_name, student_num, consult_day, consult_text,consult_type, positive) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql,(name, num, day, text, consult_type,pred))

        data = cursor.fetchall()
    
        if not data:
            db.commit()
            return redirect(url_for('enter'))
        
    return render_template('consulting.html')

@app.route('/')
def main():
    return render_template('index.html')  

    
# app.py 파일이 'python app.py'로 시작되었을 때 서버를 시작하겠다 라는 의미.
if __name__ == '__main__':
    app.run(debug=True)
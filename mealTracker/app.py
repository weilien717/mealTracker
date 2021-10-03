import csv
import bcrypt
import requests
import MySQLdb.cursors
import os
import re
from flask_mysqldb import MySQL
from flask import Flask, request,url_for, render_template, flash, redirect, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_mail import Mail, Message
from forms import ContactForm, LoginForm, RegisterForm, ReviewForm, forgotpwForm, changeMyPasswordForm, uploadForm, connectForm
from werkzeug.utils import secure_filename
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ALLO'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mealtrack'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='yukibobaforyou@gmail.com',
    MAIL_PASSWORD='yuki6321'
)
mail = Mail(app)





@app.route('/connect', methods=['GET', 'POST'])
def connect_with():
    form = connectForm()
    if request.method == 'POST' and 'email' in request.form:
        # Create variables for easy access
        friend_email = str(request.form['email'])
        my_email = session['email']
        myID = session['id']
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT account_id FROM user_login WHERE email = %s', [friend_email])
        
        account = cursor.fetchone()
        friend_id = 0
        if not account:
            print("acount dosn't exists!")
        else:
            friend_id = account['account_id']
            cursor.execute('insert into friend values(%s, %s)', (myID,friend_id))
            cursor.execute('insert into friend values(%s, %s)', (friend_id,myID))
        # Fetch one record and return result
        account = cursor.fetchone()
        mysql.connection.commit()
    return render_template('connect.html', form = form)


@app.route('/friend', methods=['GET', 'POST'])
def friend():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT friend2_id FROM friend WHERE friend1_id = %s;', [session['id']])
    account = cur.fetchone()
    if not account:
        print("acount dosn't exists!")
        return redirect(url_for('connect_with'))

    else:
        friend_id = account['friend2_id']
        cur.execute('SELECT username FROM user_login WHERE account_id = %s;', [friend_id])
        friend_acc = cur.fetchone()
        friend_name = friend_acc['username']

        cur.execute('SELECT food_post.food_name, food_post.food_pic, posted_by.date_posted, posted_by.time_posted FROM food_post, posted_by WHERE posted_by.food_id = food_post.food_id and posted_by.acc_id = ' + str(friend_id) + ' order by posted_by.time_posted desc;')
        result = cur.fetchall()
        foodNameList = []
        foodImageList = []
        datePostedList = []
        timePostedList = []
        for food in result:
            foodNameList.append(food.get('food_name'))
            foodImageList.append('/'+food.get('food_pic'))
            datePostedList.append(str(food.get('date_posted')))
            timePostedList.append(str(food.get('time_posted')))
        print("@@@@@@@" ,foodImageList)
    return render_template('friend.html', friend_name = friend_name, leng = len(foodNameList),foodNameList=foodNameList,foodImageList=foodImageList,datePostedList=datePostedList,timePostedList=timePostedList) 

@app.route('/uploadFood', methods=['GET', 'POST'])
def uploadFood():
    form = uploadForm()
    uploads_dir = os.path.join("static", 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['foodImage']
        message = request.form['message']
        current_datetime = datetime.now()
        currentDay = str(current_datetime.year) + '-'+ str(current_datetime.month) + '-' + str(current_datetime.day)
        currentTime = str(current_datetime.hour) + str(current_datetime.minute) + str(current_datetime.second)
        currentTime_sql = str(current_datetime.hour) + ':'+ str(current_datetime.minute) + ':' + str(current_datetime.second)
        user_id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) as c FROM food_post;')
        totalNumFood = cur.fetchone()
        id = totalNumFood.get('c')
        foodID = int(totalNumFood.get('c')) +1
        fileName = currentTime+'_'+str(foodID)+'_'+file.filename
        imageDir = 'static/uploads/'+fileName
        print(imageDir)
        file.save(os.path.join(uploads_dir, secure_filename(fileName)))
        print('saved')
        foodName = callAPI(imageDir)
        cur.execute('INSERT INTO food_post VALUES (%s, %s, %s, %s)', (foodID, foodName, imageDir,message))
        cur.execute('INSERT INTO posted_by VALUES (%s, %s, %s, %s)', (user_id, foodID, currentDay,currentTime_sql))
        mysql.connection.commit()
        msg = 'You have successfully uploaded!'
        return redirect(url_for('viewFood'))
    return render_template('uploadFood.html', form=form)

@app.route('/viewFood')
def viewFood():
    cur = mysql.connection.cursor()
    cur.execute('SELECT food_post.food_name, food_post.food_pic, posted_by.date_posted, posted_by.time_posted FROM food_post, posted_by WHERE posted_by.food_id = food_post.food_id and posted_by.acc_id = ' + str(session['id']) + ' order by posted_by.time_posted desc;')
    result = cur.fetchall()
    foodNameList = []
    foodImageList = []
    datePostedList = []
    timePostedList = []
    for food in result:
        foodNameList.append(food.get('food_name'))
        foodImageList.append('/'+food.get('food_pic'))
        datePostedList.append(str(food.get('date_posted')))
        timePostedList.append(str(food.get('time_posted')))
    print(foodImageList)
    return render_template('viewFood.html', leng = len(foodNameList),foodNameList=foodNameList,foodImageList=foodImageList,datePostedList=datePostedList,timePostedList=timePostedList) 

@app.route('/testAPI')
def getFoodName():
    img = 'tofu.jpg'
    resp = callAPI(img)
    return resp



@app.route('/')
def mainPage():
    return render_template("homePage.html", user=session['username'])


@app.route('/changemypassword', methods=['GET', 'POST'])
def changemypassword():
    form = changeMyPasswordForm()
    if form.validate_on_submit():
        setpw(form.email.data, form.password.data)
        return redirect(url_for('changemypassword'))
    return render_template('changemypassword.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_login WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
          # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['account_id']
            session['username'] = account['username']
            session['email'] = account['email']
            # Redirect to home page
            print('success')
            return redirect(url_for('mainPage'))
            #return render_template('homepage.html', form=form)

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            print(msg)
            return redirect(url_for('login'))

            #return render_template('login.html', form=form)

    return render_template('login.html', form=form)


def callAPI(img):
    api_user_token = '731c88f571b4c4de22a7ac00e134833c33912b9a'
    headers = {'Authorization': 'Bearer ' + api_user_token}
    # Food Type Detection
    url = 'https://api.logmeal.es/v2/recognition/dish'
    resp = requests.post(url, files={'image': open(img,'rb')}, headers=headers)
    print(resp.json())
    print(resp.json()["recognition_results"][0]["name"])  # display json response
    print(resp.json()["recognition_results"][0]["prob"])
    return resp.json()["recognition_results"][0]["name"]

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    username=''
    password=''
    email=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return redirect(url_for('register'))
        #return render_template('register.html', form = form, msg=msg)
    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user_login WHERE username = %s',(username,))
    account = cursor.fetchone()
    # If account exists show error and validation checks
    if account:
        msg = 'Account already exists!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        msg = 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', username):
        msg = 'Username must contain only characters and numbers!'
    elif not username or not password or not email:
        msg = 'Please fill out the form!'
    else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        cursor.execute('INSERT INTO user_login VALUES (NULL, %s, %s, %s)', (username, password, email,))
        mysql.connection.commit()
        msg = 'You have successfully registered!'
        return redirect(url_for('login'))
        #return render_template('login.html', form=form, msg=msg)
    return render_template('register.html', form=form)


@app.route('/reviews', methods=['GET', 'POST'])
def reviewsPage():
    reviews = []
    with open('data/reviews.txt') as f:
        index = 0
        for review in csv.reader(f):
            if not review:
                continue
            else:
                rating = review[0]
                name = review[1]
                message = ''
                for counter in range(2, len(review)):
                    message += review[counter] + ", "
                reviews.append([])
                reviews[index].append(rating)
                reviews[index].append(name)
                reviews[index].append(message)
                index += 1

    form = ReviewForm()

    if form.validate_on_submit():
        with open('data/reviews.txt', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([form.rate.data, form.name.data, form.message.data])
        return redirect(url_for('contact_response', name=form.name.data))
    return render_template('reviews.html', form=form, reviews=reviews)


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        with open('data/messages.csv', 'a' , newline='') as f:
            writer = csv.writer(f)
            writer.writerow([form.name.data, form.email.data,
                             form.message.data])
        return redirect(url_for('contact_response', name=form.name.data))
    return render_template('contact.html', form=form)


@app.route('/contact_response/<name>')
def contact_response(name):
    return render_template('contact_response.html', name=name)


@app.route('/forgotpw', methods=['GET', 'POST'])
def forgotpw():
    form = forgotpwForm()
    userEmail = form.email.data
    if form.validate_on_submit():
        user = find_userFromEmail(userEmail)
        if user:
            try:
                msg = Message("Your temporarily password",
                              sender="yukibobaforyou@gmail.com",
                              recipients=[form.email.data])
                msg.body = "Hello, " + user.id + ", 'abc123456' will be your temporarily password"
                mail.send(msg)
                setpw(userEmail, 'abc123456')
                return redirect(url_for('login'))
            except Exception as e:
                return (str(e))
        else:
            flash('This email is not registered')
    return render_template('forgotpw.html', form=form)


def find_userFromEmail(email):
    with open('data/accounts.csv') as f:
        for user in csv.reader(f):
            if not user:
                continue
            if email == user[1]:
                return User(*user)
    return None


def setpw(email, pw):
    user = find_userFromEmail(email)
    if user:
        name = user.id
        email = user.email
        phone = user.phone
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(pw.encode(), salt)

        updatedlist = []
        # rewrite everything except that line
        with open('data/accounts.csv', 'r') as f:
            for line in csv.reader(f):
                if not line:
                    continue
                if name != line[0] and email != line[1]:
                    updatedlist.append(line)

        with open('data/accounts.csv', "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(updatedlist)

        with open('data/accounts.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name, email, phone, password.decode()])
            flash('Your password has been reset!')
    else:
        flash("This username is not defined!")
    return redirect('/login')


@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')


@app.route('/non_protected')
def non_protected():
    return render_template('non_protected.html')


@app.route('/drinks')
def drinkPage():
    return render_template("DrinkPage.html")


@app.route('/locations')
def locationPage():
    return render_template("Location.html")


class User(UserMixin):
    def __init__(self, username, email, phone, password=None):
        self.id = username
        self.email = email
        self.phone = phone
        self.password = password



@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session['loggedin'] = False
   session['username']='none'
   # Redirect to login page
   return render_template("homePage.html")
   #return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()

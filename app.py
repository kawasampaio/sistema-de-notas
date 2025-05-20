from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

   # Sample username and password for demonstration
VALID_USERNAME = "teacher"
VALID_PASSWORD = "password123"

@app.route('/')
def login():
       return render_template('index.html')

@app.route('/login', methods=['POST'])
def do_login():
       username = request.form['username']
       password = request.form['password']
       
       if username == VALID_USERNAME and password == VALID_PASSWORD:
           return redirect(url_for('success'))
       return "Invalid credentials, please try again."

@app.route('/success')
def success():
       return "Logged in successfully!"

if __name__ == '__main__':
       app.run(debug=True)
   
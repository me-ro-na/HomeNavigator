from flask import Flask, render_template, redirect, url_for
from services.auth_service import auth_service
from services.search_service import search_service
from services.chat_service import chat_service
from services.fetch_service import fetch_service

app = Flask(__name__)

app.register_blueprint(auth_service)
app.register_blueprint(search_service)
app.register_blueprint(chat_service)  # 추가된 부분
app.register_blueprint(fetch_service)  # 추가된 부분


@app.route('/')
def dashboard():
    return redirect(url_for('chatbot'))
    # return render_template('dashboard.html', search_history=search_history)

@app.route('/fetch')
def fetch():
    return render_template('fetchTest.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/financial')
def financial():
    return render_template('financial.html')

@app.route('/property')
def property():
    return render_template('property.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('logout_success'))

@app.route('/logout-success')
def logout_success():
    return render_template('logout_success.html')

@app.route('/logout-failure')
def logout_failure():
    return render_template('logout_failure.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "development_secret_key"

@app.route('/')
def index():
    return render_template('simple.html', title="Perito IA - Dashboard")

if __name__ == '__main__':
    app.run(debug=True, port=5050)

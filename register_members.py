from flask import Flask, render_template,request

app = Flask(__name__)
member_name = 'student'
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/', methods=['POST'])
def post():
    global member_name
    member_name = request.form['name']
    return 'Success'
@app.route('/member')
def register():
    return member_name
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8000)
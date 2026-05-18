from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/center')
def center():
    return render_template('center.html')

@app.route('/discovery')
def discovery():
    return render_template('discovery.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/merchant')
def merchant():
    return render_template('merchant.html')

@app.route('/support')
def support():
    return render_template('support.html')






if __name__ == '__main__':
    app.run(debug=True)








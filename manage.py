from flask import Flask
from flask import render_template

from api import add_api


app = Flask(__name__)
add_api(app)


@app.route('/')
@app.route('/<photo_id>')
def home(photo_id=None):
    if not photo_id:
        photo_id = ""
    return render_template(
        'home.html',
        photo_id=photo_id,
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

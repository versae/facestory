from flask import Flask
from flask import render_template

from api import add_api
from utils import get_file_remote


app = Flask(__name__)
add_api(app)


@app.route('/')
@app.route('/<photo_id>')
def home(photo_id=None):
    if not photo_id:
        photo_id = ""
    else:
        photo_filename = "{}.png".format(photo_id)
        photo_url = get_file_remote(photo_filename)
    return render_template(
        'home.html',
        photo_id=photo_id,
        photo_url=photo_url,
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

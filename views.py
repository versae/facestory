from flask import Flask
from flask import render_template

from db import get_user_faces
from api import add_api


app = Flask(__name__)
add_api(app)


@app.route('/')
@app.route('/<photo_id>')
def home(photo_id=None):
    photo_url = None
    if not photo_id:
        photo_id = ""
    else:
        user_faces = get_user_faces(photo_id)
        if user_faces:
            photo_url = user_faces[0]['face_url']
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

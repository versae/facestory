from flask import Flask
from flask import render_template
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)


class FaceSimilarity(restful.Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(FaceSimilarity, '/api/')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

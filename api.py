from flask.ext import restful


class FaceSimilarity(restful.Resource):
    def get(self):
        return {'hello': 'world'}


def add_api(app):
    api = restful.Api(app)
    api.add_resource(FaceSimilarity, '/api/')

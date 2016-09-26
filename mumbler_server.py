import sys
from flask import Flask
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from gevent.wsgi import WSGIServer

app = Flask(__name__)
api = Api(app)


class GetWord(Resource):

    def get(self, first_word):
        conn = eng.connect()
        query = conn.execute('SELECT * FROM bigrams_counts_id WHERE FirstWord=:first', {"first": first_word.lower()})
        data = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return data


api.add_resource(GetWord, '/<string:first_word>')

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'enter bind to IP and database file path'
    else:
        ip = sys.argv[1]
        db_name = sys.argv[2]
        db_path = ''.join([r'sqlite:///', db_name])

        eng = create_engine(db_path)

        http_server = WSGIServer((ip, 5000), app)
        http_server.serve_forever()
        # app.run(ip)


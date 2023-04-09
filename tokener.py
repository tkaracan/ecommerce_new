from flask import Flask,jsonify,request,make_response
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = 'tugrul'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(args)
        token = request.args.get('token')

        if not token:
            print(token)
            return jsonify({'message': 'Error, NO TOKEN'}),403


        try:
            #bu ne anlamadim hic, data kullanilmiyor bile

            data = jwt.decode(token, app.config['SECRET_KEY'])

        except:
            print("invalid: ", token)
            return jsonify({'message': 'Token is invalid'}),403

        return f(*args,**kwargs)

    return decorated

@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'public, unprotected'})



@app.route('/protected')
@token_required
def protected():

    return jsonify({'message': 'token worked, private'})

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password == 'baba':
        token = jwt.encode({'user': auth.username, 'exp' : datetime.datetime.utcnow()+datetime.timedelta(minutes=1)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Olmadi anam', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required"'})

if __name__ == '__main__':
    app.run(debug=True)
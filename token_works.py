from flask import Flask, request, jsonify

import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbtrl4.sqlite3'
app.config['SECRET_KEY'] = 'A'  # Replace with your own secret key

# Fake user database for testing
users = {
    'tugrul': '123',
    'User': 'pass'
}



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    if username not in users or users[username] != password:
        return jsonify({'message': 'Wrong Password or Username'}), 401

    token = jwt.encode({'user': username}, app.config['SECRET_KEY'], algorithm='HS256')
    print("THIS IS TOKEN: ", token)
    return jsonify({'token': token})


@app.route('/protected')
def protected():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'No token provided'}), 401

    try:
        print("trying")
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        print("here:")
        print(token)
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('user')
    if not username or username not in users:
        return jsonify({'message': 'Invalid user'}), 401

    return jsonify({'message': 'Success!'})


if __name__ == '__main__':
    app.run(debug=True)

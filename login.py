from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Define a dictionary to store the valid tokens
valid_tokens = {}


# Define a route to generate a new token
@app.route('/api/token', methods=['POST'])
def generate_token():
    # Get the username and password from the request data
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if the credentials are valid
    if username == 'myusername' and password == 'mypassword':
        # Generate a new token
        token = secrets.token_hex(32)

        # Store the token in the dictionary
        valid_tokens[token] = username

        # Return the token as a JSON response
        return jsonify({'token': token}), 200
    else:
        # Return an error message as a JSON response
        return jsonify({'error': 'Invalid username or password'}), 401


# Define a route to access the restricted page
@app.route('/api/restricted', methods=['GET'])
def restricted_page():
    # Get the token from the request headers
    token = request.headers.get('Authorization')

    # Check if the token is valid
    if token in valid_tokens:
        # Return the restricted page as a JSON response
        return jsonify({'message': 'This is a restricted page'}), 200
    else:
        # Return an error message as a JSON response
        return jsonify({'error': 'Invalid token'}), 401


# Define a handler for 404 errors
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
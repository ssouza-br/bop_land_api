from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to your secret key

# Route to set session variables
@app.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    username = data.get('username')
    user_id = data.get('user_id')
    
    if username and user_id:
        session['username'] = username
        session['user_id'] = user_id
        return jsonify(message='Session variables set'), 200
    else:
        return jsonify(error='Username and user_id are required'), 400

# Route to get session variables
@app.route('/get_session', methods=['GET'])
def get_session():
    if 'username' in session and 'user_id' in session:
        return jsonify(username=session['username'], user_id=session['user_id']), 200
    else:
        return jsonify(error='Session variables not set'), 400

# Main method to run the application
if __name__ == '__main__':
    app.run(debug=True)
import instaloader
from flask import Flask, jsonify, request

app = Flask(__name__)

L = instaloader.Instaloader()

@app.route('/profile_picture', methods=['GET'])
def get_profile_picture():
    username = request.args.get('username')
    
    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return jsonify({
            "username": username,
            "profile_pic_url": profile.profile_pic_url
        })
    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({"error": f"Profile '{username}' not found"}), 404
    except instaloader.exceptions.ConnectionException:
        return jsonify({"error": "Connection error. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_profile_picture(username):
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find("meta", property="og:image")
        if meta_tag:
            return meta_tag['content']
    return None

@app.route('/profile_picture', methods=['GET'])
def profile_picture():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username parameter is required"}), 400
    
    profile_pic_url = get_profile_picture(username)
    if profile_pic_url:
        return jsonify({"profile_picture_url": profile_pic_url})
    else:
        return jsonify({"error": "Failed to fetch profile picture"}), 404

if __name__ == '__main__':
    app.run(debug=True)

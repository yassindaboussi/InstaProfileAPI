from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_profile_picture(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        app.logger.info(f"Status Code: {response.status_code}")
        app.logger.info(f"Final URL: {response.url}")
        
        # Check if redirected to login page
        if 'accounts/login' in response.url:
            app.logger.error("Redirected to Instagram login page.")
            return None
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag:
                return meta_tag['content']
        else:
            app.logger.error(f"Non-200 Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {str(e)}")
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
        return jsonify({"error": "Failed to fetch profile picture. The username might be invalid or the request was blocked by Instagram."}), 404

if __name__ == '__main__':
    app.run(debug=True)

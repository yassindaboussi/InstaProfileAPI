from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_profile_picture(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        app.logger.info(f"Status Code: {response.status_code}")
        app.logger.info(f"Final URL: {response.url}")

        # Check if redirected to a login page
        if 'accounts/login' in response.url:
            app.logger.error("Blocked: Redirected to Instagram login page.")
            return None

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag:
                return meta_tag['content']
        else:
            app.logger.error(f"Failed with status code: {response.status_code}")
    except Exception as e:
        app.logger.error(f"Request failed: {str(e)}")
    return None

@app.route('/profile_picture', methods=['GET'])
def profile_picture():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    profile_pic_url = get_profile_picture(username)
    if profile_pic_url:
        return jsonify({"profile_picture_url": profile_pic_url})
    else:
        return jsonify({"error": "Failed to fetch profile picture. Instagram is blocking the request."}), 404

if __name__ == '__main__':
    app.run(debug=True)

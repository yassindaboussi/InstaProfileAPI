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
        final_url = response.url
        status_code = response.status_code
        html_content = response.text  # Capture the full HTML

        app.logger.info(f"Status Code: {status_code}")
        app.logger.info(f"Final URL: {final_url}")

        # Check for login redirect
        if 'accounts/login' in final_url:
            app.logger.error("Blocked: Redirected to Instagram login page.")
            return None, html_content  # Return HTML for debugging

        if status_code == 200:
            soup = BeautifulSoup(html_content, 'html.parser')
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag:
                return meta_tag['content'], None  # Success case
            else:
                app.logger.error("og:image meta tag not found.")
                return None, html_content  # Return HTML to debug missing tag
        else:
            app.logger.error(f"Non-200 Status Code: {status_code}")
            return None, html_content  # Return HTML for non-200 errors

    except Exception as e:
        app.logger.error(f"Request failed: {str(e)}")
        return None, str(e)  # Return exception message

@app.route('/profile_picture', methods=['GET'])
def profile_picture():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    profile_pic_url, html_or_error = get_profile_picture(username)
    if profile_pic_url:
        return jsonify({"profile_picture_url": profile_pic_url})
    else:
        # Truncate HTML to avoid huge responses
        truncated_html = html_or_error[:1000] if isinstance(html_or_error, str) else None
        return jsonify({
            "error": "Failed to fetch profile picture. Instagram is blocking the request.",
            "html_snippet": truncated_html  # First 1000 characters of HTML/error
        }), 404

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import os
import json
import requests
import time
from generator import generate_app
from deployer import deploy_to_github

app = Flask(__name__)

# Your secret from the form
MY_SECRET = os.environ.get('MY_SECRET', 'your-secret-here')

@app.route('/api/deploy', methods=['POST'])
def deploy():
    try:
        data = request.get_json()
        
        # Verify secret
        if data.get('secret') != MY_SECRET:
            return jsonify({"error": "Invalid secret"}), 403
        
        # Extract request data
        email = data['email']
        task = data['task']
        round_num = data['round']
        nonce = data['nonce']
        brief = data['brief']
        checks = data['checks']
        evaluation_url = data['evaluation_url']
        attachments = data.get('attachments', [])
        
        # Generate the app using Gemini
        print(f"Generating app for task: {task}, round: {round_num}")
        app_files = generate_app(brief, checks, attachments, task, round_num)
        
        # Deploy to GitHub
        print(f"Deploying to GitHub...")
        repo_url, commit_sha, pages_url = deploy_to_github(
            task, app_files, email, round_num
        )
        
        # Notify evaluation URL
        print(f"Notifying evaluation URL...")
        response_data = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }
        
        # Try to notify with retries
        notify_success = notify_evaluation(evaluation_url, response_data)
        
        if notify_success:
            return jsonify({
                "status": "success",
                "repo_url": repo_url,
                "pages_url": pages_url
            }), 200
        else:
            return jsonify({
                "status": "deployed_but_notification_failed",
                "repo_url": repo_url,
                "pages_url": pages_url
            }), 200
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def notify_evaluation(url, data, max_retries=5):
    """Notify evaluation URL with exponential backoff"""
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)
            if resp.status_code == 200:
                print(f"Notification successful on attempt {attempt + 1}")
                return True
            else:
                print(f"Notification failed: {resp.status_code}, {resp.text}")
        except Exception as e:
            print(f"Notification error on attempt {attempt + 1}: {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1, 2, 4, 8 seconds
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
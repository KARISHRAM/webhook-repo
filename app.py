from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import datetime

app = Flask(__name__)

client = MongoClient('mongodb+srv://karishramsanjai:edy2tCHQvtxHxIaa@cluster0.wjjap.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['db']
collection = db['actions']

@app.route("/")
def home():
    return "Webhook Receiver is running!"

@app.route("/webhook", methods=["POST"])
def github_webhook():
    if request.headers.get('X-GitHub-Event') == 'push':
        data = request.json

        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        requestid = data['head_commit']['id']

        action_doc = {
            'requestid': requestid,
            'author': author,
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': to_branch,
            'timestamp': timestamp
        }

        collection.insert_one(action_doc)

        return jsonify({'msg': 'Push event received successfully'}), 200
    else:
        return jsonify({'msg': 'Event type not supported'}), 400

@app.route("/latest")
def latest_data():
    actions = list(collection.find().sort('timestamp', -1).limit(10))
    results = []
    for action in actions:
        if action['action'] == 'PUSH':
            results.append({
                'text': f"{action['author']} pushed to {action['to_branch']} on {action['timestamp']}",
                'timestamp': action['timestamp']
            })
        elif action['action'] == 'PULL_REQUEST':
            results.append({
                'text': f"{action['author']} submitted a pull request from {action['from_branch']} to {action['to_branch']} on {action['timestamp']}",
                'timestamp': action['timestamp']
            })
        elif action['action'] == 'MERGE':
            results.append({
                'text': f"{action['author']} merged branch {action['from_branch']} to {action['to_branch']} on {action['timestamp']}",
                'timestamp': action['timestamp']
            })
    return jsonify(results)

@app.route("/data")
def display_data():
    return render_template('data.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

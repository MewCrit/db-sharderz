from flask import Flask, jsonify, request
from sharder.sharder import execute, execute_query_on_all_shards, insert_data
import uuid

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def add_click_data():
     results = execute_query_on_all_shards("SELECT * FROM Users")
     return jsonify([str(result) for result in results]), 200


@app.route('/api/users', methods=['POST'])
def insert():
     data = request.json
     guid = uuid.uuid4()

     name = data['name']
     last_name = data['lastName']
     position = data['position']
     department = data['department']

     insert = {
        'UserID' : guid,
        'Name': name,
        'LastName': last_name,
        'Position': position,
        'Department': department
     }

     insert_data(guid, 'Users', insert)

     return jsonify(insert_data), 201



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port='9002')
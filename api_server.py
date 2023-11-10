from flask import Flask, request, jsonify
import requests
from requests.exceptions import Timeout
import firebase_config
import pyrebase

app = Flask(__name__)

NaiveBayesServer = 'http://localhost:8081/NaiveBayesPredict'
ClusterServer = 'http://localhost:8082/'

firebase = pyrebase.initialize_app(firebase_config.config)
auth = firebase.auth()

@app.route("/", methods=['GET'])
def root_server():
    return "Server Alive"

@app.route('/normalflow', methods=['POST'])
def normal_flow():
    id_token = request.headers.get('Authorization')
    
    if id_token:
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            data = request.get_json()
            
            if data:
                try:
                    #Enviar datos a el servidor Flask de procesamiento de Emails
                    response1 = requests.post(NaiveBayesServer, json=data, timeout=5)
                except Timeout:
                    return jsonify({"error": "The request to NaiveBayes Server timed out"}), 408
                
                #Si la respuesta del servidor es correcta y la prediccion es 1 entonces pasar al clusterizado
                if response1.status_code == 200 and response1.text == "1.0":
                    try:
                        response2 = requests.post(ClusterServer, json=request.get_json(), timeout=5)
                    except Timeout:
                        return jsonify({"error": "The request to Cluster Server timed out"}), 408
                    
                    return jsonify(response2.json()), response2.status_code
                
                #Si la predicción es 0 entonces retornar el status
                else:
                    return jsonify(response1.json()), response1.status_code    
            else:
                return jsonify({"error": "Bad Request"}), 400
        except:
            return jsonify({"error": "Invalid ID token"}), 401
    else:
        return jsonify({"error": "Missing ID token"}), 401

if __name__ == '__main__':
    #Run Flask app
    app.run(port=8080, debug=True)
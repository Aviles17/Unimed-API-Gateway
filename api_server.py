from flask import Flask, request, jsonify
import requests
from requests.exceptions import Timeout
import json



app = Flask(__name__)

NaiveBayesServer = 'http://localhost:8081/NaiveBayesPredict'
ClusterServer = 'http://localhost:8082/predecir'


@app.route("/", methods=['GET'])
def root_server():
    return "Server Alive"

@app.route('/normalflow', methods=['POST'])
def normal_flow():
    
    data = request.get_json()
    data = normalice_json_request(data)
    print(data)
    
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
            
            response2_json = json.loads(response2.text)
            label = response2_json['etiqueta_predicha']
            return jsonify({"nb_predict": response1.text, "label": label}), response2.status_code
        
        #Si la predicción es 0 entonces retornar el status
        else:
            return jsonify({"nb_predict": response1.text}), response1.status_code    
    else:
        return jsonify({"error": "Bad Request"}), 400
   
#Funcion auxiliar para normalizar inputs 
def normalice_json_request(request: dict):
    ret_dict = {}
    base_64_url = request["body"][0]['attachmentUrl']
    str_body = request["body"][0]['body']
    ret_dict["url"] = base_64_url
    ret_dict["body"] = str_body
    ret_dict["CC"] = "1000697372"
    
    return ret_dict     
        

if __name__ == '__main__':
    app.run(port=2023, debug=True)
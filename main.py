from datetime import date, datetime
from bson.objectid import ObjectId
from flask import Flask, json, request, jsonify, Response 
from flask_pymongo import PyMongo
from flask import render_template
from pymongo import mongo_client
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from bson import json_util
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import requests
import urllib


from werkzeug.wrappers import response

app = Flask (__name__)


app.config["MONGO_URI"] = "mongodb+srv://CarHubAdmin:1234@carhub.n2ouf.mongodb.net/CarHubDB?retryWrites=true&w=majority"

API_KEY_MAPS = "AIzaSyDznNAUPqKZhq9Czvpzq3Nl8ppJOd0L_XI"
API_KEY_TIEMPO = "be0d42dee8a7dc753453bdaa8a20f26a"
app.config['GOOGLEMAPS_KEY'] = API_KEY_MAPS



mongo = PyMongo(app)
maps = GoogleMaps(app)

Usuarios = mongo.db.Usuarios
Trayectos = mongo.db.Trayectos
Conversaciones = mongo.db.Conversaciones

#------------------------------------------------------------
#  _    _  _____ _    _         _____  _____ ____   _____ 
# | |  | |/ ____| |  | |  /\   |  __ \|_   _/ __ \ / ____|
# | |  | | (___ | |  | | /  \  | |__) | | || |  | | (___  
# | |  | |\___ \| |  | |/ /\ \ |  _  /  | || |  | |\___ \ 
# | |__| |____) | |__| / ____ \| | \ \ _| || |__| |____) |
#  \____/|_____/ \____/_/    \_\_|  \_\_____\____/|_____/      
#                                                    
#------------------------------------------------------------

#CRUD

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    username = request.json['username']
    nombre = request.json['nombre']
    apellidos = request.json['apellidos']
    coche = request.json['coche']
    correo = request.json['correo']
    contrasena = request.json['contrasena']
    dni = request.json['dni']
    fechanacimiento = request.json['fechanacimiento']
    telefono = request.json['telefono']
    paypal = request.json['paypal']
    foto = request.json['foto']

    if nombre and apellidos and correo and contrasena and dni and fechanacimiento and telefono:
        hashed_contrasena = generate_password_hash(contrasena)
        id = Usuarios.insert(
            {'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': hashed_contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}
        )
        resp = jsonify("Usuario añadido")
        resp.status_code = 200
        return resp

@app.route('/mostrar_usuarios', methods=['GET'])
def mostrar_usuarios():
    usuarios = Usuarios.find()
    resp = json_util.dumps(usuarios)
    return Response(resp, mimetype='application/json')

@app.route('/borrar_usuario/<id>', methods=['GET'])
def borrar_usuario(id):
    usuario = Usuarios.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Usuario eliminado")
    return resp

@app.route('/actualizar_usuario/<id>' , methods = ['POST'])
def actualizar_usuario(id):
    username = request.json['username']
    nombre = request.json['nombre']
    apellidos = request.json['apellidos']
    coche = request.json['coche']
    correo = request.json['correo']
    contrasena = request.json['contrasena']
    dni = request.json['dni']
    fechanacimiento = request.json['fechanacimiento']
    telefono = request.json['telefono']
    paypal = request.json['paypal']
    foto = request.json['foto']
    hashed_contrasena = generate_password_hash(contrasena)

    Usuarios.update_one({'_id': ObjectId(id)},{'$set':{'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': hashed_contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}})
    resp = jsonify("Usuario actualizado")
    return resp


#OP CONSULTA O BUSQ PARAMETRIZADA


@app.route('/buscar_usuario_id/<id>', methods=['GET'])
def buscar_usuario_id(id):
    usuario = Usuarios.find_one({'_id': ObjectId(id)})
    resp = json_util.dumps(usuario)
    return Response(resp, mimetype='application/json')

@app.route('/buscar_usuario_username/<filtro>', methods=['GET'])
def buscar_usuario_username(filtro):
    usuarios = Usuarios.find({'username': {'$regex':filtro}})
    resp = json_util.dumps(usuarios)
    return Response(resp, mimetype='application/json')

@app.route('/buscar_usuario_nombre_apellidos/<filtro>', methods=['GET'])
def buscar_usuario_nombre_apellidos(filtro):
    if ' ' in filtro:
        palabras = filtro.split(' ', 1)
        usuarios = Usuarios.find({"$or":[{'nombre':{'$regex':palabras[0]}}, {'apellidos':{'$regex':palabras[1]}}]}) # Usuarios.find({'apellidos':{'$regex':filtro}})
        resp = json_util.dumps(usuarios)
        return Response(resp, mimetype='application/json')
    else:   
        usuarios = Usuarios.find({"$or":[{'nombre':{'$regex':filtro}}, {'apellidos':{'$regex':filtro}}]}) # Usuarios.find({'apellidos':{'$regex':filtro}})
        resp = json_util.dumps(usuarios)
        return Response(resp, mimetype='application/json')

#-------------------------------------------------------------------------
#   _____                                         _                       
#  / ____|                                       (_)                      
# | |     ___  _ ____   _____ _ __ ___  __ _  ___ _  ___  _ __   ___  ___ 
# | |    / _ \| '_ \ \ / / _ \ '__/ __|/ _` |/ __| |/ _ \| '_ \ / _ \/ __|
# | |___| (_) | | | \ V /  __/ |  \__ \ (_| | (__| | (_) | | | |  __/\__ \
#  \_____\___/|_| |_|\_/ \___|_|  |___/\__,_|\___|_|\___/|_| |_|\___||___/
#                                                                         
#-------------------------------------------------------------------------

@app.route('/conversaciones/<id1>/<id2>', methods=['POST'])
def crear_conversacion(id1, id2):
    listMensajes = []
    if id1 and id2:
        conversacion = Conversaciones.find_one({'$or': [
            {'user1': ObjectId(id1), 'user2': ObjectId(id2)},
            {'user2': ObjectId(id2), 'user2': ObjectId(id1)}
        ]})
        if conversacion == None :
            id = Conversaciones.insert(
                               {'user1': ObjectId(id1), 'user2': ObjectId(id2), 'listMensajes': listMensajes}
                               )
            response = jsonify({
                'mensaje': 'Conversación creada satisfactoriamente'
            })
        else:
            response = jsonify({
                'mensaje': 'Ya existía una conversación creada.'
            })
    else:
        return not_found()
    return response

@app.route('/conversaciones', methods=['GET'])
def mostrar_conversaciones():
    conversaciones = Conversaciones.find()
    response = json_util.dumps(conversaciones)
    return Response(response, mimetype="application/json")

@app.route('/conversaciones/<id>', methods=['GET'])
def buscar_conversacion_id(id):
    conversacion = Conversaciones.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(conversacion)
    return response

@app.route('/conversaciones/<id>', methods=['DELETE'])
def borrar_conversacion(id):
    if Conversaciones.count_documents({'_id': ObjectId(id)}) == 1:
        Conversaciones.delete_one({'_id': ObjectId(id)})
        response = jsonify({
            'mensaje': 'La conversacion con id: ' + id + ' fue eliminada satisfactoriamente.'
        })
    else:
        return not_found()
    return response
    
@app.route('/conversaciones/<idc>/<idu>', methods=['PATCH'])
def enviar_mensaje(idc, idu):
    contenido = request.json['contenido']
    if contenido:
        Conversaciones.update_one({'_id': ObjectId(idc)}, {'$push': {
            'listMensajes': {
                'idUser': ObjectId(idu),
                'contenido': contenido,
                'fecha': datetime.utcnow()
            }
        }})
        response = {
            'mensaje': 'El mensaje ha sido enviado satisfactoriamente' 
        }
    else:
        return not_found()
    
    return response

@app.route('/conversaciones/user/<id>')
def buscar_conversaciones_usuario(id):
    conversaciones = Conversaciones.find({'$or': [
        {'user1': ObjectId(id)},
        {'user2': ObjectId(id)}
    ]})
    response = json_util.dumps(conversaciones)
    return Response(response, mimetype="application/json")
                                                                        
#------------------------------------------------------------------
#  _______ _____        __     ________ _____ _______ ____   _____ 
# |__   __|  __ \     /\\ \   / /  ____/ ____|__   __/ __ \ / ____|
#    | |  | |__) |   /  \\ \_/ /| |__ | |       | | | |  | | (___  
#    | |  |  _  /   / /\ \\   / |  __|| |       | | | |  | |\___ \ 
#    | |  | | \ \  / ____ \| |  | |___| |____   | | | |__| |____) |
#    |_|  |_|  \_\/_/    \_\_|  |______\_____|  |_|  \____/|_____/ 
#
#------------------------------------------------------------------                                                                  
                                                                 
#CRUD

@app.route('/crear_trayecto/<idconductor>', methods=['POST'])
def crear_trayecto(idconductor):
    conductor = ObjectId(idconductor)
    origen = request.json['origen']
    destino = request.json['destino']
    horasalida = request.json['horasalida']
    precio = request.json['precio']
    numeropasajeros = request.json['numeropasajeros']
    finalizado = 0
    pasajeros = []

    if origen and destino and horasalida and precio and numeropasajeros :
        id = Trayectos.insert(
            {'conductor':conductor, 'origen': origen, 'destino': destino, 'horasalida': horasalida, 'precio': precio, 'numeropasajeros': numeropasajeros, 'finalizado':finalizado, 'pasajeros' : pasajeros}
        )
        resp = jsonify("Trayecto añadido")
        resp.status_code = 200
        return resp


@app.route('/mostrar_trayectos', methods=['GET'])
def mostrar_trayectos():
    trayectos = Trayectos.find()
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/borrar_trayecto/<id>', methods=['GET'])
def borrar_trayecto(id):
    trayectos = Trayectos.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Trayecto eliminado")
    return resp

@app.route('/actualizar_trayecto/<id>' , methods = ['POST'])
def actualizar_trayecto(id):
    origen = request.json['origen']
    destino = request.json['destino']
    horasalida = request.json['horasalida']
    precio = request.json['precio']
    numeropasajeros = request.json['numeropasajeros']
    finalizado = request.json['finalizado']

    Trayectos.update_one({'_id': ObjectId(id)},{'$set':{'origen': origen, 'destino': destino, 'horasalida': horasalida, 'precio': precio, 'numeropasajeros': numeropasajeros, 'finalizado': finalizado}})
    resp = jsonify("Trayecto actualizado")
    return resp


#OP CONSULTA O BUSQ PARAMETRIZADA


@app.route('/buscar_trayecto_id/<id>', methods=['GET'])
def buscar_trayecto_id(id):
    trayecto = Trayectos.find_one({'_id': ObjectId(id)})
    resp = json_util.dumps(trayecto)
    return Response(resp, mimetype='application/json')

@app.route('/buscar_trayecto_origen/<origen>', methods = ['GET'])
def buscar_trayecto_origen(origen):
    trayectos = Trayectos.find({'origen': origen})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/buscar_trayecto_destino/<destino>', methods = ['GET'])
def buscar_trayecto_destino(destino):
    trayectos = Trayectos.find({'destino': destino})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/buscar_trayecto_origendestino/<origen>/<destino>', methods = ['GET'])
def buscar_trayecto_origendestino(origen, destino):
    trayectos = Trayectos.find({'origen': origen, 'destino': destino})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/anadir_pasajero/<idtrayecto>/<idpasajero>', methods = ['POST'])
def anadir_pasajero(idtrayecto, idpasajero):
    trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
    numpasajeros = trayecto['numeropasajeros']
    conductor = trayecto['conductor']
    pasajeros = trayecto['pasajeros']
    finalizado = trayecto['finalizado']
    if numpasajeros > 0 and ObjectId(idpasajero) not in pasajeros and finalizado == 0 and conductor != ObjectId(conductor): #la condicion de numpasajeros > 0 puede dar infinitos pasajeros para un viaje
        pasajeros.append(ObjectId(idpasajero))
        Trayectos.update_one({'_id': ObjectId(idtrayecto)},{'$set':{'pasajeros' : pasajeros, 'numeropasajeros' : numpasajeros-1}})
        resp = jsonify("Pasajero añadido")
    else:
        resp = jsonify("No se puede añadir pasajero")
    return resp

#------------------------------------------------------------------
#           _____ _____      __  __          _____   _____ 
#     /\   |  __ \_   _|    |  \/  |   /\   |  __ \ / ____|
#    /  \  | |__) || |      | \  / |  /  \  | |__) | (___  
#   / /\ \ |  ___/ | |      | |\/| | / /\ \ |  ___/ \___ \ 
#  / ____ \| |    _| |_     | |  | |/ ____ \| |     ____) |
# /_/    \_\_|   |_____|    |_|  |_/_/    \_\_|    |_____/ 
#------------------------------------------------------------------                                                       
                                                       
@app.route('/test_API/',methods =['GET'])
def mostrarAPI():
    api = requests.get("https://randomuser.me/api/")
    return api.text

@app.route('/buscagasolineras/<locationdata>', methods= ['GET'])
def buscagasolineras(locationdata):
   # place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
   # url = place_api_url + urllib.parse.urlencode({"input":locationdata,"inputtype":'textquery',"fields":'geometry', "key":API_KEY_MAPS})
   # json_data_place = requests.get(url).json()
    latitud = str(getLatitud(locationdata))
    longitud = str(getLongitud(locationdata))

    #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522%2C151.1957362&radius=1500&type=restaurant&keyword=cruise&key=AIzaSyDznNAUPqKZhq9Czvpzq3Nl8ppJOd0L_XI"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+latitud+"%2C"+longitud+"&radius=1000&type=gas_station&key=AIzaSyDznNAUPqKZhq9Czvpzq3Nl8ppJOd0L_XI"
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    return(response.text)

def getLatitud(lugar):
    place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    url = place_api_url + urllib.parse.urlencode({"input":lugar,"inputtype":'textquery',"fields":'geometry', "key":API_KEY_MAPS})
    json_data_place = requests.get(url).json()
    latitud = str(json_data_place['candidates'][0]['geometry']['location']['lat'])
    return latitud    

def getLongitud(lugar):
    place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    url = place_api_url + urllib.parse.urlencode({"input":lugar,"inputtype":'textquery',"fields":'geometry', "key":API_KEY_MAPS})
    json_data_place = requests.get(url).json()
    longitud = str(json_data_place['candidates'][0]['geometry']['location']['lng'])
    return longitud 

@app.route('/inforuta/<origen>/<destino>', methods=['GET'])      # principal para consultas en maps teniendo origen y destino
def ruta(origen, destino):                                       # devuelve el json con toda la informacion
    directions_api_url = "https://maps.googleapis.com/maps/api/directions/json?"
    url = directions_api_url + urllib.parse.urlencode({"origin":origen, "destination":destino, "key":API_KEY_MAPS})
    json_data = requests.get(url).json()
    print(url)
    return json_data

@app.route('/distancia/<origen>/<destino>', methods=['GET'])
def distancia(origen, destino):                                  # devuelve la distancia entre origen y destino
    json_data = ruta(origen,destino)
    distancia = json_data['routes'][0]['legs'][0]['distance']['text'] #hay que controlar el error por si no encuentra ruta
    return distancia

@app.route('/duracion/<origen>/<destino>', methods=['GET'])
def duracion(origen, destino):                                   # devuelve la duracion entre origen y destino
    json_data = ruta(origen,destino)
    distancia = json_data['routes'][0]['legs'][0]['duration']['text'] #hay que controlar el error por si no encuentra ruta
    return distancia


#------------------------------------------------------------------
#           _____ _____    
#     /\   |  __ \_   _|   
#    /  \  | |__) || |     
#   / /\ \ |  ___/ | |       TIEMPO
#  / ____ \| |    _| |_     
# /_/    \_\_|   |_____|    
#------------------------------------------------------------------   

@app.route('/tiempo/<lugar>', methods=['GET'])
def tiempo(lugar):  
    #LLAMADA "https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}"
    tiempo_url = "https://api.openweathermap.org/data/2.5/onecall?"
    url = tiempo_url + urllib.parse.urlencode({"lat":getLatitud(lugar),"lon":getLongitud(lugar),  "appid":API_KEY_TIEMPO})
    json_data = requests.get(url).json()
    return json_data

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'mensaje': 'Recurso no encontrado: ' + request.url,
        'Status': 404
    })
    response.status = 404
    return response

if __name__ == '__main__':
    app.run(debug=True)
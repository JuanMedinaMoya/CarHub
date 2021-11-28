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
from datetime import datetime


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
Valoraciones = mongo.db.Valoraciones

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
    d_fechanacimiento = datetime.strptime(fechanacimiento, '%d/%m/%y')
    telefono = request.json['telefono']
    paypal = request.json['paypal']
    foto = request.json['foto']

    if nombre and apellidos and correo and contrasena and dni and fechanacimiento and telefono:
        hashed_contrasena = generate_password_hash(contrasena)
        id = Usuarios.insert(
            {'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': hashed_contrasena, 'dni': dni, 'fechanacimiento': d_fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}
        )
        resp = jsonify("Usuario añadido")
        return resp
    else:
        return not_found()

@app.route('/mostrar_usuarios', methods=['GET'])
def mostrar_usuarios():
    usuarios = Usuarios.find()
    resp = json_util.dumps(usuarios)
    return Response(resp, mimetype='application/json')

@app.route('/borrar_usuario/<id>', methods=['DELETE'])
def borrar_usuario(id):
    usuario = Usuarios.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Usuario eliminado")
    return resp

@app.route('/actualizar_usuario/<id>' , methods = ['PUT'])
def actualizar_usuario(id):
    username = request.json['username']
    nombre = request.json['nombre']
    apellidos = request.json['apellidos']
    coche = request.json['coche']
    correo = request.json['correo']
    contrasena = request.json['contrasena']
    dni = request.json['dni']
    fechanacimiento = request.json['fechanacimiento']
    d_fechanacimiento = datetime.strptime(fechanacimiento, '%d/%m/%y')
    telefono = request.json['telefono']
    paypal = request.json['paypal']
    foto = request.json['foto']
    hashed_contrasena = generate_password_hash(contrasena)

    Usuarios.update_one({'_id': ObjectId(id)},{'$set':{'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': hashed_contrasena, 'dni': dni, 'fechanacimiento': d_fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}})
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


#OP CONSULTA CON RELACIONES ENTRE LAS ENTIDADES


@app.route('/mis_viajes/<idusuario>', methods=['GET'])
def mis_viajes(idusuario):
    trayectos = Trayectos.find({'pasajeros': {'$all': [ObjectId(idusuario)]}})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/mis_trayectos_creados/<idusuario>', methods = ['GET'])
def mis_trayectos_creados(idusuario):
    trayectos = Trayectos.find({'conductor': {'$all': [ObjectId(idusuario)]}})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')


#-------------------------------------------------------------------------
#
#   _____ ____  _   ___      ________ _____   _____         _____ _____ ____  _   _ ______  _____ 
#  / ____/ __ \| \ | \ \    / /  ____|  __ \ / ____|  /\   / ____|_   _/ __ \| \ | |  ____|/ ____|
# | |   | |  | |  \| |\ \  / /| |__  | |__) | (___   /  \ | |      | || |  | |  \| | |__  | (___  
# | |   | |  | | . ` | \ \/ / |  __| |  _  / \___ \ / /\ \| |      | || |  | | . ` |  __|  \___ \ 
# | |___| |__| | |\  |  \  /  | |____| | \ \ ____) / ____ \ |____ _| || |__| | |\  | |____ ____) |
#  \_____\____/|_| \_|   \/   |______|_|  \_\_____/_/    \_\_____|_____\____/|_| \_|______|_____/                                                                                                                                                                                                  
#                                                                         
#-------------------------------------------------------------------------

@app.route('/crear_conversacion/<id1>/<id2>', methods=['POST'])
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

@app.route('/mostrar_conversaciones', methods=['GET'])
def mostrar_conversaciones():
    conversaciones = Conversaciones.find()
    response = json_util.dumps(conversaciones)
    return Response(response, mimetype="application/json")

@app.route('/buscar_conversacion_id/<id>', methods=['GET'])
def buscar_conversacion_id(id):
    conversacion = Conversaciones.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(conversacion)
    return response

@app.route('/borrar_conversacion/<id>', methods=['DELETE'])
def borrar_conversacion(id):
    if Conversaciones.count_documents({'_id': ObjectId(id)}) == 1:
        Conversaciones.delete_one({'_id': ObjectId(id)})
        response = jsonify({
            'mensaje': 'La conversacion con id: ' + id + ' fue eliminada satisfactoriamente.'
        })
    else:
        return not_found()
    return response
    
@app.route('/enviar_mensaje/<idc>/<idu>', methods=['PATCH'])
def enviar_mensaje(idc, idu):
    contenido = request.json['contenido']
    conver_incluido = Conversaciones.count_documents({'$or': {
        {'_id': ObjectId(idc), 'user1': ObjectId(idu)},
        {'_id': ObjectId(idc), 'user2': ObjectId(idu)}
    }}) == 1
    if contenido and conver_incluido:
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

@app.route('/buscar_conversaciones_usuario/user/<id>', methods=['GET'])
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
    d_horasalida = datetime.strptime(horasalida, '%d/%m/%y %H:%M:%S')
    precio = request.json['precio']
    numeropasajeros = request.json['numeropasajeros']
    finalizado = 0
    pasajeros = []

    if origen and destino and horasalida and precio and numeropasajeros :
        id = Trayectos.insert(
            {'conductor':conductor, 'origen': origen, 'destino': destino, 'horasalida': d_horasalida, 'precio': precio, 'numeropasajeros': numeropasajeros, 'finalizado':finalizado, 'pasajeros' : pasajeros}
        )
        resp = jsonify("Trayecto añadido")
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route('/mostrar_trayectos', methods=['GET'])
def mostrar_trayectos():
    trayectos = Trayectos.find()
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/borrar_trayecto/<id>', methods=['DELETE'])
def borrar_trayecto(id):
    trayectos = Trayectos.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Trayecto eliminado")
    return resp

@app.route('/actualizar_trayecto/<id>' , methods = ['PUT'])
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

@app.route('/finalizar_trayecto/<idtrayecto>', methods = ['PUT'])
def finalizar_trayecto(idtrayecto):
    Trayectos.update_one({'_id': ObjectId(idtrayecto)},{'$set':{'finalizado': 1}})
    resp = jsonify("Trayecto finalizado")
    return resp
    

@app.route('/buscar_trayecto_completo', methods = ['GET'])
def buscar_trayecto_completo():
    origen = request.json['origen']
    destino = request.json['destino']
    horasalida = request.json['horasalida']
    d_horasalida = datetime.strptime(horasalida, '%d/%m/%y %H:%M:%S')
    numeropasajeros = request.json['numeropasajeros']

    trayectos = Trayectos.find({'origen': origen, 'destino': destino, 'horasalida': d_horasalida, 'numeropasajeros': numeropasajeros}).sort('horasalida', 1)
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')


#OP CONSULTA CON RELACIONES ENTRE LAS ENTIDADES


@app.route('/anadir_pasajero/<idtrayecto>/<idpasajero>', methods = ['PATCH'])
def anadir_pasajero(idtrayecto, idpasajero):
    trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
    numpasajeros = trayecto['numeropasajeros']
    conductor = trayecto['conductor']
    pasajeros = trayecto['pasajeros']
    finalizado = trayecto['finalizado']
    if numpasajeros > 0 and ObjectId(idpasajero) not in pasajeros and finalizado == 0 and conductor != ObjectId(conductor): 
        pasajeros.append(ObjectId(idpasajero))
        Trayectos.update_one({'_id': ObjectId(idtrayecto)},{'$set':{'pasajeros' : pasajeros, 'numeropasajeros' : numpasajeros-1}})
        resp = jsonify("Pasajero añadido")
    else:
        resp = jsonify("No se puede añadir pasajero")
    return resp

@app.route('/pasajeros_trayecto/<idtrayecto>', methods = ['GET'])
def pasajeros_trayecto(idtrayecto):
    trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
    pasajeros = trayecto['pasajeros']
    pasajerosPerfil = []
    if pasajeros :
        for id in pasajeros :
            usuario = Usuarios.find_one({'_id': ObjectId(id)})
            pasajerosPerfil.append(usuario)
        resp = json_util.dumps(pasajerosPerfil)
        return Response(resp, mimetype='application/json')
    else:
        return not_found()
    



#------------------------------------------------------------------
# __      __     _      ____  _____            _____ _____ ____  _   _ ______  _____ 
# \ \    / /\   | |    / __ \|  __ \     /\   / ____|_   _/ __ \| \ | |  ____|/ ____|
#  \ \  / /  \  | |   | |  | | |__) |   /  \ | |      | || |  | |  \| | |__  | (___  
#   \ \/ / /\ \ | |   | |  | |  _  /   / /\ \| |      | || |  | | . ` |  __|  \___ \ 
#    \  / ____ \| |___| |__| | | \ \  / ____ \ |____ _| || |__| | |\  | |____ ____) |
#     \/_/    \_\______\____/|_|  \_\/_/    \_\_____|_____\____/|_| \_|______|_____/                                                                                                                                                                                                                                                                                                                   
#
#------------------------------------------------------------------ 


#CRUD


@app.route('/crear_valoracion/<idvalorado>/<idtrayecto>/<idvalorador>', methods=['POST'])
def crear_valoracion(idvalorado, idtrayecto, idvalorador):
    valorado = ObjectId(idvalorado)
    trayecto = ObjectId(idtrayecto)
    valorador = ObjectId(idvalorador)
    puntuacion = request.json['puntuacion']
    comentario = request.json['comentario']

    if puntuacion and comentario:
        id = Valoraciones.insert(
            {'valorado':valorado, 'trayecto': trayecto, 'valorador': valorador, 'puntuacion': puntuacion, 'comentario': comentario}
        )
    else:
        id = Valoraciones.insert(
            {'valorado':valorado, 'trayecto': trayecto, 'valorador': valorador, 'puntuacion': puntuacion}
        )
    resp = jsonify("Valoracion añadida")
    resp.status_code = 200
    return resp
    

@app.route('/mostrar_valoraciones', methods=['GET'])
def mostrar_valoraciones():
    trayectos = Trayectos.find()
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/borrar_valoracion/<id>', methods=['DELETE'])
def borrar_valoracion(id):
    valoraciones = Valoraciones.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Valoracion eliminada")
    return resp

@app.route('/actualizar_valoracion/<id>' , methods = ['PUT'])
def actualizar_valoracion(id):

    puntuacion = request.json['puntuacion']
    comentario = request.json['comentario']

    Trayectos.update_one({'_id': ObjectId(id)},{'$set':{'puntuacion': puntuacion, 'comentario': comentario}})
    resp = jsonify("Valoración actualizada")
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

    return json_data

@app.route('/distancia/<origen>/<destino>', methods=['GET'])
def distancia(origen, destino):                                  # devuelve la distancia entre origen y destino
    json_data = ruta(origen,destino)
    distancia = json_data['routes'][0]['legs'][0]['distance']['text'] #hay que controlar el error por si no encuentra ruta
    return distancia

@app.route('/duracion/<origen>/<destino>', methods=['GET'])
def duracion(origen, destino):                                   # devuelve la duracion entre origen y destino
    json_data = ruta(origen,destino)
    duracion = json_data['routes'][0]['legs'][0]['duration']['text'] #hay que controlar el error por si no encuentra ruta
    return duracion


#------------------------------------------------------------------
#           _____ _____   _______ _____ ______ __  __ _____   ____  
#     /\   |  __ \_   _| |__   __|_   _|  ____|  \/  |  __ \ / __ \ 
#    /  \  | |__) || |      | |    | | | |__  | \  / | |__) | |  | |
#   / /\ \ |  ___/ | |      | |    | | |  __| | |\/| |  ___/| |  | |
#  / ____ \| |    _| |_     | |   _| |_| |____| |  | | |    | |__| |
# /_/    \_\_|   |_____|    |_|  |_____|______|_|  |_|_|     \____/ 
#                                                                                                                                     
#------------------------------------------------------------------   

@app.route('/infotiempo/<lugar>', methods=['GET'])
def infotiempo(lugar):  
    #LLAMADA "https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}"
    tiempo_url = "https://api.openweathermap.org/data/2.5/onecall?"
    url = tiempo_url + urllib.parse.urlencode({"lat":getLatitud(lugar),"lon":getLongitud(lugar), "appid":API_KEY_TIEMPO})
    json_data = requests.get(url).json()
    return json_data

@app.route('/lluvias/<lugar>/<fechayhora>', methods=['GET'])
def lluvias(lugar, fechayhora):
    json_data_lugar = infotiempo(lugar)
    dt = str(fechayhora)
    list = json_data_lugar['hourly']
    lluvia = 0
    for i in list:
        if dt == str(i['dt']):
            try:
               lluvia = i['rain']['1h'] 
            except KeyError:
                return "0"

    return str(lluvia)

@app.route('/nieve/<lugar>/<fechayhora>', methods=['GET'])
def nieve(lugar, fechayhora):
    json_data_lugar = infotiempo(lugar)
    fechayhora_int = int(fechayhora) - (int(fechayhora) % 3600)
    dt = str(fechayhora_int)
    list = json_data_lugar['hourly']
    nieve = 0
    for i in list:
        if dt == str(i['dt']):
            try:
               nieve = i['snow']['1h'] 
            except KeyError:
                return "0"

    return str(nieve)

@app.route('/visibilidad/<lugar>/<fechayhora>', methods=['GET'])
def visibilidad(lugar, fechayhora):
    json_data_lugar = infotiempo(lugar)
    fechayhora_int = int(fechayhora) - (int(fechayhora) % 3600)
    dt = str(fechayhora_int)
    list = json_data_lugar['hourly']
    visibilidad = 0
    for i in list:
        if dt == str(i['dt']):
            try:
               visibilidad = i['visibility'] 
            except KeyError:
                return "0"

    return str(visibilidad)

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
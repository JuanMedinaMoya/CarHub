from bson.objectid import ObjectId
from flask import Flask, json, request, jsonify, Response 
from flask_pymongo import PyMongo
from flask import render_template
from pymongo import mongo_client
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from bson import json_util
import requests

app = Flask (__name__)
app.config["MONGO_URI"] = "mongodb+srv://CarHubAdmin:1234@carhub.n2ouf.mongodb.net/CarHubDB?retryWrites=true&w=majority"

mongo = PyMongo(app)

Usuarios = mongo.db.Usuarios
Trayectos = mongo.db.Trayectos

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
    if numpasajeros > 0 and ObjectId(idpasajero) not in pasajeros and finalizado == 0 and conductor != ObjectId(conductor):
        pasajeros.append(ObjectId(idpasajero))
        Trayectos.update_one({'_id': ObjectId(idtrayecto)},{'$set':{'pasajeros' : pasajeros, 'numeropasajeros' : numpasajeros-1}})
        resp = jsonify("Pasajero añadido")
    else:
        resp = jsonify("No se puede añadir pasajero")
    return resp

@app.route('/test_API/',methods =['GET'])
def mostrarAPI():
    api = requests.get("https://randomuser.me/api/")
    return api.text

if __name__ == '__main__':
    app.run(debug=True)
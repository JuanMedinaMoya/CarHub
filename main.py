from bson.objectid import ObjectId
from flask import Flask, json, request, jsonify, Response 
from flask_pymongo import PyMongo
from flask import render_template
from pymongo import mongo_client
from werkzeug.utils import redirect
from bson import json_util

app = Flask (__name__)
app.config["MONGO_URI"] = "mongodb+srv://CarHubAdmin:1234@carhub.n2ouf.mongodb.net/CarHubDB?retryWrites=true&w=majority"

mongo = PyMongo(app)

Usuarios = mongo.db.Usuarios
Trayectos = mongo.db.Trayectos

@app.route('/crearusuario', methods=['POST'])
def crearusuario():
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
        id = Usuarios.insert(
            {'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto, 'trayectos' : []}
        )
        resp = jsonify("Usuario añadido")
        resp.status_code = 200
        return resp

@app.route('/mostrarusuarios', methods=['GET'])
def mostrarusuarios():
    usuarios = Usuarios.find()
    resp = json_util.dumps(usuarios)
    return Response(resp, mimetype='application/json')

@app.route('/buscarusuario/<id>', methods=['GET'])
def buscarusuario(id):
    usuario = Usuarios.find_one({'_id': ObjectId(id)})
    resp = json_util.dumps(usuario)
    return Response(resp, mimetype='application/json')

@app.route('/buscarnombre/<filtro>', methods=['GET'])
def buscarnombre(filtro):
    usuarios = Usuarios.find({'nombre': filtro})
    resp = json_util.dumps(usuarios)
    return Response(resp, mimetype='application/json')

@app.route('/borrarusuario/<id>', methods=['GET'])
def borrarusuario(id):
    usuario = Usuarios.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Usuario eliminado")
    return resp

@app.route('/actualizarusuario/<id>' , methods = ['POST'])
def actualizarusuario(id):
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

    Usuarios.update_one({'_id': ObjectId(id)},{'$set':{'username': username, 'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}})
    resp = jsonify("Usuario eliminado")
    return resp

@app.route('/creartrayecto', methods=['POST'])
def creartrayecto():
    conductor = request.json['conductor']
    origen = request.json['origen']
    destino = request.json['destino']
    horasalida = request.json['horasalida']
    precio = request.json['precio']
    numeropasajeros = request.json['numeropasajeros']
    pasajeros = ""
    finalizado = "0"

    if conductor and origen and destino and horasalida and precio and numeropasajeros :
        id = Trayectos.insert(
            {'conductor':conductor,'origen': origen, 'origen': origen, 'destino': destino, 'horasalida': horasalida, 'precio': precio, 'numeropasajeros': numeropasajeros, 'finalizado':finalizado, 'pasajeros': ""}
        )
        resp = jsonify("Usuario añadido")
        resp.status_code = 200
        return resp


@app.route('/mostrartrayectos', methods=['GET'])
def mostrartrayectos():
    trayectos = Trayectos.find()
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/buscartrayecto/<id>', methods=['GET'])
def buscartrayecto(id):
    trayectos = Trayectos.find_one({'_id': ObjectId(id)})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/borrartrayecto/<id>', methods=['GET'])
def borrartrayecto(id):
    trayectos = Trayectos.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Trayecto eliminado")
    return resp

@app.route('/actualizartrayecto/<id>' , methods = ['POST'])
def actualizartrayecto(id):

    origen = request.json['origen']
    destino = request.json['destino']
    horasalida = request.json['horasalida']
    precio = request.json['precio']
    numeropasajeros = request.json['numeropasajeros']
    pasajeros = ""
    finalizado = request.json['finalizado']

    Trayectos.update_one({'_id': ObjectId(id)},{'$set':{'origen': origen, 'destino': destino, 'horasalida': horasalida, 'precio': precio, 'numeropasajeros': numeropasajeros, 'finalizado': finalizado}})
    resp = jsonify("Trayecto actualizado")
    return resp

@app.route('/buscarorigen/<origen>', methods = ['GET'])
def buscarorigen(origen):
    trayectos = Trayectos.find({'origen': origen})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/buscardestino/<destino>', methods = ['GET'])
def buscardestino(destino):
    trayectos = Trayectos.find({'destino': destino})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

@app.route('/buscarorigendestino/<origen>/<destino>', methods = ['GET'])
def buscarorigendestino(origen, destino):
    trayectos = Trayectos.find({'origen': origen, 'destino': destino})
    resp = json_util.dumps(trayectos)
    return Response(resp, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
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

@app.route('/crearusuario', methods=['POST'])
def crearusuario():
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

    if nombre and apellidos and coche and correo and contrasena and dni and fechanacimiento and telefono and paypal and foto:
        id = Usuarios.insert(
            {'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}
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

@app.route('/borrarusuario/<id>', methods=['GET'])
def borrarusuario(id):
    usuario = Usuarios.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Usuario eliminado")
    return resp

@app.route('/actualizarusuario/<id>' , methods = ['POST'])
def actualizarusuario(id):
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

    Usuarios.update_one({'_id': ObjectId(id)},{'$set':{'nombre': nombre, 'apellidos': apellidos, 'coche': coche, 'correo': correo, 'contrasena': contrasena, 'dni': dni, 'fechanacimiento': fechanacimiento, 'telefono': telefono, 'paypal': paypal, 'foto': foto}})
    resp = jsonify("Usuario eliminado")
    return resp

if __name__ == '__main__':
    app.run(debug=True)
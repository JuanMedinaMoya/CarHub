from datetime import date, datetime, timedelta
from dns.rdatatype import NULL
from flask.templating import render_template_string

from werkzeug.datastructures import Authorization
from bson.objectid import ObjectId
from flask import Flask, json, request, jsonify, Response, session, flash, redirect
from flask_pymongo import PyMongo
from flask import render_template
from pymongo import mongo_client
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from bson import json_util
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import requests
import urllib
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import google.oauth2.id_token
from datetime import datetime
from imgurpython import ImgurClient
import os
from itertools import chain


from authlib.integrations.flask_client import OAuth
from flask import url_for, render_template

from werkzeug.wrappers import response

app = Flask(__name__)



app.config[
    "MONGO_URI"] = "mongodb+srv://CarHubAdmin:1234@carhub.n2ouf.mongodb.net/CarHubDB?retryWrites=true&w=majority"
app.config["FOTO_UPLOADS"] = os.getcwd()

API_KEY_MAPS = "AIzaSyC1GXp71yv3zHYbZBvgu6a0CTL7SMxEZzk"
API_KEY_TIEMPO = "be0d42dee8a7dc753453bdaa8a20f26a"
app.config['GOOGLEMAPS_KEY'] = API_KEY_MAPS

app.secret_key = "CarHub"

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="195417323379-cfskdhqvf71gkoajilafthirmlvgt3da.apps.googleusercontent.com",
    client_secret="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",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


mongo = PyMongo(app)
maps = GoogleMaps(app)

client_id = "0395845c9df00b0"
client_secret = "90c28199ac4625ad38af84077253b22d3a346436"

client = ImgurClient(client_id, client_secret,
                     "43d6958c71e03f7d0f6e5cfdb62122557c31edc6",
                     "e2b6db72adc1a6bbf8c63246d6a5d45c4c8ffc86")    

Usuarios = mongo.db.Usuarios
Trayectos = mongo.db.Trayectos
Conversaciones = mongo.db.Conversaciones
Valoraciones = mongo.db.Valoraciones
TrayectosPrueba = mongo.db.TrayectosPrueba




#------------------------------------------------------------

#------------------------------------------------------------
#  _    _  _____ _    _         _____  _____ ____   _____
# | |  | |/ ____| |  | |  /\   |  __ \|_   _/ __ \ / ____|
# | |  | | (___ | |  | | /  \  | |__) | | || |  | | (___
# | |  | |\___ \| |  | |/ /\ \ |  _  /  | || |  | |\___ \
# | |__| |____) | |__| / ____ \| | \ \ _| || |__| |____) |
#  \____/|_____/ \____/_/    \_\_|  \_\_____\____/|_____/
#
#------------------------------------------------------------

#------------------------------------------------------------



@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/logingoogle')
def logingoogle():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()['id_token']

        CLIENT_ID="195417323379-cfskdhqvf71gkoajilafthirmlvgt3da.apps.googleusercontent.com"
        id_info = id_token.verify_oauth2_token(token,requests.Request(),CLIENT_ID,10)

        session["token"] = token

        resp = google.get('userinfo')
        resp.raise_for_status()
        user_info = resp.json()
        email = user_info["email"]
        arraystr = email.split('@', 1)
            
        if Usuarios.find_one({"correo": email}):
            usuario = Usuarios.find_one({"correo": email})   
            session["username"] = usuario["username"] 
            puedeCrear = (usuario['paypal'] != "") and (usuario['coche'] != "") and (usuario['dni'] != "")  and (usuario['telefono'] != "")
            session["creador"] = puedeCrear

        else:
            id = Usuarios.insert({
                
                'username': arraystr[0],
                'nombre': user_info["given_name"],
                'apellidos': user_info["family_name"],
                'correo': email,
                'contrasena': "",
                'foto': user_info["picture"],
                'dni': "",
                'fechanacimiento': "",
                'telefono': "",
                'coche': "",
                'paypal': ""
            })
            usuario = Usuarios.find_one({"correo": email})   
            session["username"] = arraystr[0]
            puedeCrear = (usuario['paypal'] != "") and (usuario['coche'] != "") and (usuario['dni'] != "") and (usuario['telefono'] != "")
            session["creador"] = puedeCrear
    except Exception as ex:
        return "Error de autenticación: " + str(ex), 401           
    # do something with the token and profile
    return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        correousername = request.form['correousername']
        contrasena = request.form['contrasena']
        busq = Usuarios.find_one({
            '$or': [{
                'correo': correousername
            }, {
                'username': correousername
            }]
        })
        if busq == None:
            error = "Error: correo electrónico o Username no existente"
            return render_template('login.html',
                                   correousername=correousername,
                                   contrasena=contrasena,
                                   error=error)

        if check_password_hash(busq['contrasena'], contrasena):
            puedeCrear =  (busq['paypal'] != "") or (busq['coche'] != "") or (busq['dni'] != "") or (busq['fechanacimiento'] != "") or (busq['telefono'] != "")
            session["username"] = busq['username']
            session["creador"] = puedeCrear
            return redirect("/")
        else:
            error = "Error: contraseña incorrecta"
            return render_template('login.html',
                                   correousername=correousername,
                                   contrasena=contrasena,
                                   error=error)


@app.route('/registro', methods=['POST', 'GET'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')
    else:
        username = request.form['username']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        dni = request.form['dni']
        fechanacimiento = request.form['fechanacimiento']
        d_fechanacimiento = datetime.strptime(fechanacimiento, '%Y-%m-%d')
        telefono = request.form['telefono']
        contrasena = request.form['contrasena']
        contrasenarep = request.form['contrasenarep']
        hashed_contrasena = generate_password_hash(contrasena)

        if Usuarios.find_one({"correo": correo}):
            error = "Correo electrónico ya en uso"
            return render_template('registro.html',
                                   username=username,
                                   nombre=nombre,
                                   apellidos=apellidos,
                                   correo=correo,
                                   dni=dni,
                                   fechanacimiento=fechanacimiento,
                                   telefono=telefono,
                                   contrasena=contrasena,
                                   contrasenarep=contrasenarep,
                                   error=error)
        if Usuarios.find_one({"username": username}):
            error = "Error: username ya en uso"
            return render_template('registro.html',
                                   username=username,
                                   nombre=nombre,
                                   apellidos=apellidos,
                                   correo=correo,
                                   dni=dni,
                                   fechanacimiento=fechanacimiento,
                                   telefono=telefono,
                                   contrasena=contrasena,
                                   contrasenarep=contrasenarep,
                                   error=error)
        if contrasena != contrasenarep:
            error = "Error: contraseñas no iguales"
            return render_template('registro.html',
                                   username=username,
                                   nombre=nombre,
                                   apellidos=apellidos,
                                   correo=correo,
                                   dni=dni,
                                   fechanacimiento=fechanacimiento,
                                   telefono=telefono,
                                   contrasena=contrasena,
                                   contrasenarep=contrasenarep,
                                   error=error)
        id = Usuarios.insert({
            'username': username,
            'nombre': nombre,
            'apellidos': apellidos,
            'correo': correo,
            'contrasena': hashed_contrasena,
            'foto': "https://www.traigoyllevo.com/categorias/imagen-icono/1",
            'dni': dni,
            'fechanacimiento': d_fechanacimiento,
            'telefono': telefono,
            'coche': "",
            'paypal': ""
        })
        session["username"] = username
        session["creador"] = False
        return redirect("/")



@app.route('/perfil', methods=['POST', 'GET'])
def perfil():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        username = session["username"]
        usuario = Usuarios.find_one({"username": username})
        return render_template('perfil.html', usuario=usuario)


@app.route('/perfilId/<id>', methods=['POST', 'GET'])
def perfilId(id):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        usuario = Usuarios.find_one({'_id': ObjectId(id)})
        media = media_valoraciones(id)
        numvaloraciones = num_valoraciones(id)
        valoraciones = Valoraciones.find({"valorado": ObjectId(id)})

        valoracion = []
        for val in valoraciones:
            user = Usuarios.find_one({'_id': ObjectId(val['valorador'])})
            valoracion.append({
                'nombre': user['username'],
                'comentario': val['comentario'],
                'puntuacion': val['puntuacion']
            })

        return render_template('perfilId.html',
                            usuario=usuario,
                            media=media,
                            valoraciones=valoracion,
                            numvaloraciones=numvaloraciones)


@app.route('/editarperfil', methods=['POST', 'GET'])
def perfilEditar():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if request.method == 'GET':
            username = session["username"]
            usuario = Usuarios.find_one({"username": username})
            return render_template('perfilEditar.html', usuario=usuario)
        else:
            usuario = Usuarios.find_one({"username": session["username"]})
            correoAntiguo = usuario["correo"]

            nombre = request.form['nombre']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            dni = request.form['dni']
            telefono = request.form['telefono']
            coche = request.form['coche']
            paypal = request.form['paypal']
            contrasena = request.form['contrasena']
            contrasenarep = request.form['contrasenarep']
            hashed_contrasena = generate_password_hash(contrasena)

            if correoAntiguo != correo and Usuarios.find_one({"correo": correo}):
                error = "Correo electrónico ya en uso"
                return redirect('/editarperfil', error=error)

            if contrasena != contrasenarep:
                error = "Contraseñas no iguales"
                return redirect('/editarperfil', error=error)

            if contrasena == "":

                if request.files["foto"]:

                    foto = request.files["foto"]
                    foto.save(
                        os.path.join(app.config["FOTO_UPLOADS"], foto.filename))
                    config = {'title': str(ObjectId(usuario['_id']))}

                    items = client.get_account_images("CarHubUMA", page=0)
                    for item in items:
                        if item.title == str(ObjectId(usuario['_id'])):
                            client.delete_image(item.id)

                    client.upload_from_path(app.config["FOTO_UPLOADS"] + "/" +
                                            foto.filename,
                                            config=config,
                                            anon=False)
                    os.remove(foto.filename)
                    items = client.get_account_images("CarHubUMA", page=0)
                    url = None
                    for item in items:
                        if item.title == str(ObjectId(usuario['_id'])):
                            url = item.link

                    id = Usuarios.update_one({'username': session["username"]}, {
                        '$set': {
                            'nombre': nombre,
                            'apellidos': apellidos,
                            'correo': correo,
                            'dni': dni,
                            'coche': coche,
                            'paypal': paypal,
                            'foto': url,
                            'telefono': telefono
                        }
                    })
                else:
                    id = Usuarios.update_one({'username': session["username"]}, {
                        '$set': {
                            'nombre': nombre,
                            'apellidos': apellidos,
                            'correo': correo,
                            'dni': dni,
                            'coche': coche,
                            'paypal': paypal,
                            'telefono': telefono
                        }
                    })

            else:
                if request.files["foto"]:

                    foto = request.files["foto"]
                    foto.save(
                        os.path.join(app.config["FOTO_UPLOADS"], foto.filename))
                    config = {'title': str(ObjectId(usuario['_id']))}

                    items = client.get_account_images("CarHubUMA", page=0)
                    for item in items:
                        if item.title == str(ObjectId(usuario['_id'])):
                            client.delete_image(item.id)

                    client.upload_from_path(app.config["FOTO_UPLOADS"] + "/" +
                                            foto.filename,
                                            config=config,
                                            anon=False)
                    os.remove(foto.filename)
                    items = client.get_account_images("CarHubUMA", page=0)
                    url = None
                    for item in items:
                        if item.title == str(ObjectId(usuario['_id'])):
                            url = item.link

                    id = Usuarios.update_one({'username': session["username"]}, {
                        '$set': {
                            'nombre': nombre,
                            'apellidos': apellidos,
                            'correo': correo,
                            'contrasena': hashed_contrasena,
                            'dni': dni,
                            'coche': coche,
                            'paypal': paypal,
                            'foto': url,
                            'telefono': telefono
                        }
                    })
                else:
                    id = Usuarios.update_one({'username': session["username"]}, {
                        '$set': {
                            'nombre': nombre,
                            'apellidos': apellidos,
                            'correo': correo,
                            'contrasena': hashed_contrasena,
                            'dni': dni,
                            'coche': coche,
                            'paypal': paypal,
                            'telefono': telefono
                        }
                    })
            session["creador"] = paypal != "" and coche != ""
            return redirect('/perfil')


@app.route('/eliminarusuario')
def eliminar_usuario():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        usuario = Usuarios.delete_one({'username': session["username"]})
        return redirect('/logout')


@app.route('/logout')
def logout():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        session.clear()
        return redirect("/")




#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
#
#   _____ ____  _   ___      ________ _____   _____         _____ _____ ____  _   _ ______  _____
#  / ____/ __ \| \ | \ \    / /  ____|  __ \ / ____|  /\   / ____|_   _/ __ \| \ | |  ____|/ ____|
# | |   | |  | |  \| |\ \  / /| |__  | |__) | (___   /  \ | |      | || |  | |  \| | |__  | (___
# | |   | |  | | . ` | \ \/ / |  __| |  _  / \___ \ / /\ \| |      | || |  | | . ` |  __|  \___ \
# | |___| |__| | |\  |  \  /  | |____| | \ \ ____) / ____ \ |____ _| || |__| | |\  | |____ ____) |
#  \_____\____/|_| \_|   \/   |______|_|  \_\_____/_/    \_\_____|_____\____/|_| \_|______|_____/
#
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------


@app.route('/crear_conversacion/<usuario1>/<usuario2>', methods=['POST'])
def crear_conversacion(usuario1, usuario2):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        listMensajes = []
        id1 = Usuarios.find_one({'username': usuario1})['_id']
        id2 = Usuarios.find_one({'username': usuario2})['_id']
        if id1 and id2 and id1 != id2:
            conversacion = Conversaciones.find_one({
                '$or': [{
                    'user1': ObjectId(id1),
                    'user2': ObjectId(id2)
                }, {
                    'user1': ObjectId(id2),
                    'user2': ObjectId(id1)
                }]
            })
            if conversacion == None:  # Si no ha creado ya una conversacion
                id = Conversaciones.insert_one({
                    'user1': ObjectId(id1),
                    'user2': ObjectId(id2),
                    'listMensajes': listMensajes
                })
                response = {'mensaje': 'Conversacion creada con exito'}
            else:
                response = {'mensaje': 'Conversacion ya existente'}
        else:  # No encuentra los usuarios
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
    return Response(response, mimetype="application/json")


@app.route('/borrar_conversacion/<id>', methods=['DELETE'])
def borrar_conversacion(id):
    if Conversaciones.count_documents({'_id': ObjectId(id)}) == 1:
        Conversaciones.delete_one({'_id': ObjectId(id)})
        response = jsonify({
            'mensaje':
            'La conversacion con id: ' + id +
            ' fue eliminada satisfactoriamente.'
        })
    else:
        return not_found()
    return response


@app.route('/enviar_mensaje/<idc>/<idu>', methods=['PATCH'])
def enviar_mensaje(idc, idu):
    contenido = request.json['contenido']
    conver_incluido = Conversaciones.count_documents({
        '_id':
        ObjectId(idc),
        '$or': [{
            'user1': ObjectId(idu)
        }, {
            'user2': ObjectId(idu)
        }]
    }) == 1
    if contenido and conver_incluido:
        Conversaciones.update_one({'_id': ObjectId(idc)}, {
            '$push': {
                'listMensajes': {
                    'idUser': ObjectId(idu),
                    'contenido': contenido,
                    'fecha': datetime.utcnow()
                }
            }
        })
        response = {'mensaje': 'El mensaje ha sido enviado satisfactoriamente'}
    else:
        return not_found()
    return response


@app.route('/buscar_conversaciones_usuario/<usuario>', methods=['GET'])
def buscar_conversaciones_usuario(usuario):
    id = Usuarios.find_one({'username': usuario})['_id']
    conversaciones = Conversaciones.find(
        {'$or': [{
            'user1': ObjectId(id)
        }, {
            'user2': ObjectId(id)
        }]})
    response = json_util.dumps(conversaciones)
    return Response(response, mimetype="application/json")


@app.route('/mis_conversaciones/<usuario>', methods=['GET'])
def mis_conversaciones(usuario):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if not 'username' in session or usuario != session['username']:
            return not_access_permission()

        id = Usuarios.find_one({'username': usuario})['_id']
        mis_conversaciones = conversaciones = Conversaciones.find(
            {'$or': [{
                'user1': ObjectId(id)
            }, {
                'user2': ObjectId(id)
            }]})
        listConversaciones = []
        for c in mis_conversaciones:
            contact = c['user2'] if c['user1'] == ObjectId(id) else c['user1']
            contact = Usuarios.find_one({'_id': contact}, {
                '_id': 0,
                'foto': 1,
                'username': 1
            })
            listConversaciones.append({
                '_id': c['_id'],
                'username': contact['username'],
                'profile_picture': contact['foto']
            })
        return render_template('misConversaciones.html',
                            listConversaciones=listConversaciones,
                            len=len(listConversaciones))


@app.route('/conversacion/<contact>/<username>')
def crear_obtener_chat(contact, username):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        id1 = Usuarios.find_one({'username': username})['_id']
        id2 = Usuarios.find_one({'username': contact})['_id']
        conversacion = Conversaciones.find_one({
            '$or': [{
                'user1': ObjectId(id1),
                'user2': ObjectId(id2)
            }, {
                'user1': ObjectId(id2),
                'user2': ObjectId(id1)
            }]
        })
        if conversacion == None:
            crear_conversacion(contact, username)
            conversacion = Conversaciones.find_one({
                '$or': [{
                    'user1': ObjectId(id1),
                    'user2': ObjectId(id2)
                }, {
                    'user1': ObjectId(id2),
                    'user2': ObjectId(id1)
                }]
            })

        return redirect('/conversacion/chat/' + str(conversacion['_id']))


@app.route('/conversacion/chat/<id_conversacion>')
def entrar_conversacion(id_conversacion):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if Conversaciones.count_documents({'_id': ObjectId(id_conversacion)}) == 1:
            conversacion = Conversaciones.find_one(
                {'_id': ObjectId(id_conversacion)})
            id = Usuarios.find_one({'username': session["username"]})['_id']
            contact = conversacion['user2'] if conversacion[
                'user1'] == id else conversacion['user1']
            contact = Usuarios.find_one({'_id': contact}, {
                'foto': 1,
                'username': 1
            })
            return render_template('chat.html',
                                id=id,
                                id2=contact['_id'],
                                contact=contact['username'],
                                profile_picture=contact['foto'],
                                listMensajes=conversacion['listMensajes'],
                                id_conversacion=id_conversacion,
                                len_mensajes=len(conversacion['listMensajes']))
        else:
            return not_found()


@app.route('/enviarMensaje', methods=['POST'])
def enviarMensaje():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        contenido = request.form['contenido']
        id_conversacion = request.form['id_conversacion']
        id = Usuarios.find_one({'username': session["username"]})['_id']
        contenido = contenido.strip()
        if contenido != '':
            Conversaciones.update_one({'_id': ObjectId(id_conversacion)}, {
                '$push': {
                    'listMensajes': {
                        'idUser': id,
                        'contenido': contenido,
                        'fecha': datetime.utcnow()
                    }
                }
            })

        return ('4', 200)


@app.route('/recibirMensajes', methods=['POST'])
def recibirMensajes():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        id_conversacion = request.form['id_conversacion']
        currentTotal = int(request.form['currentTotal'])
        listMensajes = Conversaciones.find_one({'_id': ObjectId(id_conversacion)
                                                })['listMensajes']
        listMensajes = listMensajes[currentTotal:len(
            listMensajes
        )]
        rendered = getHTMLListaMensajes(listMensajes)
        return rendered    

def getHTMLListaMensajes(listMensajes):
    id = Usuarios.find_one({'username': session["username"]})['_id']
    listInHtml = '''{% for m in listMensajes %}
            {% if m['idUser'] == id %}
            <div class="row justify-content-end">
                <div class="col-auto">
                    <div class="alert-success text-end px-5 py-2 ms-5 mb-4">
                        <p class="text-break">
                            {{ m['contenido'] }}
                        </p>
                        <span>{{ m['fecha']|datetime }}</span>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="row ">
                <div class="col-auto justify-content-start">
                    <div class="alert-dark text-start mb-4 px-5 py-2 me-5">
                        <p class="text-break">
                            {{ m['contenido'] }}
                        </p>
                        <span class="">{{ m['fecha']|datetime }}</span>
                    </div>
                </div>
            </div>
            {% endif %}
            {% endfor %}
            '''
    return render_template_string(listInHtml, listMensajes=listMensajes, id=id)

@app.template_filter('datetime')
def date_format(value):
    months = ('Enero','Febrero',"Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre")
    month = months[value.month-1]
    hora = str(value.hour).zfill(2)
    minutos = str(value.minute).zfill(2)
    return "{} de {} del {} a las {}:{}hs".format(value.day, month, value.year, hora, minutos)


#------------------------------------------------------------------

#------------------------------------------------------------------
#  _______ _____        __     ________ _____ _______ ____   _____
# |__   __|  __ \     /\\ \   / /  ____/ ____|__   __/ __ \ / ____|
#    | |  | |__) |   /  \\ \_/ /| |__ | |       | | | |  | | (___
#    | |  |  _  /   / /\ \\   / |  __|| |       | | | |  | |\___ \
#    | |  | | \ \  / ____ \| |  | |___| |____   | | | |__| |____) |
#    |_|  |_|  \_\/_/    \_\_|  |______\_____|  |_|  \____/|_____/
#
#------------------------------------------------------------------

#------------------------------------------------------------------


@app.route('/crearviaje', methods=['POST', 'GET'])
def crearViaje():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if request.method == 'GET':
            return render_template('crearViaje.html')
        else:
            usuario = Usuarios.find_one({"username": session["username"]})
            conductor = ObjectId(usuario['_id'])
            origenstr = request.form['origen']
            destinostr = request.form['destino']
            horasalida = request.form['horasalida']
            d_horasalida = datetime.strptime(horasalida, '%Y-%m-%dT%H:%M')
            precio = request.form['precio']
            numeropasajeros = request.form['numeropasajeros']
            finalizado = 0
            pasajeros = []
            origen = {
                'type':
                "Point",
                'coordinates':
                [float(getLatitud(origenstr)),
                float(getLongitud(origenstr))]
            }
            destino = {
                'type':
                "Point",
                'coordinates':
                [float(getLatitud(destinostr)),
                float(getLongitud(destinostr))]
            }
            if origenstr == destinostr:
                error = "Error: origen y destino iguales"
                return render_template('crearViaje.html',
                                    error=error,
                                    origen=origenstr,
                                    destino=destinostr,
                                    horasalida=horasalida,
                                    precio=precio,
                                    numeropasajeros=numeropasajeros)
            else:
                id = Trayectos.insert({
                    'conductor': conductor,
                    'origenstr': origenstr,
                    'origen': origen,
                    'destinostr': destinostr,
                    'destino': destino,
                    'horasalida': d_horasalida,
                    'precio': int(precio),
                    'numeropasajeros': int(numeropasajeros),
                    'finalizado': finalizado,
                    'pasajeros': pasajeros
                })
                return redirect('/trayecto/'+str(id))


@app.route('/editarviaje/<id>', methods=['POST'])
def editarViaje(id):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        trayecto = Trayectos.find_one({'_id': ObjectId(id)})
        origenstr = request.form['origen']
        destinostr = request.form['destino']
        horasalida = request.form['horasalida']
        d_horasalida = datetime.strptime(horasalida, '%Y-%m-%dT%H:%M')
        numeropasajeros = request.form['numeropasajeros']
        precio = request.form['precio']

        origen = {
            'type':
            "Point",
            'coordinates':
            [float(getLatitud(origenstr)),
            float(getLongitud(origenstr))]
        }

        destino = {
            'type':
            "Point",
            'coordinates':
            [float(getLatitud(destinostr)),
            float(getLongitud(destinostr))]
        }
        if origenstr == destinostr:
            error = "Error: origen y destino iguales"
            return render_template('editarViaje.html',
                                error=error,
                                trayecto=trayecto)
        else:
            Trayectos.update_one({'_id': ObjectId(id)}, {
                '$set': {
                    'origenstr': origenstr,
                    'origen': origen,
                    'destinostr': destinostr,
                    'destino': destino,
                    'horasalida': d_horasalida,
                    'precio': int(precio),
                    'numeropasajeros': int(numeropasajeros)
                }
            })
        return mostrarViaje(id)



@app.route('/finalizartrayecto/<idtrayecto>', methods=['POST','GET'])
def finalizarTrayecto(idtrayecto):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        Trayectos.update_one({'_id': ObjectId(idtrayecto)},
                            {'$set': {
                                'finalizado': 1
                            }})
        return redirect('/trayecto/'+idtrayecto)

@app.route('/borrartrayecto/<id>', methods=['POST','GET'])
def borrarTrayecto(id):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        trayectos = Trayectos.delete_one({'_id': ObjectId(id)})
        return redirect('/mis_viajes_creados/'+session["username"]+'/1')



@app.route('/busqueda', methods=['POST'])
def busquedatrayecto_post():
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        origen = request.form['origen']
        localidad_origen = 'False'
        if 'mostrarlocalidadorigen' in request.form:
            localidad_origen = request.form['mostrarlocalidadorigen']
        radio_origen = request.form['radioorigen']
        destino = request.form['destino']
        localidad_destino = 'False'
        if 'mostrarlocalidaddestino' in request.form:
            localidad_destino = request.form['mostrarlocalidaddestino']
        radio_destino = request.form['radiodestino']
        horasalida = request.form['horasalida']
        #d_horasalida = datetime.strptime(horasalida, '%d/%m/%Y %H:%M')
        numeropasajeros = request.form['numeropasajeros']
        return redirect('/busqueda/' + origen + '/' + localidad_origen + '/' +
                        radio_origen + '/' + destino + '/' + localidad_destino +
                        '/' + radio_destino + '/' + horasalida + '/' +
                        numeropasajeros + '/1')


@app.route('/busqueda/<origen>/<mostrarlocalidadorigen>/<radioorigen>/<destino>/<mostrarlocalidaddestino>/<radiodestino>/<horasalida>/<numpasajeros>/<pagina>', methods=['GET'])
def busquedatrayecto_get(origen, mostrarlocalidadorigen, radioorigen, destino,
                         mostrarlocalidaddestino, radiodestino, horasalida,
                         numpasajeros, pagina):
    loc_origen = bool(mostrarlocalidadorigen)
    loc_destino = bool(mostrarlocalidaddestino)
    d_horasalida = datetime.strptime(horasalida, '%Y-%m-%d')
    d_horasalida_sup = d_horasalida + timedelta(days=1)
    if not 'username' in session:
        if loc_origen:
            trayectos_proximos_origen = []
            tray1 = Trayectos.find({
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                }
            }).sort('horasalida', 1)
            loc = localidad(getLatitud(origen), getLongitud(origen))
            for doc in tray1:
                l = localidad(doc['origen']['coordinates'][0],
                              doc['origen']['coordinates'][1])
                if loc == l:
                    trayectos_proximos_origen.append(doc)
        else:
            trayectos_proximos_origen = Trayectos.find({
                'origen': {
                    '$near': {
                        '$geometry': {
                            'type':
                            "Point",
                            'coordinates': [
                                float(getLatitud(origen)),
                                float(getLongitud(origen))
                            ]
                        },
                        '$maxDistance': int(radioorigen)
                    }
                },
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                }
            }).sort('horasalida', 1)

        if loc_destino:
            trayectos_proximos_destino = []
            tray2 = Trayectos.find({
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                }
            }).sort('horasalida', 1)
            loc = localidad(getLatitud(destino), getLongitud(destino))
            for doc in tray2:
                l = localidad(doc['destino']['coordinates'][0],
                              doc['destino']['coordinates'][1])
                if loc == l:
                    trayectos_proximos_destino.append(doc)
        else:
            trayectos_proximos_destino = Trayectos.find({
                'destino': {
                    '$near': {
                        '$geometry': {
                            'type':
                            "Point",
                            'coordinates': [
                                float(getLatitud(destino)),
                                float(getLongitud(destino))
                            ]
                        },
                        '$maxDistance': int(radiodestino)
                    }
                },
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                }
            }).sort('horasalida', 1)

    else:
        user = Usuarios.find_one({'username': session['username']})
        if loc_origen:
            trayectos_proximos_origen = []
            tray1 = Trayectos.find({
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                },
                'conductor': {
                    '$ne': user['_id']
                },
                'pasajeros': {
                    '$not': {
                        '$elemMatch': {
                            'comprador': user['_id']
                        }
                    }
                }
            }).sort('horasalida', 1)
            loc = localidad(getLatitud(origen), getLongitud(origen))
            for doc in tray1:
                l = localidad(doc['origen']['coordinates'][0],
                              doc['origen']['coordinates'][1])
                if loc == l:
                    trayectos_proximos_origen.append(doc)
        else:
            trayectos_proximos_origen = Trayectos.find({
                'origen': {
                    '$near': {
                        '$geometry': {
                            'type':
                            "Point",
                            'coordinates': [
                                float(getLatitud(origen)),
                                float(getLongitud(origen))
                            ]
                        },
                        '$maxDistance': int(radioorigen)
                    }
                },
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                },
                'conductor': {
                    '$ne': user['_id']
                },
                'pasajeros': {
                    '$not': {
                        '$elemMatch': {
                            'comprador': user['_id']
                        }
                    }
                }
            }).sort('horasalida', 1)

        if loc_destino:
            trayectos_proximos_destino = []
            tray2 = Trayectos.find({
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                },
                'conductor': {
                    '$ne': user['_id']
                },
                'pasajeros': {
                    '$not': {
                        '$elemMatch': {
                            'comprador': user['_id']
                        }
                    }
                }
            }).sort('horasalida', 1)
            loc = localidad(getLatitud(destino), getLongitud(destino))
            for doc in tray2:
                l = localidad(doc['destino']['coordinates'][0],
                              doc['destino']['coordinates'][1])
                if loc == l:
                    trayectos_proximos_destino.append(doc)
        else:
            trayectos_proximos_destino = Trayectos.find({
                'destino': {
                    '$near': {
                        '$geometry': {
                            'type':
                            "Point",
                            'coordinates': [
                                float(getLatitud(destino)),
                                float(getLongitud(destino))
                            ]
                        },
                        '$maxDistance': int(radiodestino)
                    }
                },
                'horasalida': {
                    '$gte': d_horasalida,
                    '$lt': d_horasalida_sup
                },
                'numeropasajeros': {
                    '$gte': int(numpasajeros)
                },
                'conductor': {
                    '$ne': user['_id']
                },
                'pasajeros': {
                    '$not': {
                        '$elemMatch': {
                            'comprador': user['_id']
                        }
                    }
                }
            }).sort('horasalida', 1)

    num_tray = 0
    trayectos = []
    for doc in trayectos_proximos_origen:
        if (doc in trayectos_proximos_destino and doc['finalizado'] == 0):
            trayectos.append({
                '_id': str(ObjectId(doc['_id'])),
                'origen': doc['origenstr'],
                'destino': doc['destinostr'],
                'horasalida': doc['horasalida'],
                'precio': doc['precio'],
                'numeropasajeros': doc['numeropasajeros']
            })
            num_tray += 1
    trayectos = trayectos[7 * (int(pagina) - 1):7 * (int(pagina))]
    datos = {
        'origen': origen,
        'destino': destino,
        'horasalida': horasalida,
        'numpasajeros': numpasajeros,
        'pagina': int(pagina),
        'ultimaPag': int((num_tray - 1) // 7),
        'encontrado': True
    }
    if not trayectos:
        datos['encontrado'] = False
    return render_template('busqueda.html', datos=datos, trayectos=trayectos)


@app.route('/trayecto/<id>', methods=['GET'])
def mostrarViaje(id):
    user = None
    trayecto = Trayectos.find_one({'_id': ObjectId(id)})
    pasajeros = trayecto['pasajeros']
    espasajero = False
    if session.get('username') is not None:
        user = Usuarios.find_one({'username': session['username']})
        
        for p in pasajeros:
                if p['comprador'] == user['_id']:
                    espasajero = True

    
    conductor = Usuarios.find_one({'_id': ObjectId(trayecto['conductor'])})
    
    pasajerosPerfil = []

    if pasajeros:
        for pas in pasajeros:
            usuario = Usuarios.find_one({'_id': ObjectId(pas['comprador'])})
            pasajerosPerfil.append(usuario)

    


    duracionViaje = duracion(origen=trayecto['origenstr'],
                             destino=trayecto['destinostr'])

    if(user):
        if user['_id'] == trayecto['conductor'] :
            pasval = []
            for p in pasajeros:
                esta = Valoraciones.find_one({'valorador': ObjectId(user['_id']),'trayecto': ObjectId(id),'valorado': ObjectId(p['comprador'])})
                pasval.append({
                'viajero': p['comprador'],
                'estavalorado': esta
            }) 
                
                
            return render_template('viaje.html',
                            trayecto=trayecto,
                            conductor=conductor,
                            pasajeros=pasajerosPerfil,
                            duracion=duracionViaje,
                            fechahoy=datetime.now(),
                            espasajero=espasajero,
                            viajerosvalorados=pasval,
                             tiempo=daily(trayecto['destinostr']))
        else :

            puedeCrear = (user['paypal'] != "") and (user['dni'] != "")  and (user['telefono'] != "")
          
            condval = Valoraciones.find_one({'valorador': ObjectId(user['_id']),'trayecto': ObjectId(id),'valorado': ObjectId(trayecto['conductor'])}) != None
            return render_template('viaje.html',
                            trayecto=trayecto,
                            conductor=conductor,
                            pasajeros=pasajerosPerfil,
                            duracion=duracionViaje,
                            fechahoy=datetime.now(),
                            espasajero=espasajero,
                            conductorvalorado=condval,
                            puedeCrear=puedeCrear,
                            tiempo=daily(trayecto['destinostr']))
    else:
        return render_template('viaje.html',
                           trayecto=trayecto,
                           conductor=conductor,
                           pasajeros=pasajerosPerfil,
                           duracion=duracionViaje,
                           fechahoy=datetime.now(),
                            tiempo=daily(trayecto['destinostr']))


@app.route('/anadirpasajero/<idtrayecto>/<numreservas>', methods=['GET', 'POST'])
def anadirPasajero(idtrayecto,numreservas):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
        usuario = Usuarios.find_one({"username": session["username"]})

        numpasajeros = trayecto['numeropasajeros']
        conductor = trayecto['conductor']
        pasajeros = trayecto['pasajeros']
        asientos = numreservas

        pasajeros.append({'comprador' : ObjectId(usuario['_id']), 'personas': int(asientos) })

        Trayectos.update({'_id': ObjectId(idtrayecto)}, {
            '$set': {
                'pasajeros': pasajeros,
                'numeropasajeros': numpasajeros - int(asientos)
            }
        })

        return redirect('/trayecto/'+idtrayecto)




@app.route('/mis_viajes/<usuario>', methods=['GET'])
def mis_viajes_1(usuario):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        return redirect('/mis_viajes/' + usuario + '/' + str(1))


@app.route('/mis_viajes/<usuario>/<pagina>', methods=['GET'])
def mis_viajes(usuario, pagina):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if not 'username' in session or usuario != session['username']:
            return not_access_permission()
        
        id_usuario = Usuarios.find_one({'username': usuario})['_id']

        tray = Trayectos.find({
            'pasajeros': {
                '$elemMatch': {
                    'comprador': id_usuario
                }
            }
        }).sort('horasalida', 1)[7 * (int(pagina) - 1):7 * (int(pagina))]

        num_tray = Trayectos.count_documents({
            'pasajeros': {
                '$elemMatch': {
                    'comprador': id_usuario
                }
            }
        })

        datos = {
            'pagina': int(pagina),
            'ultimaPag': int((num_tray - 1) // 7),
            'encontrado': True
        }
        trayectos = []

        for doc in tray:
            trayectos.append({
                '_id': str(ObjectId(doc['_id'])),
                'origenstr': doc['origenstr'],
                'destinostr': doc['destinostr'],
                'horasalida': doc['horasalida'],
                'precio': doc['precio'],
                'numeropasajeros': doc['numeropasajeros']
            })
        if not trayectos:
            datos['encontrado'] = False
        return render_template('misViajes.html', datos=datos, trayectos=trayectos)


@app.route('/mis_viajes_creados/<usuario>/<pagina>', methods=['GET'])
def mis_viajes_creados(usuario, pagina):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if not 'username' in session or usuario != session['username']:
            return not_access_permission()
        
        
        id_usuario = Usuarios.find_one({'username': usuario})['_id']
        tray = Trayectos.find({
            'conductor': id_usuario
        }).sort('horasalida', 1)[7 * (int(pagina) - 1):7 * (int(pagina))]

        num_tray = Trayectos.count_documents({
            'conductor': id_usuario
        })

        datos = {
            'pagina': int(pagina),
            'ultimaPag': int((num_tray - 1) // 7),
            'encontrado': True
        }
        trayectos = []
        for doc in tray:
            trayectos.append({
                '_id': str(ObjectId(doc['_id'])),
                'origenstr': doc['origenstr'],
                'destinostr': doc['destinostr'],
                'horasalida': doc['horasalida'],
                'precio': doc['precio'],
                'numeropasajeros': doc['numeropasajeros']
            })
        if not trayectos:
            datos['encontrado'] = False
        return render_template('misViajesCreados.html',
                            datos=datos,
                            trayectos=trayectos)




@app.route('/mostrar_editar_trayecto/<idtrayecto>', methods=['GET'])
def mostrar_editar_trayecto(idtrayecto):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
        return render_template('editarViaje.html', trayecto=trayecto)


@app.route('/salir_trayecto/<usuario>/<idtrayecto>', methods=['GET'])
def salir_trayecto(usuario, idtrayecto):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if usuario != session['username']:
            return not_access_permission()
        
        idusuario = Usuarios.find_one({'username': usuario})['_id']
        trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
        for pas in trayecto['pasajeros']:
            if pas['comprador'] == ObjectId(idusuario):
                num_pasajeros = pas['personas']
        Trayectos.update({'_id': ObjectId(idtrayecto)}, { '$set': { 'numeropasajeros': trayecto['numeropasajeros'] + num_pasajeros } })
        Trayectos.update({'_id': ObjectId(idtrayecto)}, {
                '$pull': {
                    'pasajeros': { 'comprador': ObjectId(idusuario) } }
        })

        return redirect('/mis_viajes/' + usuario + '/' + str(1))
    

#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# __      __     _      ____  _____            _____ _____ ____  _   _ ______  _____
# \ \    / /\   | |    / __ \|  __ \     /\   / ____|_   _/ __ \| \ | |  ____|/ ____|
#  \ \  / /  \  | |   | |  | | |__) |   /  \ | |      | || |  | |  \| | |__  | (___
#   \ \/ / /\ \ | |   | |  | |  _  /   / /\ \| |      | || |  | | . ` |  __|  \___ \
#    \  / ____ \| |___| |__| | | \ \  / ____ \ |____ _| || |__| | |\  | |____ ____) |
#     \/_/    \_\______\____/|_|  \_\/_/    \_\_____|_____\____/|_| \_|______|_____/
#
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------



@app.route('/valorar/<idtrayecto>/<idusuario>', methods=['GET', 'POST'])
def valorar(idtrayecto, idusuario):
    if comprobarToken() == 0 :
        return redirect("/")
    else:
        if request.method == 'GET':
            username = session["username"]
            usuarioact = Usuarios.find_one({"username": username})
            trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
            usuariovalorado = Usuarios.find_one({'_id': ObjectId(idusuario)})
            return render_template('valorar.html',
                                usuario=usuariovalorado,
                                trayecto=trayecto,
                                usuarioact=usuarioact)
        else:
            username = session["username"]
            usuarioact = Usuarios.find_one({"username": username})
            trayecto = Trayectos.find_one({'_id': ObjectId(idtrayecto)})
            usuariovalorado = Usuarios.find_one({'_id': ObjectId(idusuario)})
            valoracion = request.form['valoracion']
            comentario = request.form['comentario']

            Valoraciones.insert({
                'valorado': usuariovalorado['_id'],
                'trayecto': trayecto['_id'],
                'valorador': usuarioact['_id'],
                'puntuacion': int(valoracion),
                'comentario': comentario
            })
            return redirect('/perfilId/' + str(usuariovalorado["_id"])
                            ) 


def estavalorado(conductor, usuario):
    v = Valoraciones.find_one({
        'valorado': conductor['_id'],
        'valorador': usuario['_id']
    })
    print(v)
    print(conductor['_id'])
    print(usuario['_id'])
    if v == None:
        return False
    else:
        return True



def media_valoraciones(id):
    valoraciones = Valoraciones.find({"valorado": ObjectId(id)})
    total = 0
    suma = 0

    for val in valoraciones:
        suma += val['puntuacion']
        total += 1

    if total == 0:
        return 0
    else:
        media = suma / total
        return round(media, 1)


def num_valoraciones(id):
    valoraciones = Valoraciones.find({"valorado": ObjectId(id)})
    total = 0
    for val in valoraciones:
        total += 1

    return total

#------------------------------------------------------------------

#------------------------------------------------------------------
#           _____ _____      __  __          _____   _____
#     /\   |  __ \_   _|    |  \/  |   /\   |  __ \ / ____|
#    /  \  | |__) || |      | \  / |  /  \  | |__) | (___
#   / /\ \ |  ___/ | |      | |\/| | / /\ \ |  ___/ \___ \
#  / ____ \| |    _| |_     | |  | |/ ____ \| |     ____) |
# /_/    \_\_|   |_____|    |_|  |_/_/    \_\_|    |_____/
#------------------------------------------------------------------

#------------------------------------------------------------------

@app.route('/buscagasolineras/<locationdata>', methods=['GET'])
def buscagasolineras(locationdata):
    # place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    # url = place_api_url + urllib.parse.urlencode({"input":locationdata,"inputtype":'textquery',"fields":'geometry', "key":API_KEY_MAPS})
    # json_data_place = requests.get(url).json()
    latitud = str(getLatitud(locationdata))
    longitud = str(getLongitud(locationdata))

    #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522%2C151.1957362&radius=1500&type=restaurant&keyword=cruise&key=AIzaSyDznNAUPqKZhq9Czvpzq3Nl8ppJOd0L_XI"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + latitud + "%2C" + longitud + "&radius=1000&type=gas_station&key=AIzaSyDznNAUPqKZhq9Czvpzq3Nl8ppJOd0L_XI"
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.text)


def getLatitud(lugar):
    place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    url = place_api_url + urllib.parse.urlencode({
        "input": lugar,
        "inputtype": 'textquery',
        "fields": 'geometry',
        "key": API_KEY_MAPS
    })
    json_data_place = requests.get(url).json()
    latitud = str(
        json_data_place['candidates'][0]['geometry']['location']['lat'])
    return latitud


def getLongitud(lugar):
    place_api_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    url = place_api_url + urllib.parse.urlencode({
        "input": lugar,
        "inputtype": 'textquery',
        "fields": 'geometry',
        "key": API_KEY_MAPS
    })
    json_data_place = requests.get(url).json()
    longitud = str(
        json_data_place['candidates'][0]['geometry']['location']['lng'])
    return longitud


@app.route('/inforuta/<origen>/<destino>', methods=['GET']
           )  # principal para consultas en maps teniendo origen y destino
def ruta(origen, destino):  # devuelve el json con toda la informacion
    directions_api_url = "https://maps.googleapis.com/maps/api/directions/json?"
    url = directions_api_url + urllib.parse.urlencode({
        "origin": origen,
        "destination": destino,
        "language": "es",
        "key": API_KEY_MAPS
    })
    json_data = requests.get(url).json()

    return json_data


@app.route('/distancia/<origen>/<destino>', methods=['GET'])
def distancia(origen, destino):  # devuelve la distancia entre origen y destino
    json_data = ruta(origen, destino)
    distancia = json_data['routes'][0]['legs'][0]['distance'][
        'text']  #hay que controlar el error por si no encuentra ruta
    return distancia


@app.route('/duracion/<origen>/<destino>', methods=['GET'])
def duracion(origen, destino):  # devuelve la duracion entre origen y destino
    json_data = ruta(origen, destino)
    duracion = json_data['routes'][0]['legs'][0]['duration'][
        'text']  #hay que controlar el error por si no encuentra ruta
    return duracion


@app.route('/localidad/<lat>/<lon>', methods=['GET'])
def localidad(lat, lon):
    directions_api_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    url = directions_api_url + urllib.parse.urlencode(
        {
            "latlng": str(lat) + ',' + str(lon),
            "sensor": "false",
            "language": "es",
            "key": API_KEY_MAPS
        })
    json_data = requests.get(url).json()
    for r in json_data['results']:
        if r['types'][0] == 'locality':
            return r['place_id']
    return None


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
    url = tiempo_url + urllib.parse.urlencode({
        "lat": getLatitud(lugar),
        "lon": getLongitud(lugar),
        "appid": API_KEY_TIEMPO
    })
    json_data = requests.get(url).json()
    return json_data

@app.route('/daily/<lugar>', methods=['GET'])
def daily(lugar):
    json_data_lugar = infotiempo(lugar)
    list = json_data_lugar['daily']
    tempmaxlist=[]
    tempminlist=[]
    weatherlist=[]
    iconlist=[]
    data=[]
    timelist=[]
    for i in list:
        tempmaxlist.append(round((i['temp']['max']-273.15),1))
        tempminlist.append(round((i['temp']['min']-273.15),1))
        weatherlist.append(i['weather'][0]['description'])
        iconlist.append(i['weather'][0]['icon'])
        timelist.append(datetime.utcfromtimestamp(int(i['dt'])).strftime('%d-%m-%Y')     )
    data.append(tempmaxlist)
    data.append(tempminlist)
    data.append(weatherlist)
    data.append(iconlist)
    data.append(timelist)
    return (data)


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


@app.errorhandler(403)
def not_access_permission(error=None):
    response = jsonify({
        'mensaje': 'No tiene acceso al recurso ' + request.url,
        'Status': 403
    })
    response.status = 403
    return response

def comprobarToken():
    try:
        if session.get('token') is not None:
            idtoken=session['token']
            CLIENT_ID = '195417323379-cfskdhqvf71gkoajilafthirmlvgt3da.apps.googleusercontent.com'
            try:
                id_token.verify_oauth2_token(idtoken, requests.Request(), CLIENT_ID,10)
            except ValueError:
                return 0
        else: 
            return 1
    except KeyError :
        return 0
    return 1

if __name__ == '__main__':
    app.run( debug=True)
    
    
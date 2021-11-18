from bson.objectid import ObjectId
from flask import Flask, json ,request ,jsonify
from flask_pymongo import PyMongo
from flask import render_template
from pymongo import mongo_client
from werkzeug.utils import redirect


app = Flask (__name__)
app.config["MONGO_URI"] = "mongodb+srv://CarHubAdmin:1234@carhub.n2ouf.mongodb.net/CarHubDB?retryWrites=true&w=majority"

mongo = PyMongo(app)

db = mongo.db.Users

@app.route('/create')
def create():
    return render_template('home/create.html')

@app.route('/edit/<id>')
def edit(id):
    user = db.find_one({'_id': ObjectId(id)})
    return render_template('home/edit.html', user = user )

@app.route('/users' , methods = ['POST'])
def CreateUser():
    _name = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _password = request.form['txtPassword']

    id = db.insert({
        'name': _name,
        'email': _correo,
        'password': _password,
    })
    return render_template('home/index.html')
    

@app.route('/users' , methods = ['GET'])
def GetUsers():
    users = []
    for doc in db.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'email': doc['email'],
            'password': doc['password']
        })

    return render_template('/home/list.html', users=users)
    
@app.route('/delete/<id>' , methods = ['GET'])
def DeleteUser(id):
    db.delete_one({'_id': ObjectId(id)})
    return redirect('/')

@app.route('/users/<id>' , methods = ['POST'])
def UpdateUser(id):
    _name = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _password = request.form['txtPassword']

    db.update_one({'_id': ObjectId(id)},{'$set':{
        'name': _name,
        'email': _correo,
        'password': _password
    }})
    return GetUsers()

@app.route('/')
def index():
    return render_template('home/index.html')
    

if __name__ == '__main__':
    app.run(debug=True)
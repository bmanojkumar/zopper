#!zopper/bin/python
from flask import Flask,request,jsonify,render_template,Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask.ext.cors import CORS
from flask.ext.cache import Cache
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


#initiaze Flask
app = Flask(__name__)
#Connecting to database
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zopper:zopper@localhost/postgres'
db = SQLAlchemy(app)  #initialize SQLAlchemy
cors = CORS(app)    #enable Cross origin requests
cache = Cache(app,config={'CACHE_TYPE': 'simple'}) #used for cacheing requests
admin = Admin(app) #for admin panel "/admin"

#the ORM model
class Sighting(db.Model):
  __tablename__ = 'devices'
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.Text)
  trange = db.Column(db.Integer)

  def __init__(self, name, trange):
        self.name = name
        self.trange = trange


db.create_all()
db.session.commit()

admin.add_view(ModelView(Sighting, db.session))

#home route
@app.route('/')
def index():
	return render_template('home.html')

#benchmark route
@app.route('/benchmark')
def bench():
	return render_template('benchmark.html')

#birds eye view
@app.route('/birdseyeview/<int:page>',methods=['GET'])
def birdseye(page):
	end = page*10;  #start index
	start = end - 9; #end index
	row_num = db.session.query(Sighting).count()

	if row_num < end:	# for last page, to avoid overflow
		end = row_num

	sql = text('SELECT name,trange from devices where id >= :s AND id <= :e')
	results = db.engine.execute(sql,s=start,e=end)

	# total no of pages, in which we can fit the rows
	r = int(row_num)/10
	if row_num%10 != 0:
		r = r+1

	return render_template('birdseyeview.html',db_results = results,rows = str(row_num), count = r)


#delete API
@app.route('/api/devices/delete',methods=['DELETE'])
#@cache.cached(timeout=50)
def dDev():
	if (request.method == 'DELETE'):
		if not (request.form.get('trange') is None): 
			m = request.form.get('trange')

			try:

				sql = text('DELETE from devices where trange = :f')
				results = db.engine.execute(sql,f=m)
				return jsonify(status={"success" : "Delete successfull"})
			except:
				return jsonify(status={"err" : "Unable to delete."})
		return jsonify(status={"err" : "Unable to delete."})
	return jsonify(status={"err" : "Not a delete,request"})


@app.route('/api/devices/add',methods=['POST'])
def getDevicesk():
	if (request.method == 'POST'):
		if not (request.form.get('fname') is None and request.form.get('trange') is None): 
			f = request.form.get('fname')
			t = request.form.get('trange')
			dev = Sighting(f, t)
			try:

				db.session.add(dev)
				db.session.commit()
			except:
				return jsonify(success=True)

			return jsonify(success=True)
	return jsonify(success=True)	



@app.route('/api/devices/update',methods=['PUT'])
def pDev():
	if (request.method == 'PUT'):
		if not (request.form.get('fname') is None and request.form.get('trange') is None): 
			g = request.form.get('fname')
			f = request.form.get('trange')
			try:

				sql = text('UPDATE devices SET trange = :f where name = :g')
				results = db.engine.execute(sql,f=f,g=g)
			except:
				return jsonify(error={"err" : "Unable to update failed"})

			return jsonify(status={"success" : "Update successfull"})
	return jsonify(error={"err" : "Unable to Update,not a put request"})	

	
	
@app.route('/api/devices/namesearch',methods=['GET','POST'])
def getDevicesname():
	if (request.method == 'GET'):
		if not request.args.get('fname') is None:
				n = request.args.get('fname')
				sql = text('SELECT name,trange from devices where name LIKE :st') 
				results = db.engine.execute(sql,st="%"+n+"%")

				json_results = []
				for result in results:
					d = {'Name':result.name,'Range':result.trange}
					json_results.append(d)

			
				return jsonify(items=json_results)


@app.route('/api/devices/range',methods=['GET','POST'])
def getDevices():
	if (request.method == 'GET'):
		if not (request.args.get('from') is None and request.args.get('to') is None): 
			f = request.args.get('from')
			t = request.args.get('to')
			sql = text('SELECT name from devices where trange >= :f AND trange <= :t')
			results = db.engine.execute(sql,f=f,t=t)

			json_results = []
			for result in results:
				d = {'Name':result.name}
				json_results.append(d)

			return jsonify(items=json_results)

@app.route('/api/devices/<int:device_id>',methods=['GET'])
def getDevice(device_id):
	if request.method == 'GET':
		results = Sighting.query.filter_by(id=device_id).all()

		json_results = []
		for result in results:
			d = {'Name':result.name,'Range':result.trange}
			json_results.append(d)

		return jsonify(items=json_results)

if __name__ == '__main__':
	app.run(debug=True)

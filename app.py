#!zopper/bin/python
from flask import Flask,request,jsonify,render_template,Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask.ext.cors import CORS
from flask.ext.cache import Cache
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zopper:zopper@localhost/postgres'
db = SQLAlchemy(app)
cors = CORS(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
admin = Admin(app)


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

@app.route('/')
def index():
	return render_template('home.html')


@app.route('/benchmark')
def bench():
	return render_template('benchmark.html')

@app.route('/birdseyeview/<int:page>',methods=['GET'])
def birdseye(page):
	end = page*10;
	start = end - 9;

	#sql = text('SELECT COUNT(*) from devices')
	#rown = db.engine.execute(sql)
	#row_num = rown.rowcount
	row_num = db.session.query(Sighting).count()
	#print "**************************************8"
	#print rown.rowcount

	if row_num < end:
		end = row_num

	sql = text('SELECT name,trange from devices where id >= :s AND id <= :e')
	results = db.engine.execute(sql,s=start,e=end)

	r = int(row_num)/10
	if row_num%10 != 0:
		r = r+1

	return render_template('birdseyeview.html',db_results = results,rows = str(row_num), count = r)


	


#ok
@app.route('/api/devices/delete',methods=['DELETE'])
#@cache.cached(timeout=50)
def dDev():
	if (request.method == 'DELETE'):
		if not (request.form.get('trange') is None): 
			m = request.form.get('trange')

			try:

				sql = text('DELETE from devices where trange = :f')
		#			query = "SELECT name from devices where trange >= 600 AND trange <= 800" 
		#			results = Sighting.query.from_statement(query).all()
				results = db.engine.execute(sql,f=m)
				return jsonify(status={"success" : "Delete successfull"})
			except:
				return jsonify(status={"err" : "Unable to delete."})
		return jsonify(status={"err" : "Unable to delete."})
	return jsonify(status={"err" : "Not a delete,request"})



# @app.route('/api/devices/temp/add',methods=['POST'])
# def cDev():

# 	if not request.json or not 'fname' in request.json or not 'trange' in request.json:
# 		return jsonify(error={"err" : "Unable to insert."})

# 	n = request.json['fname']
# 	m = request.json['trange']

# 	dev = Sighting(n, m)
# 	try:

# 		db.session.add(dev)
# 		db.session.commit()
# 	except:
# 		return jsonify(error={"err" : "Unable to insert."})

# 	return jsonify(status={"success" : "Insert successfull"})
	

#ok ok
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



#not ok
@app.route('/api/devices/update',methods=['PUT'])
#@cache.cached(timeout=50,key_prefix="update")
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

	
	


#OK
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


#OK
@app.route('/api/devices/range',methods=['GET','POST'])
def getDevices():
	if (request.method == 'GET'):
		if not (request.args.get('from') is None and request.args.get('to') is None): 
			f = request.args.get('from')
			t = request.args.get('to')
			sql = text('SELECT name from devices where trange >= :f AND trange <= :t')
#			query = "SELECT name from devices where trange >= 600 AND trange <= 800" 
#			results = Sighting.query.from_statement(query).all()
			results = db.engine.execute(sql,f=f,t=t)

			json_results = []
			for result in results:
				d = {'Name':result.name}
				json_results.append(d)

			return jsonify(items=json_results)





#OK
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

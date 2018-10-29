import json, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import render_template, url_for, flash, redirect

# bootstrap the database
if 'VCAP_SERVICES' in os.environ:
    services = json.loads(os.getenv('VCAP_SERVICES'))
    mysql_env = services['p.mysql'][0]['credentials']
    sqluri = mysql_env['uri']
    sqluri = sqluri[:5] + '+pymysql' + sqluri[5:]
else:
    mysql_env = dict(sqlhost='localhost', sqlport='3306', sqluser='redacted', sqluserpw='redacted', sqluri='mysql+pymysql://redacted:redacted@localhost:3306/mysql')
    sqluri = mysql_env['sqluri']

# bootstrap the app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = sqluri
db = SQLAlchemy(app)
ma = Marshmallow(app)

# define table
class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(120), unique=False, nullable=False)

class SampleSchema(ma.ModelSchema):
    class Meta:
        model = Sample

db.create_all()

#commit fake data
new_message = Sample(message="hello world")
db.session.add(new_message)
db.session.commit() 
 
# set the port dynamically with a default of 80 for local development
port = int(os.getenv('PORT', '80'))

@app.route('/')
@app.route('/index')
def index():
    searcher = Sample.query.first()
    searcherSchema = SampleSchema()
    output = searcherSchema.dump(searcher).data
    return render_template('index.html', message=output)

# start the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
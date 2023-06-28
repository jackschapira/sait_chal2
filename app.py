from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from base64 import b64encode

from flask import Markup


# initilise flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'SECRET_KEY'

# Custom Jinja2 filter for base64 decoding
def b64decode(value):
    try:
        decoded_value = base64.b64decode(value).decode('utf-8')
        return Markup(decoded_value)
    except:
        return value
# Register the custom filter
app.jinja_env.filters['b64decode'] = b64decode


# Load equipment data from CSV
global equipment_data
equipment_data = pd.read_csv('kit_info.csv', header=0)
equipment_data['mgrs'] = ''
equipment_data['mobile'] = True
equipment_data['online'] = True
equipment_data['tampered'] = False
equipment_data['battery'] = np.nan
equipment_data['payload'] = None

# Set up base index page
@app.route('/')
def Index():
    print (equipment_data)
    return render_template('index.html', columns=[c.title() for c in list(equipment_data.columns)], 
                           equipment_data=list(equipment_data.itertuples(index=False, name=None)))

# route for adding new equipment
@app.route('/insert', methods=['POST'])
def insert():
    global equipment_data
    if request.method == 'POST':
        # check if payload provided
        payload = None
        if 'type' in request.form and request.form['type'] == 'camera':
            payload = request.form.get('payload')
        if payload is not None:
            # decode payload as byte string
            #payload = b64encode(payload).decode('utf-8')
            payload = base64.b64encode(payload).decode('utf-8')


        new_equip = pd.Series([request.form['serial'], request.form['type'], request.form['model'],
                               request.form['op'], request.form['deployed'], request.form['description'],
                               request.form['location'], request.form['mgrs'], bool(request.form['mobile']),
                               bool(request.form['online']), bool(request.form['tampered']), request.form['battery'], 
                               payload], index=equipment_data.columns)
        equipment_data = equipment_data.append(new_equip, ignore_index=True)

        #flash("Equipment added successfully")
        return redirect(url_for('Index'))

# route for updating existing equipment
@app.route('/update', methods=['GET','POST'])
def update():
    if request.method == 'POST':
        # check if payload provided
        payload = None
        if 'type' in request.form and request.form['type'] == 'camera':
            payload = request.form.get('payload')
        if payload is not None:
            # encode payload as byte string
            #payload = payload.encode('utf-8')
            #payload = b64encode(payload).decode('utf-8')
            payload = base64.b64encode(payload).decode('utf-8')


        upd_equip = pd.Series([request.form['serial'], request.form['type'], request.form['model'],
                               request.form['op'], request.form['deployed'], request.form['description'],
                               request.form['location'], request.form['mgrs'], bool(request.form['mobile']),
                               bool(request.form['online']), bool(request.form['tampered']), request.form['battery'], 
                               payload], index=equipment_data.columns)
        equipment_data.iloc[equipment_data.serial==request.form['serial'], :] = upd_equip
        return redirect(url_for('Index'))
    
# route for deleting specified entry
@app.route('/delete/<serial>', methods=['GET','POST'])
def delete(serial):
    global equipment_data
    equipment_data = equipment_data[equipment_data.serial != serial].reset_index(drop=True)
    return redirect(url_for('Index'))

# route for receiving incoming broadcasts
@app.route('/device_rx', methods=['POST'])
def receive_data():
    global equipment_data
    data = request.json
    rec_equip = pd.Series(data)
    if rec_equip[0] in equipment_data.serial.values: # check if the equipment already in database
        equipment_data.iloc[equipment_data.serial==rec_equip[0], :] = rec_equip
    else:
        equipment_data = equipment_data.append(rec_equip, ignore_index=True)
    return redirect(url_for('Index'))

if __name__ == "__main__":
    app.run(host='localhost', port=8000, debug=True)

    
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import click
import pandas as pd
import os
from os.path import join, dirname, realpath
from collections import OrderedDict


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="100900",
  database="test-toppan"
)

# Create user on command line
@app.cli.command("create-user")
@click.option("--username", prompt="Enter username")
@click.option("--password", prompt="Enter password", hide_input=True, confirmation_prompt=True)
def create_user(username, password):
    try:
        cursor = mydb.cursor()
        assert username != '', "Username must not be empty" 
        assert len(password) >= 8, "Password must be at least 8 characters long"
        cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
        users = cursor.fetchone()
        if users:
            print('Account already exists!')
            pass
        else: 
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mydb.commit()
            cursor.close()
            mydb.close()
            print('You have successfully created user: ',username)
    except Exception as e:
        print(f"Error: {e}")

# Define routes and views
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
        account = cursor.fetchone()
        pw = account["password"]
        if account and check_password_hash(pw, password):
            session['loggedin'] = True
            session['username'] = account['username']
            message = 'Logged in successfully!'
            return redirect(url_for('main'))
        else:
            message = 'Incorrect username or password, please try again.'
    return render_template('index.html', message=message)

@app.route('/login/logout')
def logout():    
   # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'loggedin' in session:
        return render_template('main.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def uplaodFiles():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            # set the file path
            uploaded_file.save(file_path)
            message = parseCSV(file_path)
            # save the file
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM computer_list")
            data = cursor.fetchall()
            print(data[0])
            return {'data':data, 'message':message}
    return None

def parseCSV(filePath):
    # Use Pandas to parse the CSV file
    csvData = pd.read_csv(filePath, header=0)
    cursor = mydb.cursor()
    #  Loop through the Rows
    for i,row in csvData.iterrows():  
        cursor.execute('SELECT * FROM computer_list WHERE serial = %s', (row['serial'], ))
        data = cursor.fetchone()
        # Check if data already exists, replace the data
        if data:
            print('Data already exists!')
            update_sql = "UPDATE computer_list SET username=%s, department=%s, license=%s, Installed=%s, brand=%s, model=%s WHERE serial=%s"
            update_values = (row['username'], row['department'], row['license'], row['Installed'], row['brand'], row['model'], row['serial'])
            cursor.execute(update_sql, update_values)
            msg = 'Data already exists, Successfully update.'
            return msg
        # Insert data into database
        else: 
            sql = "INSERT INTO computer_list (username, department, license, Installed, brand, model, serial) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            value = (row['username'],row['department'],row['license'],row['Installed'],row['brand'],row['model'],row['serial'])
            cursor.execute(sql, value)
            mydb.commit()
            msg = 'Data have been successfully imported '
            return msg

@app.route('/export', methods=['POST'])
def export_to_json():
    try:
        data_to_export = request.get_json().get('data', '')  # Use get_json() to parse JSON data
        if not data_to_export:
            return jsonify({'success': False, 'error': 'No data provided'})

        data = json.loads(data_to_export)

        formatted_data = []
        for item in data:
            formatted_item = OrderedDict([
                ("username", item[0]),
                ("department", item[1]),
                ("license", item[2]),
                ("Installed", item[3]),
                ("brand", item[4]),
                ("model", item[5]),
                ("serial", item[6])
            ])
            formatted_data.append(formatted_item)
        print('Successfully exported data')

        return jsonify({'success': True, 'message': 'Successfully exported data', 'formatted_data': formatted_data})

    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'Error decoding JSON: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
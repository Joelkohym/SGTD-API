from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_mysqldb import MySQL
from sqlalchemy import create_engine, text
import re
import requests
import json
import pygsheets
from datetime import datetime
import pandas as pd
import leafmap.foliumap as leafmap
import random
import time
import pytz 
import os
from database import load_data_from_db, new_registration, validate_login, receive_details

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']

app.secret_key = os.urandom(24)
print(f"app sercret key = {app.secret_key}")

mysql = MySQL(app)

db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(
  db_connection_string,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})


colors = [
"red","blue","green","purple","orange","darkred","lightred","beige","darkblue","darkgreen","cadetblue","darkpurple","white","pink","lightblue","lightgreen","gray","black","lightgray"
]
  
@app.route("/register", methods=['GET','POST'])
def register():
  if request.method == 'POST':
    data = request.form
    print(data)
    new_registration(data)
    return render_template('login.html')
  if request.method == 'GET':
    return render_template('register.html')
    
@app.route('/')
@app.route("/login", methods=['GET','POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    login_data = validate_login(email, password)
    print(f"Validate_login value returned = {validate_login(email, password)}")
    if len(login_data) == 5:
      id = login_data[0]
      API_KEY = login_data[1]
      pID = login_data[2]
      pitstop = login_data[3]
      gSheet = login_data[4]

      session['loggedin'] = True
      session['id'] = id
      session['email']=email
      session['participant_id']=pID
      session['pitstop_url']=pitstop
      session['api_key']=API_KEY
      session['gc']=gSheet
      
      gc = pygsheets.authorize(service_account_file=gSheet)
      msg = f"Login success for {email}, redirect"
      print(f"Login success for {email}, redirect")
      return render_template('vessel_request.html', msg=msg)
    else:
      msg = "Invalid credentials, reset login"
      print("Invalid credentials, reset login")
      return redirect(url_for('login'),msg=msg)
    # if request.data['username'] and request.data['password'] in db:
    #   user_data = load_data_from_db()
  if request.method == 'GET':
    return redirect(url_for('login'))
  
colors = [
"red","blue","green","purple","orange","darkred","lightred","beige","darkblue","darkgreen","cadetblue","darkpurple","white","pink","lightblue","lightgreen","gray","black","lightgray"
]

#========================Vessel data PULL===========================
@app.route("/api/vessel", methods=['GET', 'POST'])
def Vessel_data_pull():
  if request.method == 'POST':
    user_vessel_imo = request.form['vessel_imo']
    #Split vessel_imo list into invdivual records
    input_list = [int(x) for x in user_vessel_imo.split(',')]
    
    print(f"user_vessel_imo from html = {user_vessel_imo}")
    print(f"input_list from html = {input_list}")
    
    #Loop through input IMO list
    for vessel_imo in input_list:
      print(f"IMO Number = {vessel_imo}")
      
      url_vessel_movement = f"{session['pitstop_url']}/api/v1/data/pull/vessel_movement"
      url_vessel_current_position = f"{session['pitstop_url']}/api/v1/data/pull/vessel_current_position"
      
      payload = {
        "participants": [{
          "id": "1817878d-c468-411b-8fe1-698eca7170dd",
          "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
          "meta": {
            "data_ref_id": ""
          }
        }],
        "parameters": {
          "vessel_imo_no": str(vessel_imo)
        },
        "on_behalf_of": [{
          "id": session['participant_id']
        }]
      }
      
      json_string = json.dumps(
        payload, indent=4)  # Convert payload dictionary to JSON string
      # Rest of the code to send the JSON payload to the API
      data = json.loads(json_string)
      
    #========================PULL vessel_current_position===========================
      response_vessel_current_position = requests.post(
    url_vessel_current_position,json=data, headers={'SGTRADEX-API-KEY': session['api_key']})
      if response_vessel_current_position.status_code == 200:
        print(f"Response JSON = {response_vessel_current_position.json()}")
        print("Pull vessel_current_position success.")
      else:
        print(
          f"Failed to PULL vessel_current_position data. Status code: {response_vessel_current_position.status_code}"
        )
  
    #========================PULL vessel_movement=====================================
      response_vessel_movement = requests.post(
        url_vessel_movement, json=data, headers={'SGTRADEX-API-KEY': session['api_key']})
      if response_vessel_movement.status_code == 200:
        print("Pull vessel_movement success.")
      else:
        print(
          f"Failed to PULL vessel_movement data. Status code: {response_vessel_movement.status_code}"
        )

      
    gc = pygsheets.authorize(service_account_file=session['gc'])
    sh = gc.open('SGTD Received APIs')
    sheet1 = sh.worksheet_by_title("replit_vessel_current_position")
    #Clear gSheet
    sheet1.clear()
    print('Cleared replit_vessel_current_position')
    sheet2 = sh.worksheet_by_title('replit_vessel_movement')
    sheet2.clear()
    print('Cleared replit_vessel_movement')
    
    return redirect(url_for('Vessel_map'))
    
  return render_template('vessel_request.html')

#==========================RECEIVE vessel_movement===============================
@app.route("/api/vessel_movement/receive/admin", methods=['POST'])
def Vessel_movement_receive():
    email = "joel.koh@sgtradex.com"
    receive_details_data = receive_details(email)
    print(f"Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]

    data = request.data  # Get the raw data from the request body
    print(data)
    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    # Extract the last item from the "payload" array
    last_payload_item = data_dict['payload'][-1]
    try:
      print(f"Length of vessel movement end date = {len(last_payload_item['vm_vessel_movement_end_dt'])}")
      row_data_vessel_movement = {
      "vm_vessel_particulars.vessel_nm":
      last_payload_item['vm_vessel_particulars'][0]['vessel_nm'],
      "vm_vessel_particulars.vessel_imo_no":
      last_payload_item['vm_vessel_particulars'][0]['vessel_imo_no'],
      "vm_vessel_particulars.vessel_flag":
      last_payload_item['vm_vessel_particulars'][0]['vessel_flag'],
      "vm_vessel_particulars.vessel_call_sign":
      last_payload_item['vm_vessel_particulars'][0]['vessel_call_sign'],
      "vm_vessel_location_from":
      last_payload_item['vm_vessel_location_from'],
      "vm_vessel_location_to":
      last_payload_item['vm_vessel_location_to'],
      "vm_vessel_movement_height":
      last_payload_item['vm_vessel_movement_height'],
      "vm_vessel_movement_type":
      last_payload_item['vm_vessel_movement_type'],
      "vm_vessel_movement_start_dt":
      last_payload_item['vm_vessel_movement_start_dt'],
      "vm_vessel_movement_end_dt":
      last_payload_item['vm_vessel_movement_end_dt'],
      "vm_vessel_movement_status":
      last_payload_item['vm_vessel_movement_status'],
      "vm_vessel_movement_draft":
      last_payload_item['vm_vessel_movement_draft']
    }
    except:
      print("================no movement end date, printing exception===============")
      row_data_vessel_movement = {
      "vm_vessel_particulars.vessel_nm":
      last_payload_item['vm_vessel_particulars'][0]['vessel_nm'],
      "vm_vessel_particulars.vessel_imo_no":
      last_payload_item['vm_vessel_particulars'][0]['vessel_imo_no'],
      "vm_vessel_particulars.vessel_flag":
      last_payload_item['vm_vessel_particulars'][0]['vessel_flag'],
      "vm_vessel_particulars.vessel_call_sign":
      last_payload_item['vm_vessel_particulars'][0]['vessel_call_sign'],
      "vm_vessel_location_from":
      last_payload_item['vm_vessel_location_from'],
      "vm_vessel_location_to":
      last_payload_item['vm_vessel_location_to'],
      "vm_vessel_movement_height":
      last_payload_item['vm_vessel_movement_height'],
      "vm_vessel_movement_type":
      last_payload_item['vm_vessel_movement_type'],
      "vm_vessel_movement_start_dt":
      last_payload_item['vm_vessel_movement_start_dt'],
      "vm_vessel_movement_end_dt":
      "",
      "vm_vessel_movement_status":
      last_payload_item['vm_vessel_movement_status'],
      "vm_vessel_movement_draft":
      last_payload_item['vm_vessel_movement_draft']
    }
    # Append the data to the worksheet
    print(f"row_data_vessel_movement: {row_data_vessel_movement}")
    # Add the current date and time to your data dictionary
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data_vessel_movement['Timestamp vessel_movement'] = str(current_datetime)
    #Initialise Gsheet
    gc = pygsheets.authorize(service_account_file=gsheet_cred_path)
    print(f"Receive vessel_movement API: {gc.spreadsheet_titles()}")
    sh = gc.open('SGTD Received APIs')
    worksheet_replit = sh.worksheet_by_title("replit_vessel_movement")

    # Write the headers as the first row
    print(f"row_data_vessel_movement.keys: {row_data_vessel_movement.keys()}")
    worksheet_replit.insert_rows(
    row=1,number=1,values=list(row_data_vessel_movement.keys()))

    # Append the data as a new row
    worksheet_replit.append_table(
      start='A2',  # You can specify the starting cell here
      end=None,  # You can specify the ending cell if needed
      values=list(row_data_vessel_movement.values()))
    worksheet_replit.delete_rows(1)
    print([list(row_data_vessel_movement.values())])

    return f"Gsheet row_data_vessel_movement appended {list(row_data_vessel_movement.values())}"



#==========================RECEIVE vessel_current_position===============================
@app.route("/api/vessel_current_position/receive/admin", methods=['POST'])
def Vessel_current_position():
    email = "joel.koh@sgtradex.com"
    receive_details_data = receive_details(email)
    print(f"Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]
  
    data = request.data  # Get the raw data from the request body
    
    print(f"Vessel_current_position = {data}")

    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_vessel_current_position = data_dict['payload'][-1]
    # Add the current date and time to your data dictionary
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data_vessel_current_position['Timestamp vessel_current_position'] = str(current_datetime)
    
    print(
      f"row_data_vessel_current_position: {row_data_vessel_current_position}")
    #Initialise Gsheet
    gc = pygsheets.authorize(service_account_file=gsheet_cred_path)
  
    print(gc.spreadsheet_titles())
  
    sh = gc.open('SGTD Received APIs')
    worksheet_replit = sh.worksheet_by_title("replit_vessel_current_position")

    # Extract specific keys from 'vessel_particulars' for column headers
    vessel_particulars = data_dict['payload'][0]['vessel_particulars'][0]
  
    print(f"vessel_particulars: {vessel_particulars}")
  
    # Create column headers from the keys in 'vessel_particulars'
    column_headers = list(vessel_particulars.keys())
  
    print(f"column_headers: {column_headers}")
  
    # Extract all the keys from the payload data
    payload_keys = list(data_dict['payload'][0].keys())
  
    print(f"payload_keys: {payload_keys}")
      # Append the payload keys (excluding 'vessel_particulars') to column_headers
    column_headers.extend([key for key in payload_keys if key != 'vessel_particulars'])
    
    # Append a 'Timestamp' column
    #Column_headers.append('Timestamp')
    print(f"column_headers final: {column_headers}")

    # Write the headers as the first row
    worksheet_replit.insert_rows(
    row=1,number=1,values=column_headers)

    # Extract the payload data
    payload_data = data_dict['payload'][0]
  
    print(f"payload_data: {payload_data}")
  
    # Extract all the values from the payload data
    payload_values = [payload_data[key] for key in payload_keys if key != 'vessel_particulars']
  
    print(f"payload_values: {payload_data}")
  
    # Create a list of values corresponding to the keys
    vessel_particulars_values = list(vessel_particulars.values())
  
    print(f"vessel_particulars_values: {vessel_particulars_values}")
  
    # Extend row_values with payload_values
    row_values = vessel_particulars_values + payload_values
    
    # Append the 'Timestamp' value
    #row_values.append(current_datetime)
    print(f"row_values = {row_values}")

    # Append the data as a new row
    worksheet_replit.append_table(values=row_values, start='A2')
    worksheet_replit.delete_rows(1)
    return f"Vessel Current Location Data saved to Google Sheets.{row_values}"
  # except Exception as e:
  #   # Handle the error gracefully and log it
  #   print("An error occurred:", str(e))
  #   return f"An error occurred: {str(e)}", 500  # Return a 500





#9490820 / 9929297
#====================================MAP========================================
@app.route("/api/vessel_map", methods=['GET','POST'])
def Vessel_map():
  if g.email:
    session['id'] = id
    session['email']=email
    session['participant_id']=pID
    session['pitstop_url']=pitstop
    session['api_key']=API_KEY
    session['gc']=gSheet
    gc = pygsheets.authorize(service_account_file=session['gc'])
    # Assuming you have two sheets named 'Sheet1' and 'Sheet2'
    print(gc.spreadsheet_titles())
    sh = gc.open('SGTD Received APIs')
    sheet1 = sh.worksheet_by_title('replit_vessel_current_position')
    sheet2 = sh.worksheet_by_title('replit_vessel_movement')
    # Read data from 'Sheet1' into a DataFrame
    df1 = pd.DataFrame(sheet1.get_all_records())
    print(f"df1 = {df1}")
    # Read data from 'Sheet2' into another DataFrame
    df2 = pd.DataFrame(sheet2.get_all_records())
    print(f"df2 = {df2}")
    
    # Assuming 'imo_no' is the common column
    merged_df = pd.merge(df1,
                         df2,
                         left_on='vessel_imo_no',
                         right_on='vm_vessel_particulars.vessel_imo_no',
                         how='inner')
    
    merged_df.drop(columns=['vm_vessel_particulars.vessel_call_sign', 'vm_vessel_particulars.vessel_flag', 'vm_vessel_movement_type', 'vm_vessel_movement_height','vessel_year_built','vessel_call_sign','vessel_length','vessel_depth','vessel_course','vessel_longitude','vessel_latitude','vm_vessel_movement_draft','vm_vessel_particulars.vessel_nm'], inplace=True)
    print(f"Merged_df == {merged_df.to_string(index=False)}")
    print(f"Merged_df IMO No == {merged_df['vessel_imo_no'].to_string(index=False)}")

    #sort & drop duplicates
    # sorting by first name
    merged_df.drop_duplicates(subset="vessel_imo_no", keep='last', inplace=True)
    
    m = leafmap.Map(center=[1.257167, 103.897], zoom=12)
    regions = 'templates/SG_anchorages.geojson'
    m.add_geojson(regions,
                  layer_name='SG Anchorages',
                  style={
                    "color": (random.choice(colors)),
                    "fill": True,
                    "fillOpacity": 0.05
                  })
    m.add_points_from_xy(
      merged_df,
      x="vessel_longitude_degrees",
      y="vessel_latitude_degrees",
      icon_names=['gear', 'map', 'leaf', 'globe'],
      spin=True,
      add_legend=True,
    )
    print(f"Merged_df IMO No == {merged_df['vessel_imo_no'].to_string(index=False)}, vessel_latitude_degrees = {merged_df['vessel_latitude_degrees'].to_string(index=False)}, vessel_longitude_degrees = {merged_df['vessel_longitude_degrees'].to_string(index=False)}")
    for f in os.listdir("templates/"):
      #print(f)
      if "mymap.html" in f:
          print(f"*mymap.html file to be removed = {f}")
          os.remove(f"templates/{f}")
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    newHTML = f"templates/{current_datetime}mymap.html"
    newHTMLwotemp = f"{current_datetime}mymap.html"
    print(f"new html file created = {newHTML}")
    m.to_html(newHTML)
    #time.sleep(2)
    return render_template(newHTMLwotemp, user=session['email'])
  return redirect(url_for('login'))

@app.before_request
def before_request():
  g.email=None
  if 'email' in session:
    g.email=session['email']




#========================Vesseldata GET===========================
@app.route("/api/sgtd")
def SGTD():
  system_ids_names = []
  API_Key = 'VJN5vqP8LfZxVCycQT6PvpJ0VM4Vk2pW'
  # Make the GET request
  url = 'https://sgtradexdummy-lbo.pitstop.uat.sgtradex.io/api/v1/config'
  r_GET = requests.get(url, headers={'SGTRADEX-API-KEY': API_Key})
  consumes_list = r_GET.json()['data']['consumes']
  # Check the response
  if r_GET.status_code == 200:
    print("Config Data retrieved successfully!")
  else:
    print(f"Failed to get Config Data. Status code: {r_GET.status_code}")
    print(r_GET.text
          )  # Print the response content if the request was not successful
  for consume in consumes_list:
    if consume['id'] == 'vessel_current_position':
      from_list = consume['from']
      for from_item in from_list:
        system_ids_names.append((from_item['id'], from_item['name']))
  return system_ids_names

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

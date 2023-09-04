from flask import Flask, render_template, request, redirect, url_for, session, g
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
# from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)

app.secret_key = os.urandom(24)

@app.route("/", methods=['GET','POST'])
def index():
  if request.method=='POST':
    session.pop('user,None')
  return render_template('login.html')
  
@app.route("/register", methods=['GET','POST'])
def register():
  if request.method == 'POST':
    data = request.form
    print(data)
    new_registration(data)
    return render_template('login.html')
  if request.method == 'GET':
    return render_template('register.html')

@app.route("/login", methods=['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username_']
    password = request.form['password_']
    # API_KEY = request.form['api_key_']
    # pID = request.form['participant_id_']
    # obID = request.form['on_behalf_id_']
    validate_login(username, password)
    print(f"Validate_login value returned = {validate_login(username, password)}")
    if len(validate_login(username, password)) == 4:
      session['user']=username
      global API_KEY
      global pID 
      global obID
      global gc
      global gSheet
      API_KEY = validate_login(username, password)[0]
      pID = validate_login(username, password)[1]
      obID = validate_login(username, password)[2]
      gSheet = validate_login(username, password)[3]
      gc = pygsheets.authorize(service_account_file=gSheet)
      print("Login success, redirect")
      #redirect(url_for('Vessel_data_pull', API_KEY=API_KEY, pID=pID, obID=obID))
      #return redirect(url_for('Vessel_map'))
      return render_template('vessel_request.html')
    else:
      print("Invalid credentials, reset login")
      return render_template('login.html')
    # if request.data['username'] and request.data['password'] in db:
    #   user_data = load_data_from_db()
  if request.method == 'GET':
    return render_template('login.html')
      

  
colors = [
"red","blue","green","purple","orange","darkred","lightred","beige","darkblue","darkgreen","cadetblue","darkpurple","white","pink","lightblue","lightgreen","gray","black","lightgray"
]
#gc = pygsheets.authorize(service_account_file='creds.json')


#========================Vessel data PULL===========================
@app.route("/api/vessel")
def Vessel_data_pull(API_KEY, pID, obID):
  user_vessel_imo = request.form['vessel_imo']
  input_list = [int(x) for x in user_vessel_imo.split(',')]
  print(f"API_KEY={API_KEY}, pID={pID}, obID={obID}")
  print(f"user_vessel_imo from html = {user_vessel_imo}")
  print(f"input_list from html = {input_list}")
  print(f"API_KEY={API_KEY}, pID={pID}, obID={obID}")
  #vessel_imo = request.args.get('imo')
  #API_KEY = API_KEY
  # API_KEY = 'VJN5vqP8LfZxVCycQT6PvpJ0VM4Vk2pW'
  #vessel_imo = "9702699"
  for vessel_imo in input_list:
    print(f"IMO Number = {vessel_imo}")
    url_vessel_movement = "https://sgtradexdummy-lbo.pitstop.uat.sgtradex.io/api/v1/data/pull/vessel_movement"
    url_vessel_current_position = "https://sgtradexdummy-lbo.pitstop.uat.sgtradex.io/api/v1/data/pull/vessel_current_position"
    on_behalf_of_id = "49f04a6f-f157-479b-b211-18931fad4ca4"
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
        #"id": on_behalf_of_id
        "id": obID
      }]
    }
    
    json_string = json.dumps(
      payload, indent=4)  # Convert payload dictionary to JSON string
    # Rest of the code to send the JSON payload to the API
    data = json.loads(json_string)
  #========================PULL vessel_current_position===========================
    response_vessel_current_position = requests.post(
  url_vessel_current_position,json=data, headers={'SGTRADEX-API-KEY': API_KEY})
    if response_vessel_current_position.status_code == 200:
      print(f"Response JSON = {response_vessel_current_position.json()}")
      print("Pull vessel_current_position success.")
    else:
      print(
        f"Failed to PULL vessel_current_position data. Status code: {response_vessel_current_position.status_code}"
      )

  #========================PULL vessel_movement=====================================
    response_vessel_movement = requests.post(
      url_vessel_movement, json=data, headers={'SGTRADEX-API-KEY': API_KEY})
    if response_vessel_movement.status_code == 200:
      #print(f"Response JSON = {response_vessel_movement.json()}")
      print("Pull vessel_movement success.")
    else:
      print(
        f"Failed to PULL vessel_movement data. Status code: {response_vessel_movement.status_code}"
      )
    #print(response_vessel_movement.text)
  
  sh = gc.open('SGTD Received APIs')
  sheet1 = sh.worksheet_by_title("replit_vessel_current_position")
  sheet1.clear()
  print('Cleared replit_vessel_current_position')
  sheet2 = sh.worksheet_by_title('replit_vessel_movement')
  sheet2.clear()
  print('Cleared replit_vessel_movement')
    #clear
  #print("Sleep 3 seconds")
  #time.sleep(2)
    #print(response_vessel_current_position.text)
  return redirect(url_for('Vessel_map'))


#==========================RECEIVE vessel_movement===============================
@app.route("/api/vessel_movement/receive/admin", methods=['POST'])
def Vessel_movement_receive():
    username = "admin"
    gsheet_data = receive_details(username)
    print(f"Receive_details from database.py {receive_details(username)}")
    gc = pygsheets.authorize(service_account_file=gsheet_data)
  #try:
    data = request.data  # Get the raw data from the request body
    #print(data)
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
    row_data_vessel_movement['Timestamp'] = current_datetime
    print(gc.spreadsheet_titles())
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

    #wks.update_value( (1,len(wks[0])), "classstr")
    return "Gsheet row_data_vessel_movement appended"
  # except Exception as e:
  #   # Handle the error gracefully and log it
  #   print("An error occurred:", str(e))
  #   return f"An error occurred: {str(e)}", 500  # Return a 500


#==========================RECEIVE vessel_current_position===============================
@app.route("/api/vessel_current_position/receive/admin", methods=['POST'])
def Vessel_current_position():
  # try:
    username = "admin"
    gsheet_data = receive_details(username)
    print(f"Receive_details from database.py {receive_details(username)}")
    gc = pygsheets.authorize(service_account_file=gsheet_data)
    data = request.data  # Get the raw data from the request body
    print(f"Vessel_current_position = {data}")
    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_vessel_current_position = data_dict['payload'][-1]
    # Add the current date and time to your data dictionary
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data_vessel_current_position['Timestamp'] = current_datetime
    print(
      f"row_data_vessel_current_position: {row_data_vessel_current_position}")
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
    # Append the column headers as the first row
    #worksheet_replit.append_table(values=column_headers, start='A1')


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
    return "Vessel Current Location Data saved to Google Sheets."
  # except Exception as e:
  #   # Handle the error gracefully and log it
  #   print("An error occurred:", str(e))
  #   return f"An error occurred: {str(e)}", 500  # Return a 500





#9490820 / 9929297
#====================================MAP========================================
@app.route("/api/vessel_map", methods=['GET','POST'])
def Vessel_map():
  if g.user:
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
    return render_template(newHTMLwotemp, user=session['user'])
  return redirect(url_for('login'))

@app.before_request
def before_request():
  g.user=None
  if 'user' in session:
    g.user=session['user']




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

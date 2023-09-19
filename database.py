from sqlalchemy import create_engine, text
import pandas as pd
import os
import json

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})

def load_data_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from userDB"))
    result_all = result.all()
    print(f"result = {result_all}")
    user_data = []
    for row in result_all:
      user_data.append(dict(row._mapping))
    print(f"result_dicts = {user_data}")
  return user_data

def load_user_from_db(email, password):
  with engine.connect() as conn:
    email = email
    password = password
    result = conn.execute(text("select * from userDB WHERE email = :email and password = :password"))
    result_all = result.all()
    if len(result_all) == 0:
      return None
    else:
      return dict(rows[0])
    print(f"result = {result_all}")
  return user_data

# def new_registration(email, password, api_key, participant_id, on_behalf_id, gsheet_cred_path, company):
def new_registration(data):
  print(f"printing data from new_registration: {data}")
  print(f"data['email'] == {data['email']}")
  print(f"data['api_key'] == {data['api_key']}")
  print(f"data['participant_id'] == {data['participant_id']}")
  email = data['email']
  password = data['password']
  with engine.connect() as conn:
    query = text("select * from userDB WHERE email = :email")
    values = {'email' : email}
    result = conn.execute(query, values)
    result_all = result.all()
    print(result_all)
    print(f"length of result all = {len(result_all)}")
    if len(result_all) == 0:
      query = text("INSERT INTO userDB (email, password, api_key, participant_id, pitstop_url, gsheet_cred_path) VALUES (:email,:password, :api_key, :participant_id, :pitstop_url, :gsheet_cred_path)")
      values = {'email' : data['email'], 'password' : data['password'], 'api_key' : data['api_key'], 'participant_id' :data['participant_id'], 'pitstop_url':data['pitstop_url'],'gsheet_cred_path' : data['gsheet_cred_path']}
      print(query)
      result = conn.execute(query, values)
      print("execute success")
      return 1
    else:
      print('User exists, please try again')
      return 0
    #conn.execute(query, email = data['email'],password =data['password'],api_key = data['api_key'],participant_id = data['participant_id'],on_behalf_id_ = data['on_behalf_id_'],gsheet_cred_path = data['gsheet_cred_path'], company_ = data['company_'])
    


def validate_login(email, password):
  print(f"printing data from validate_login: email = {email}, password = {password}")

  with engine.connect() as conn:
    query = text("SELECT * FROM userDB WHERE email = :email AND password = :password")
    values = {'email' : email, 'password' : password}
    check_login = conn.execute(query, values)
    login_entry = check_login.all()[0]
    print(f"check_login == {login_entry}")
    print(f"check_login TYPE == {type(login_entry)}")
    print(f"check_login_API == {login_entry[3]}")
    result_login = len(login_entry)
    print(login_entry[3],login_entry[4],login_entry[5])
    print(f"result_login == {result_login}")
    if result_login > 1:
      print("Login success")
      return (login_entry[0],login_entry[3],login_entry[4],login_entry[5], login_entry[6])
    else:
      print("Error in Login")
      return 0

def receive_details(email):
  with engine.connect() as conn:
    query = text("SELECT * FROM userDB WHERE email = :email")
    values = {'email' : email}
    receive_db = conn.execute(query, values)
    receive_data = receive_db.all()[0]
    #print(f"receive_data == {receive_data}, return api ={receive_data[3]}, return pID = {receive_data[4]}, return pitstop = {receive_data[5]}")
  return(receive_data[0],receive_data[3],receive_data[4],receive_data[5],receive_data[6])


def new_vessel_current_position(data, email, gsheet_cred_path):
  engine_vcp = create_engine(gsheet_cred_path,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
  with engine_vcp.connect() as conn:
    query_vcp = text("""
    INSERT INTO vessel_current_position_UCE (
        vessel_nm,
        vessel_imo_no,
        vessel_call_sign,
        vessel_flag,
        vessel_length,
        vessel_depth,
        vessel_type,
        vessel_grosstonnage,
        vessel_nettonnage,
        vessel_deadweight,
        vessel_mmsi_number,
        vessel_year_built,
        vessel_latitude,
        vessel_longitude,
        vessel_latitude_degrees,
        vessel_longitude_degrees,
        vessel_speed,
        vessel_course,
        vessel_heading,
        vessel_time_stamp
    ) VALUES (
        :vessel_nm,
        :vessel_imo_no,
        :vessel_call_sign,
        :vessel_flag,
        :vessel_length,
        :vessel_depth,
        :vessel_type,
        :vessel_grosstonnage,
        :vessel_nettonnage,
        :vessel_deadweight,
        :vessel_mmsi_number,
        :vessel_year_built,
        :vessel_latitude,
        :vessel_longitude,
        :vessel_latitude_degrees,
        :vessel_longitude_degrees,
        :vessel_speed,
        :vessel_course,
        :vessel_heading,
        :vessel_time_stamp
    )
""")
        

# Define the data dictionary
    values_vcp = {
    'vessel_nm': data['vessel_particulars'][0]['vessel_nm'],
    'vessel_imo_no': data['vessel_particulars'][0]['vessel_imo_no'],
    'vessel_call_sign': data['vessel_particulars'][0]['vessel_call_sign'],
    'vessel_flag': data['vessel_particulars'][0]['vessel_flag'],
    'vessel_length': data['vessel_length'],
    'vessel_depth': data['vessel_depth'],
    'vessel_type': data['vessel_type'],
    'vessel_grosstonnage': data['vessel_grosstonnage'],
    'vessel_nettonnage': data['vessel_nettonnage'],
    'vessel_deadweight': data['vessel_deadweight'],
    'vessel_mmsi_number': data['vessel_mmsi_number'],
    'vessel_year_built': data['vessel_year_built'],
    'vessel_latitude': data['vessel_latitude'],
    'vessel_longitude': data['vessel_longitude'],
    'vessel_latitude_degrees': data['vessel_latitude_degrees'],
    'vessel_longitude_degrees': data['vessel_longitude_degrees'],
    'vessel_speed': data['vessel_speed'],
    'vessel_course': data['vessel_course'],
    'vessel_heading': data['vessel_heading'],
    'vessel_time_stamp': data['vessel_time_stamp']
}

    result = conn.execute(query_vcp, values_vcp)
  print("New vessel_current_position execute success")
  return 1


def new_vessel_movement(data, email, gsheet_cred_path):
  engine_vm = create_engine(gsheet_cred_path,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
  with engine_vm.connect() as conn:
    query_vm = text("INSERT INTO vessel_movement_UCE (    vessel_nm,vessel_imo_no,vessel_flag,vessel_call_sign,vessel_location_from,vessel_location_to,vessel_movement_height,vessel_movement_type,vessel_movement_start_dt,vessel_movement_end_dt,vessel_movement_status,vessel_movement_draft) VALUES (:vessel_nm,:vessel_imo_no,:vessel_flag,:vessel_call_sign,:vessel_location_from,:vessel_location_to,:vessel_movement_height,:vessel_movement_type,:vessel_movement_start_dt,:vessel_movement_end_dt,:vessel_movement_status,:vessel_movement_draft)")
      
    values_vm = {'vessel_nm':data['vm_vessel_particulars.vessel_nm'],'vessel_imo_no':data['vm_vessel_particulars.vessel_imo_no'],'vessel_flag':data['vm_vessel_particulars.vessel_flag'],'vessel_call_sign': data['vm_vessel_particulars.vessel_call_sign'],'vessel_location_from': data['vm_vessel_location_from'],'vessel_location_to':data['vm_vessel_location_to'],'vessel_movement_height': data['vm_vessel_movement_height'],'vessel_movement_type':data['vm_vessel_movement_type'],'vessel_movement_start_dt':data['vm_vessel_movement_start_dt'],'vessel_movement_end_dt':data['vm_vessel_movement_end_dt'],'vessel_movement_status':data['vm_vessel_movement_status'],'vessel_movement_draft':data['vm_vessel_movement_draft']}

    result = conn.execute(query_vm, values_vm)
  print("New vessel_current_position execute success")
  return 1


def new_pilotage_service(data, email, gsheet_cred_path):
  engine_pilot = create_engine(gsheet_cred_path,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
  with engine_pilot.connect() as conn:
    query_pilot = text("INSERT INTO vessel_movement_UCE (    vessel_nm,vessel_imo_no,vessel_flag,vessel_call_sign,vessel_location_from,vessel_location_to,vessel_movement_height,vessel_movement_type,vessel_movement_start_dt,vessel_movement_end_dt,vessel_movement_status,vessel_movement_draft) VALUES (:vessel_nm,:vessel_imo_no,:vessel_flag,:vessel_call_sign,:vessel_location_from,:vessel_location_to,:vessel_movement_height,:vessel_movement_type,:vessel_movement_start_dt,:vessel_movement_end_dt,:vessel_movement_status,:vessel_movement_draft)")
    
    values_pilot = {'vessel_nm':data['vm_vessel_particulars.vessel_nm'],'vessel_imo_no':data['vm_vessel_particulars.vessel_imo_no'],'vessel_flag':data['vm_vessel_particulars.vessel_flag'],'vessel_call_sign': data['vm_vessel_particulars.vessel_call_sign'],'vessel_location_from': data['vm_vessel_location_from'],'vessel_location_to':data['vm_vessel_location_to'],'vessel_movement_height': data['vm_vessel_movement_height'],'vessel_movement_type':data['vm_vessel_movement_type'],'vessel_movement_start_dt':data['vm_vessel_movement_start_dt'],'vessel_movement_end_dt':data['vm_vessel_movement_end_dt'],'vessel_movement_status':data['vm_vessel_movement_status'],'vessel_movement_draft':data['vm_vessel_movement_draft']}

    result = conn.execute(query_pilot, values_pilot)
  print("New vessel_current_position execute success")
  return 1





















def get_map_data(db_creds):
  print("Start of get_map_data......")
  engine = create_engine(
  db_creds,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})
  with engine.connect() as conn:
    query = text("select * from vessel_movement_UCE")
    result_VM = conn.execute(query)
    result_all_VM = result_VM.fetchall()
    column_names_VM = result_VM.keys()
    print(result_all_VM)
    print(f"length of result_all_VM = {len(result_all_VM)}")
    df1 = pd.DataFrame(result_all_VM, columns=column_names_VM)

    
    query = text("select * from MPA_vessel_data")
    result_VCP = conn.execute(query)
    result_all_VCP = result_VCP.fetchall()
    column_names_VCP = result_VCP.keys() 
    print(result_all_VCP)
    print(f"length of result_all_VCP = {len(result_all_VCP)}")
    df2 = pd.DataFrame(result_all_VCP, columns=column_names_VCP)
    # sorting by first name
   df2.drop_duplicates(subset="imoNumber", keep='last', inplace=True)


    query = text("select * from MPA_arrivaldeclaration")
    result_ETA = conn.execute(query)
    result_all_ETA = result_ETA.fetchall()
    column_names_ETA = result_ETA.keys() 
    print(result_all_ETA)
    print(f"length of result_all_ETA = {len(result_all_ETA)}")
    df3 = pd.DataFrame(result_all_ETA, columns=column_names_ETA)
    df3.drop_duplicates(subset="imo_number", keep='last', inplace=True)
    df2.drop(columns=['key_0'],inplace=True)
    df2 = pd.merge(df2,
                   df3,
                   left_on=df2['imoNumber'],
                   right_on=df3['imo_number'],
                   how='outer')
    
    print(f"Final Result all vm = {[df1, df2]}")
    return [df1, df2]

    
def delete_all_rows_in_table(db_creds):
  print("Start of delete_all_rows_in_table......")
  engine = create_engine(
  db_creds,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})
  with engine.connect() as conn:
    query_VM = text("DELETE FROM vessel_movement_UCE where id > 0")
    print("Deleted vessel_movement_UCE where id > 0")
    result_VM = conn.execute(query_VM)
    query_VCP = text("DELETE FROM vessel_current_position_UCE where id > 0")
    result_VCP = conn.execute(query_VCP)
    print("Deleted vessel_current_position_UCE where id > 0")
    query_MPA = text("DELETE FROM MPA_vessel_data WHERE id > 0")
    result_MPA = conn.execute(query_MPA)
    print("Deleted MPA_vessel_data where id > 0")

def MPA_GET(api_response, gsheet_cred_path):
  
  data_list = json.loads(api_response)
  print(f"API response = {(data_list)}")
  print(f"API response[0] = {data_list[0]}")
  vessel_data = data_list[0]['vesselParticulars']
  print(f"vessel_data = {vessel_data}")
  print(f"vessel_data['vesselName'] = {vessel_data['vesselName']}")
  print(f"vessel_data['callSign'] = {vessel_data['callSign']}")
  latitude = data_list[0]['latitude']
  print(f"latitude = {data_list[0]['latitude']}")
  longitude = data_list[0]['longitude']
  latitude_degrees = data_list[0]['latitudeDegrees']
  longitude_degrees = data_list[0]['longitudeDegrees']
  speed = data_list[0]['speed']
  course = data_list[0]['course']
  heading = data_list[0]['heading']
  timestamp = data_list[0]['timeStamp']
  
  query = text("INSERT INTO MPA_vessel_data (vesselName, callSign, imoNumber, flag, vesselLength, vesselBreadth, vesselDepth, vesselType, grossTonnage, netTonnage, deadweight, mmsiNumber, yearBuilt, latitude, longitude, latitudeDegrees, longitudeDegrees, speed, course, heading, timeStamp) VALUES (:vesselName, :callSign, :imoNumber, :flag, :vesselLength, :vesselBreadth, :vesselDepth, :vesselType, :grossTonnage, :netTonnage, :deadweight, :mmsiNumber, :yearBuilt, :latitude, :longitude, :latitudeDegrees, :longitudeDegrees, :speed, :course, :heading, :timeStamp)")
  values = {'vesselName':vessel_data['vesselName'], 'callSign':vessel_data['callSign'], 'imoNumber':vessel_data['imoNumber'], 'flag':vessel_data['flag'], 'vesselLength':vessel_data['vesselLength'], 'vesselBreadth':vessel_data['vesselBreadth'], 'vesselDepth':vessel_data['vesselDepth'], 'vesselType':vessel_data['vesselType'], 'grossTonnage':vessel_data['grossTonnage'], 'netTonnage':vessel_data['netTonnage'], 'deadweight':vessel_data['deadweight'], 'mmsiNumber':vessel_data['mmsiNumber'], 'yearBuilt':vessel_data['yearBuilt'], 'latitude':latitude, 'longitude':longitude, 'latitudeDegrees':latitude_degrees, 'longitudeDegrees':longitude_degrees, 'speed':speed, 'course':course, 'heading':heading, 'timeStamp':timestamp}

  engine_MPA_GET = create_engine(gsheet_cred_path,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
  with engine_MPA_GET.connect() as conn:
    MPA_Data = conn.execute(query, values)
  return MPA_Data



def MPA_GET_arrivaldeclaration(api_response, gsheet_cred_path):
  data_list = json.loads(api_response)
  print(f"API response = {(data_list)}")
  print(f"API response[0] = {data_list[0]}")

  # Initialize variables to keep track of the latest record and time
  latest_record = None
  latest_time = None
  # Iterate through the list of records
  for record in data_list:
    reported_arrival_time = record.get("reportedArrivalTime")

    # Check if reported_arrival_time is not None and greater than the latest_time
    if reported_arrival_time and (latest_time is None or reported_arrival_time > latest_time):
        latest_record = record
        latest_time = reported_arrival_time

    # Print the latest record
  if latest_record:
      print(json.dumps(latest_record, indent=4))
  else:
    print("No records with reported arrival times found.")

  # Your JSON data
  vessel_data = latest_record
  
  # Create a SQL query with placeholders for the values
  query = text("""
      INSERT INTO MPA_arrivaldeclaration (
          vessel_name, call_sign, imo_number, flag, 
          location, grid, purpose, agent, reported_arrival_time
      ) VALUES (
          :vessel_name, :call_sign, :imo_number, :flag, 
          :location, :grid, :purpose, :agent, :reported_arrival_time
      )
  """)
  
  # Prepare the values
  values = {
      'vessel_name': vessel_data['vesselParticulars']['vesselName'],
      'call_sign': vessel_data['vesselParticulars']['callSign'],
      'imo_number': vessel_data['vesselParticulars']['imoNumber'],
      'flag': vessel_data['vesselParticulars']['flag'],
      'location': vessel_data['location'],
      'grid': vessel_data['grid'],
      'purpose': vessel_data['purpose'],
      'agent': vessel_data['agent'],
      'reported_arrival_time': vessel_data['reportedArrivalTime']
  }
  
  engine_MPA_arrivaldeclaration = create_engine(gsheet_cred_path,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
  with engine_MPA_arrivaldeclaration.connect() as conn:
    MPA_arrivaldeclaration = conn.execute(query, values)
  return MPA_arrivaldeclaration


# def MPA_GET_GSHEET(api_response,gsheet_cred_path):

#   gc = pygsheets.authorize(service_account_file=gsheet_cred_path)
#   print(gc.spreadsheet_titles())
#   sh = gc.open('SGTD Received APIs')
#   worksheet_replit = sh.worksheet_by_title("replit_vessel_current_position")
  
#   data_list = json.loads(api_response)
#   print(f"API response = {(data_list)}")
#   print(f"API response[0] = {data_list[0]}")
#   vessel_data = data_list[0]['vesselParticulars']
#   print(f"vessel_data = {vessel_data}")
#   print(f"vessel_data['vesselName'] = {vessel_data['vesselName']}")
#   print(f"vessel_data['callSign'] = {vessel_data['callSign']}")
#   latitude = data_list[0]['latitude']
#   print(f"latitude = {data_list[0]['latitude']}")
#   longitude = data_list[0]['longitude']
#   latitude_degrees = data_list[0]['latitudeDegrees']
#   longitude_degrees = data_list[0]['longitudeDegrees']
#   speed = data_list[0]['speed']
#   course = data_list[0]['course']
#   heading = data_list[0]['heading']
#   timestamp = data_list[0]['timeStamp']

#   #Column Headers
#   column_headers = list(vessel_data.keys())
#     # Extract all the keys from the payload data
#   payload_keys = list(data_list[0].keys())
#   print(f"payload_keys: {payload_keys}")
#     # Append the payload keys (excluding 'vessel_particulars') to column_headers
#   column_headers.extend([key for key in payload_keys if key != 'vesselParticulars'])
#   # Write the headers as the first row
#   worksheet_replit.insert_rows(
#   row=1,number=1,values=column_headers)

#   #Column Values
# # Extract the payload data
#   # Extract the payload data
#   payload_data = data_list[0]
#   print(f"payload_data: {payload_data}")
#   # Extract all the values from the payload data
#   payload_values = [payload_data[key] for key in payload_keys if key != 'vesselParticulars']
#   print(f"payload_values: {payload_data}")
#   # Create a list of values corresponding to the keys
#   vessel_particulars_values = list(vesselParticulars.values())
#   print(f"vessel_particulars_values: {vessel_particulars_values}")
#   # Extend row_values with payload_values
#   row_values = vessel_particulars_values + payload_values

#   # Append the data as a new row
#   worksheet_replit.append_table(values=row_values, start='A2')
#   worksheet_replit.delete_rows(1)
#   return f"Vessel Current Location Data saved to Google Sheets.{row_values}"











# #CREATE TABLE vessel_movement_UCE (
# 	id int NOT NULL AUTO_INCREMENT,
#     vessel_nm VARCHAR(255),
#     vessel_imo_no VARCHAR(255),
#     vessel_flag VARCHAR(255),
#     vessel_call_sign VARCHAR(255),
#     vessel_location_from VARCHAR(255),
#     vessel_location_to VARCHAR(255),
#     vessel_movement_height VARCHAR(255),
#     vessel_movement_type VARCHAR(255),
#     vessel_movement_start_dt DATETIME,
#     vessel_movement_end_dt DATETIME,
#     vessel_movement_status VARCHAR(255),
#     vessel_movement_draft VARCHAR(255),
#     Timestamp_vessel_movement DATETIME,
#     Timestamp_query DATETIME default now(),
#     PRIMARY KEY (`id`)
# );

# #CREATE TABLE vessel_current_position_UCE (
# 	id int NOT NULL AUTO_INCREMENT,
#     vessel_nm VARCHAR(255),
#     vessel_imo_no VARCHAR(255),
#     vessel_call_sign VARCHAR(255),
#     vessel_flag VARCHAR(255),
#     vessel_length FLOAT,
#     vessel_depth FLOAT,
#     vessel_type VARCHAR(255),
#     vessel_grosstonnage FLOAT,
#     vessel_nettonnage FLOAT,
#     vessel_deadweight FLOAT,
#     vessel_mmsi_number VARCHAR(255),
#     vessel_year_built INT,
#     vessel_latitude DECIMAL(10, 6),
#     vessel_longitude DECIMAL(10, 6),
#     vessel_latitude_degrees DECIMAL(10, 6),
#     vessel_longitude_degrees DECIMAL(10, 6),
#     vessel_speed FLOAT,
#     vessel_course FLOAT,
#     vessel_heading FLOAT,
#     vessel_time_stamp DATETIME,
#     Timestamp_vessel_current_position DATETIME,
#     Timestamp_query DATETIME default now(),
#     PRIMARY KEY (`id`)
# );

# CREATE TABLE MPA_arrivaldeclaration (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     vessel_name VARCHAR(255),
#     call_sign VARCHAR(255),
#     imo_number VARCHAR(255),
#     flag VARCHAR(255),
#     location VARCHAR(255),
#     grid VARCHAR(255),
#     purpose VARCHAR(255),
#     agent VARCHAR(255),
#     reported_arrival_time DATETIME
# );

# CREATE TABLE MPA_vessel_data (
# 	id int NOT NULL AUTO_INCREMENT,
#     vesselName VARCHAR(255),
# 	callsign VARCHAR(255),
#     imoNumber VARCHAR(255),
#     flag VARCHAR(255),
#     vesselLength FLOAT,
#     vesselBreadth FLOAT,
#     vesselDepth FLOAT,
#     vesselType VARCHAR(255),
#     grossTonnage FLOAT,
#     netTonnage FLOAT,
#     deadweight FLOAT,
#     mmsiNumber VARCHAR(255),
#     yearBuilt INT,
#     latitude DECIMAL(10, 6),
#     longitude DECIMAL(10, 6),
#     latitudeDegrees DECIMAL(10, 6),
#     longitudeDegrees DECIMAL(10, 6),
#     speed FLOAT,
#     course FLOAT,
#     heading FLOAT,
#     timeStamp DATETIME,
#     time_queried DATETIME default now(),
#     PRIMARY KEY (`id`)
# );
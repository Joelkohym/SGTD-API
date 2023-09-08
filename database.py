from sqlalchemy import create_engine, text
import pandas as pd
import os

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
    print(f"receive_data == {receive_data}, return api ={receive_data[3]}, return pID = {receive_data[4]}, return pitstop = {receive_data[5]}")
  return(receive_data[0],receive_data[3],receive_data[4],receive_data[5],receive_data[6])


def new_vessel_current_position(data, email):
  with engine.connect() as conn:
    query = text("select * from userDB WHERE email = :email")
    values = {'email' : email}
    result = conn.execute(query, values)
    result_all = result.fetchall()
    #result_all = result.all()
    print(result_all)
    print(f"length of result all = {len(result_all)}")
    if len(result_all) > 0:
      db_connection_string_vcp = result_all[0][6]
      engine_vcp = create_engine(db_connection_string_vcp,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
      with engine.connect() as conn:
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
    else:
      print('User exists, please try again')
      return 0


def new_vessel_movement(data, email):
  with engine.connect() as conn:
    query = text("select * from userDB WHERE email = :email")
    values = {'email' : email}
    result = conn.execute(query, values)
    result_all = result.all()
    print(result_all)
    print(f"length of result all = {len(result_all)}")
    if len(result_all) > 0:
      db_connection_string_vcp = result_all[0][6]
      engine_vcp = create_engine(db_connection_string_vcp,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
      with engine.connect() as conn:
        query_vm = text("INSERT INTO vessel_movement_UCE (    vessel_nm,vessel_imo_no,vessel_flag,vessel_call_sign,vessel_location_from,vessel_location_to,vessel_movement_height,vessel_movement_type,vessel_movement_start_dt,vessel_movement_end_dt,vessel_movement_status,vessel_movement_draft) VALUES (:vessel_nm,:vessel_imo_no,:vessel_flag,:vessel_call_sign,:vessel_location_from,:vessel_location_to,:vessel_movement_height,:vessel_movement_type,:vessel_movement_start_dt,:vessel_movement_end_dt,:vessel_movement_status,:vessel_movement_draft)")
        
        values_vm = {'vessel_nm':data['vm_vessel_particulars.vessel_nm'],'vessel_imo_no':data['vm_vessel_particulars.vessel_imo_no'],'vessel_flag':data['vm_vessel_particulars.vessel_flag'],'vessel_call_sign': data['vm_vessel_particulars.vessel_call_sign'],'vessel_location_from': data['vm_vessel_location_from'],'vessel_location_to':data['vm_vessel_location_to'],'vessel_movement_height': data['vm_vessel_movement_height'],'vessel_movement_type':data['vm_vessel_movement_type'],'vessel_movement_start_dt':data['vm_vessel_movement_start_dt'],'vessel_movement_end_dt':data['vm_vessel_movement_end_dt'],'vessel_movement_status':data['vm_vessel_movement_status'],'vessel_movement_draft':data['vm_vessel_movement_draft']}

        result = conn.execute(query_vm, values_vm)
      print("New vessel_current_position execute success")
      return 1
    else:
      print('User exists, please try again')
      return 0


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
    query = text("select * from vessel_current_position_UCE")
    result_VCP = conn.execute(query)
    result_all_VCP = result_VCP.fetchall()
    column_names_VCP = result_VCP.keys() 
    print(result_all_VCP)
    print(f"length of result_all_VCP = {len(result_all_VCP)}")
    df2 = pd.DataFrame(result_all_VCP, columns=column_names_VCP)
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
    query_VM = text("DELETE FROM vessel_movement_UCE where id > 1")
    result_VM = conn.execute(query_VM)
    query_VCP = text("DELETE FROM vessel_current_position_UCE where id > 1")
    result_VCP = conn.execute(result_VCP)
  
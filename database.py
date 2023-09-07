from sqlalchemy import create_engine, text
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
    result_all = result.all()
    print(result_all)
    print(f"length of result all = {len(result_all)}")
    if len(result_all) > 0:
      db_connection_string_vcp = result_all[0][6]
      engine_vcp = create_engine(db_connection_string_vcp,connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
      with engine.connect() as conn:
        query = text("INSERT INTO vessel_current_position_UCE (    vessel_nm,vessel_imo_no,vessel_flag,vessel_call_sign,vessel_location_from,vessel_location_to,vessel_movement_height,vessel_movement_type,vessel_movement_start_dt,vessel_movement_end_dt,vessel_movement_status,vessel_movement_draft,Timestamp_vessel_movement) VALUES (:vessel_nm,:vessel_imo_no,:vessel_flag,:vessel_call_sign,:vessel_location_from,:vessel_location_to,:vessel_movement_height,:vessel_movement_type,:vessel_movement_start_dt,:vessel_movement_end_dt,:vessel_movement_status,:vessel_movement_draft,:Timestamp_vessel_movement)")
        values = {'vessel_nm,vessel_imo_no':data['vessel_nm,vessel_imo_no'],vessel_flag,vessel_call_sign,vessel_location_from,vessel_location_to,vessel_movement_height,vessel_movement_type,vessel_movement_start_dt,vessel_movement_end_dt,vessel_movement_status,vessel_movement_draft,Timestamp_vessel_movement
        values = {'email' : data['email'], 'password' : data['password'], 'api_key' : data['api_key'], 'participant_id' :data['participant_id'], 'pitstop_url':data['pitstop_url'],'gsheet_cred_path' : data['gsheet_cred_path']}
        print(query)
        result = conn.execute(query, values)
      print("execute success")
      return 1
    else:
      print('User exists, please try again')
      return 0


    email = email_url
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
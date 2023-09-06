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
    result_all = result.all()
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
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

def load_user_from_db(username, password):
  with engine.connect() as conn:
    username_ = username
    password_ = password
    result = conn.execute(text("select * from userDB WHERE username = :username_ and password = :password_"))
    result_all = result.all()
    if len(result_all) == 0:
      return None
    else:
      return dict(rows[0])
    print(f"result = {result_all}")
  return user_data

# def new_registration(username, password, api_key, participant_id, on_behalf_id, gsheet_cred_path, company):
def new_registration(data):
  print(f"printing data from new_registration: {data}")
  print(f"data['username_'] == {data['username_']}")
  print(f"data['api_key_'] == {data['api_key_']}")
  print(f"data['participant_id_'] == {data['participant_id_']}")
  print(f"data['on_behalf_id_'] == {data['on_behalf_id_']}")
  with engine.connect() as conn:
    #query = text("INSERT INTO userDB (username_, password_, api_key_, participant_id_, on_behalf_id_, gsheet_cred_path_, company_) VALUES (:username_, :password_, :api_key_, :participant_id_, :on_behalf_id_, :gsheet_cred_path_, :company_)")
    query = text("INSERT INTO userDB (username_, password_, api_key_, participant_id_, on_behalf_id_, gsheet_cred_path_, company_) VALUES (:username_,:password_, :api_key_, :participant_id_, :on_behalf_id_, :gsheet_cred_path_, :company_)")
    values = {'username_' : data['username_'], 'password_' : data['password_'], 'api_key_' : data['api_key_'], 'participant_id_' :data['participant_id_'], 'on_behalf_id_' : data['on_behalf_id_'], 'gsheet_cred_path_' : data['gsheet_cred_path_'], 'company_' : data['company_']}
    print(query)
    conn.execute(query, values)
    #conn.execute(query, username_ = data['username_'],password_ =data['password_'],api_key_ = data['api_key_'],participant_id_ = data['participant_id_'],on_behalf_id_ = data['on_behalf_id_'],gsheet_cred_path_ = data['gsheet_cred_path_'], company_ = data['company_'])
    print("execute success")


def validate_login(username, password):
  print(f"printing data from validate_login: username = {username}, password = {password}")

  with engine.connect() as conn:
    query = text("SELECT * FROM userDB WHERE username_ = :username_ AND password_ = :password_")
    values = {'username_' : username, 'password_' : password}
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
      return (login_entry[3],login_entry[4],login_entry[5], login_entry[6])
    else:
      print("Error in Login")
      return 0

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
  with engine.connect() as conn:
    query = text("INSERT INTO userDB (username_, password_, api_key_, participant_id_, on_behalf_id_, gsheet_cred_path_, company_) VALUES (:username_, :password_, :api_key_, :participant_id_, :on_behalf_id_, :gsheet_cred_path_, :company_)")
    conn.execute(query, username_ = data['username_'],
    password_ =data['password_'],
    api_key_ = data['api_key_'],
    participant_id_ = data['participant_id'],
    on_behalf_id_ = data['on_behalf_id'],
    gsheet_cred_path_ = data['gsheet_cred_path'], 
    company_ = data['company'])


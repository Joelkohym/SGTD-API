from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://jhf1ksg5tmrpia7hl6n1:pscale_pw_pCHorRp8Lw1r9NHKnRmWcSrcB3pkvmu81cv2wS5HsaT@aws.connect.psdb.cloud/sgtd?charset=utf8mb4"
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
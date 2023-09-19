from sqlalchemy import create_engine, text
import pandas as pd
import os
import json

# db_connection_string = os.environ['DB_CONNECTION_STRING']
db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(
  db_connection_string,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})



def get_table_data(db_creds):
  print("Start of get_table_data......")
  engine = create_engine(
  db_creds,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})
  with engine.connect() as conn:
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
    print(f"df3 = {df3}")
    print(f"df2= {df2}")
    df3.drop(columns=['call_sign','flag','vessel_name','purpose'], inplace=True)
    #   df3.rename(columns={'key_0': 'renamed_key_0'}, inplace=True)
    # if 'key_0' in df2.columns:
    #   df2.drop(columns=['key_0'], inplace=True)
    new_df = pd.merge(df2,
                   df3,
                   left_on=df2['imoNumber'],
                   right_on=df3['imo_number'],
                   how='inner')
    if 'key_0' in new_df.columns:
      new_df.drop(columns=['key_0'], inplace=True)
    print(f"new_df= {new_df}")
    print(f"Final Result all vm = {[new_df]}")
    return [new_df]
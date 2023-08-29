from flask import Flask, render_template, jsonify, request
import requests
import json
import pygsheets
from datetime import datetime
import pandas as pd
import leafmap.foliumap as leafmap
import random

app = Flask(__name__)

colors = [
  "red", "green", "blue", "yellow", "violet", "indigo", "orange", "black",
  "purple", "grey", "silver", "gold"
]


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


@app.route("/api/vessel")
def Vessel_movement():
  API_Key = 'VJN5vqP8LfZxVCycQT6PvpJ0VM4Vk2pW'
  vessel_imo = "9702699"
  url_vessel_movement = "https://sgtradexdummy-lbo.pitstop.uat.sgtradex.io/api/v1/data/pull/vessel_movement"
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
      "vessel_imo_no": vessel_imo
    },
    "on_behalf_of": [{
      "id": on_behalf_of_id
    }]
  }
  json_string = json.dumps(
    payload, indent=4)  # Convert payload dictionary to JSON string
  # Rest of the code to send the JSON payload to the API
  data = json.loads(json_string)
  response_vessel_movement = requests.post(
    url_vessel_movement, json=data, headers={'SGTRADEX-API-KEY': API_Key})
  if response_vessel_movement.status_code == 200:
    print(f"Response JSON = {response_vessel_movement.json()}")
    print("Pull vessel_movement success.")
  else:
    print(
      f"Failed to PULL vessel_movement data. Status code: {response_vessel_movement.status_code}"
    )
    print(response_vessel_movement.text)
  return response_vessel_movement.text


@app.route("/api/vessel_movement/receive", methods=['POST'])
def Vessel_movement_receive(formName=None):
  try:
    data = request.data  # Get the raw data from the request body
    #print(data)
    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    # Extract the last item from the "payload" array
    last_payload_item = data_dict['payload'][-1]
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

    # Append the data to the worksheet
    print(f"row_data_vessel_movement: {row_data_vessel_movement}")
    # Add the current date and time to your data dictionary
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data_vessel_movement['Timestamp'] = current_datetime
    gc = pygsheets.authorize(service_account_file='creds.json')
    print(gc.spreadsheet_titles())
    sh = gc.open('SGTD Received APIs')
    worksheet_replit = sh.worksheet_by_title("replit_vessel_movement")

    #clear
    worksheet_replit.clear()

    # Write the headers as the first row
    worksheet_replit.insert_rows(row=1,
                                 number=1,
                                 values=list(row_data_vessel_movement.keys()))
    # Append the data as a new row
    worksheet_replit.append_table(
      start='A2',  # You can specify the starting cell here
      end=None,  # You can specify the ending cell if needed
      values=list(row_data_vessel_movement.values()))
    print([list(row_data_vessel_movement.values())])
    return "Data saved to Google Sheets."
  except Exception as e:
    # Handle the error gracefully and log it
    print("An error occurred:", str(e))
    return f"An error occurred: {str(e)}", 500  # Return a 500


@app.route("/api/vessel_current_location/receive", methods=['POST'])
def Vessel_movement_current_location(formName=None):
  try:

    data = request.data  # Get the raw data from the request body
    print(data)
    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_vessel_current_location = data_dict['payload'][-1]
    # Add the current date and time to your data dictionary
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data_vessel_current_location['Timestamp'] = current_datetime
    print(
      f"row_data_vessel_current_location: {row_data_vessel_current_location}")
    gc = pygsheets.authorize(service_account_file='creds.json')
    print(gc.spreadsheet_titles())
    sh = gc.open('SGTD Received APIs')
    worksheet_replit = sh.worksheet_by_title("replit_vessel_current_location")

    #clear
    worksheet_replit.clear()

    # Write the headers as the first row
    worksheet_replit.insert_rows(row=1,
                                 number=1,
                                 values=list(
                                   row_data_vessel_current_location.keys()))
    # Append the data as a new row
    worksheet_replit.append_table(
      start='A2',  # You can specify the starting cell here
      end=None,  # You can specify the ending cell if needed
      values=list(row_data_vessel_current_location.values()))
    return "Vessel Current Location Data saved to Google Sheets."
  except Exception as e:
    # Handle the error gracefully and log it
    print("An error occurred:", str(e))
    return f"An error occurred: {str(e)}", 500  # Return a 500


@app.route("/api/vessel_map", methods=['POST'])
def Vessel_map(formName=None):
  # Assuming you have two sheets named 'Sheet1' and 'Sheet2'
  gc = pygsheets.authorize(service_account_file='creds.json')
  print(gc.spreadsheet_titles())
  sh = gc.open('SGTD Received APIs')
  sheet1 = sh.worksheet_by_title('Sheet1')
  sheet2 = sh.worksheet_by_title('Sheet2')
  # Read data from 'Sheet1' into a DataFrame
  df1 = pd.DataFrame(sheet1.get_all_records())

  # Read data from 'Sheet2' into another DataFrame
  df2 = pd.DataFrame(sheet2.get_all_records())
  # Assuming 'imo_no' is the common column
  merged_df = pd.merge(df1, df2, left_on='vessel_particulars.vessel_imo_no', right_on='vm_vessel_particulars.vessel_imo_no', how='inner')




  
  m = leafmap.Map(center=[1.257167, 103.897], zoom=12)
  regions = 'static/SG_anchorages.geojson'
  m.add_geojson(regions,
                layer_name='SG Anchorages',
                style={
                  "color": (random.choice(colors)),
                  "fill": True,
                  "fillOpacity": 0.05
                })
  m.to_html("templates/mymap.html")
  #m.to_html("mymap.html")
  return render_template('mymap.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

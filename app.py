from flask import Flask, render_template, jsonify, request
import requests
import json
import pygsheets
import os

app = Flask(__name__)
#my_secret = os.environ['GSHEET_API_CREDENTIALS']
#print(my_secret)
#service_account_info = json.loads(my_secret)
# my_credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
#gc = pygsheets.authorize(service_account_json=my_secret)

# Set up OAuth2 credentials using your JSON credentials file
scope = [
  "https://spreadsheets.google.com/feeds",
  "https://www.googleapis.com/auth/drive"
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






@app.route("/api/vessel/receive", methods=['POST'])
def Vessel_movement_receive(formName=None):
  try:
    data = request.data  # Get the raw data from the request body
    print(data)
    data_str = data.decode('utf-8')  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    # Extract the last item from the "payload" array
    last_payload_item = data_dict['payload'][-1]
    # # Open the Google Sheets spreadsheet by title or URL
    # spreadsheet = gc.open(
    #   "https://docs.google.com/spreadsheets/d/1yvUCUCfZsTPSMf88i9JoZocSsSm7iyclVCimCGpuTEk/edit#gid=0"
    # )
    # # Select a specific worksheet within the spreadsheet
    # worksheet = spreadsheet.worksheet(
    #   "replit")  # Change the sheet name if needed
    # Create a dictionary to map column names to values
    row_data = {
            "vm_vessel_particulars.vessel_nm": last_payload_item['vm_vessel_particulars'][0]['vessel_nm'],
            "vm_vessel_particulars.vessel_imo_no": last_payload_item['vm_vessel_particulars'][0]['vessel_imo_no'],
            "vm_vessel_particulars.vessel_flag": last_payload_item['vm_vessel_particulars'][0]['vessel_flag'],
            "vm_vessel_particulars.vessel_call_sign": last_payload_item['vm_vessel_particulars'][0]['vessel_call_sign'],
            "vm_vessel_location_from": last_payload_item['vm_vessel_location_from'],
            "vm_vessel_location_to": last_payload_item['vm_vessel_location_to'],
            "vm_vessel_movement_height": last_payload_item['vm_vessel_movement_height'],
            "vm_vessel_movement_type": last_payload_item['vm_vessel_movement_type'],
            "vm_vessel_movement_start_dt": last_payload_item['vm_vessel_movement_start_dt'],
            "vm_vessel_movement_end_dt": last_payload_item['vm_vessel_movement_end_dt'],
            "vm_vessel_movement_status": last_payload_item['vm_vessel_movement_status'],
            "vm_vessel_movement_draft": last_payload_item['vm_vessel_movement_draft']
        }

        # Append the data to the worksheet
    print(row_data)
    #worksheet.append_table(values=[list(row_data.values())])
    return "Data saved to Google Sheets."
  except Exception as e:
    # Handle the error gracefully and log it
    print("An error occurred:", str(e))
    return f"An error occurred: {str(e)}", 500  # Return a 500 

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
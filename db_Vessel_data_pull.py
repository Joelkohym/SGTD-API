from sqlalchemy import create_engine, text
import pandas as pd
import os
import json
from datetime import datetime
import requests
import threading


def delete_all_rows_vessel_location(db_creds):
    print(
        "Start of delete_all_rows_vessel_location 3 tables: vessel_movement_UCE, vessel_current_position_UCE, MPA_vessel_data......"
    )
    engine = create_engine(
        db_creds, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
    )
    with engine.connect() as conn:
        # query_VM = text("DELETE FROM vessel_movement_UCE where id > 0")
        # result_VM = conn.execute(query_VM)
        # print("Deleted vessel_movement_UCE where id > 0")
        query_VCP = text("DELETE FROM vessel_current_position_UCE where id > 0")
        result_VCP = conn.execute(query_VCP)
        print("Deleted vessel_current_position_UCE where id > 0")
        query_MPA = text("DELETE FROM MPA_vessel_data WHERE id > 0")
        result_MPA = conn.execute(query_MPA)
        print("Deleted MPA_vessel_data where id > 0")


# ============= GET 2 API's from MPA: VCP + VDA ===================
# ============= PULL 2 API's from SGTD: VCP + VDA =================
def PULL_GET_VCP_VDA_MPA(
    input_list,
    session_pitstop,
    session_gc,
    session_participant_id,
    session_api_key,
    session_imo_not_found,
):
    current_datetime = datetime.now().strftime("%Y-%m-%d")
    for vessel_imo in input_list:
        print(f"IMO Number = {vessel_imo}")

        # url_vessel_movement = f"{session_pitstop}/api/v1/data/pull/vessel_movement"
        url_vessel_current_position = (
            f"{session_pitstop}/api/v1/data/pull/vessel_current_position"
        )
        url_vessel_due_to_arrive = (
            f"{session_pitstop}/api/v1/data/pull/vessel_due_to_arrive"
        )
        url_MPA_VCP = (
            f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/positions/imonumber/{vessel_imo}"
        )
        url_MPA_arrivaldeclaration = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/arrivaldeclaration/imonumber/{vessel_imo}"

        ##################### START Make the GET request for MPA_vessel_data table LOCATION VCP ALT  #####################
        API_KEY_MPA = "QgCv2UvINPRfFqbbH3yVHRVVyO8Iv5CG"
        r_GET = requests.get(url_MPA_VCP, headers={"Apikey": API_KEY_MPA})

        # Check the response
        if r_GET.status_code == 200:
            print("Config Data retrieved successfully!")
            # Store GET data from MPA into MPA_vessel_data table table
            MPA_GET(r_GET.text, session_gc)
        else:
            NOT_FOUND_LIST = session_imo_not_found
            NOT_FOUND_LIST.append(vessel_imo)
            session_imo_not_found = NOT_FOUND_LIST
            print(f"Failed to get Config Data. Status code: {r_GET.status_code}")
        ##################### END Make the GET request for MPA_vessel_data table LOCATION VCP ALT  #####################
        ##################### START Make the GET request for MPA_arrivaldeclaration table ETA  #####################
        r_GET_arrivaldeclaration = requests.get(
            url_MPA_arrivaldeclaration, headers={"Apikey": API_KEY_MPA}
        )
        if r_GET_arrivaldeclaration.status_code == 200:
            print("Config Data retrieved successfully!")
            print(r_GET_arrivaldeclaration.text)

            # Store GET data from MPA into MPA_arrivaldeclaration table
            MPA_GET_arrivaldeclaration(r_GET_arrivaldeclaration.text, session_gc)
        else:
            print(
                f"Failed to get Config Data for arrivaldeclaration. Status code: {r_GET_arrivaldeclaration.status_code}"
            )
            print(r_GET_arrivaldeclaration.text)
        ##################### END Make the GET request for MPA_arrivaldeclaration table ETA  #####################
        print("Start PULL_SGTD_VCP_VDA thread...")
        print(datetime.now())
        threading.Thread(
            target=PULL_VCP_VDA_SGTD,
            args=(
                session_participant_id,
                vessel_imo,
                current_datetime,
                url_vessel_current_position,
                url_vessel_due_to_arrive,
                session_api_key,
            ),
        ).start()
        print("End PULL_SGTD_VCP_VDA  thread...")
        print(datetime.now())


def PULL_VCP_VDA_SGTD(
    session_participant_id,
    vessel_imo,
    current_datetime,
    url_vessel_current_position,
    url_vessel_due_to_arrive,
    session_api_key,
):
    # ========================    PULL payload for vessel_current_position and vessel_movement    ===========================
    if session_participant_id == "49f04a6f-f157-479b-b211-18931fad4ca4":
        payload_id = "1817878d-c468-411b-8fe1-698eca7170dd"
    else:
        payload_id = "4c22b7a7-b583-4b6a-baae-e9f38d94beed"
    payload = {
        "participants": [
            {
                "id": payload_id,
                "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
                "meta": {"data_ref_id": ""},
            }
        ],
        "parameters": {"vessel_imo_no": str(vessel_imo)},
        "on_behalf_of": [{"id": session_participant_id}],
    }

    payload_VDA = {
        "participants": [
            {
                "id": payload_id,
                "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
                "meta": {"data_ref_id": ""},
            }
        ],
        "parameters": {"vda_vessel_due_to_arrive_dt": current_datetime},
        "on_behalf_of": [{"id": session_participant_id}],
    }

    json_string = json.dumps(
        payload, indent=4
    )  # Convert payload dictionary to JSON string
    # Rest of the code to send the JSON payload to the API
    data = json.loads(json_string)

    json_string_VDA = json.dumps(
        payload_VDA, indent=4
    )  # Convert payload dictionary to JSON string
    # Rest of the code to send the JSON payload to the API
    data_VDA = json.loads(json_string_VDA)
    # ========================    PULL vessel_current_position     ===========================
    PULL_vessel_current_position = requests.post(
        url_vessel_current_position,
        json=data,
        headers={"SGTRADEX-API-KEY": session_api_key},
    )
    if PULL_vessel_current_position.status_code == 200:
        print(f"Response JSON = {PULL_vessel_current_position.json()}")
        print("Pull vessel_current_position success.")
    else:
        print(
            f"Failed to PULL vessel_current_position data. Status code: {PULL_vessel_current_position.status_code}"
        )

    # ========================    PULL vessel_due_to_arrive    ===========================
    PULL_vessel_due_to_arrive = requests.post(
        url_vessel_due_to_arrive,
        json=data_VDA,
        headers={"SGTRADEX-API-KEY": session_api_key},
    )
    if PULL_vessel_due_to_arrive.status_code == 200:
        print(f"Response JSON = {PULL_vessel_due_to_arrive .json()}")
        print("Pull vessel_due_to_arrive success.")
    else:
        print(
            f"Failed to PULL vessel_due_to_arrive data. Status code: {PULL_vessel_due_to_arrive.status_code}"
        )
    # ========================    PULL vessel_movement     =====================================
    # response_vessel_movement = requests.post(
    #     url_vessel_movement,
    #     json=data,
    #     headers={"SGTRADEX-API-KEY": session["api_key"]},
    # )
    # if response_vessel_movement.status_code == 200:
    #     print("Pull vessel_movement success.")
    # else:
    #     print(
    #         f"Failed to PULL vessel_movement data. Status code: {response_vessel_movement.status_code}"
    #     )
        

# Store data into MPA_vessel_data from GET
def MPA_GET(api_response, gsheet_cred_path):
    data_list = json.loads(api_response)
    print(f"API response = {(data_list)}")
    print(f"API response[0] = {data_list[0]}")
    vessel_data = data_list[0]["vesselParticulars"]
    print(f"vessel_data = {vessel_data}")
    print(f"vessel_data['vesselName'] = {vessel_data['vesselName']}")
    print(f"vessel_data['callSign'] = {vessel_data['callSign']}")
    latitude = data_list[0]["latitude"]
    print(f"latitude = {data_list[0]['latitude']}")
    longitude = data_list[0]["longitude"]
    latitude_degrees = data_list[0]["latitudeDegrees"]
    longitude_degrees = data_list[0]["longitudeDegrees"]
    speed = data_list[0]["speed"]
    course = data_list[0]["course"]
    heading = data_list[0]["heading"]
    timestamp = data_list[0]["timeStamp"]

    query = text(
        "INSERT INTO MPA_vessel_data (vesselName, callSign, imoNumber, flag, vesselLength, vesselBreadth, vesselDepth, vesselType, grossTonnage, netTonnage, deadweight, mmsiNumber, yearBuilt, latitude, longitude, latitudeDegrees, longitudeDegrees, speed, course, heading, timeStamp) VALUES (:vesselName, :callSign, :imoNumber, :flag, :vesselLength, :vesselBreadth, :vesselDepth, :vesselType, :grossTonnage, :netTonnage, :deadweight, :mmsiNumber, :yearBuilt, :latitude, :longitude, :latitudeDegrees, :longitudeDegrees, :speed, :course, :heading, :timeStamp)"
    )
    values = {
        "vesselName": vessel_data["vesselName"],
        "callSign": vessel_data["callSign"],
        "imoNumber": vessel_data["imoNumber"],
        "flag": vessel_data["flag"],
        "vesselLength": vessel_data["vesselLength"],
        "vesselBreadth": vessel_data["vesselBreadth"],
        "vesselDepth": vessel_data["vesselDepth"],
        "vesselType": vessel_data["vesselType"],
        "grossTonnage": vessel_data["grossTonnage"],
        "netTonnage": vessel_data["netTonnage"],
        "deadweight": vessel_data["deadweight"],
        "mmsiNumber": vessel_data["mmsiNumber"],
        "yearBuilt": vessel_data["yearBuilt"],
        "latitude": latitude,
        "longitude": longitude,
        "latitudeDegrees": latitude_degrees,
        "longitudeDegrees": longitude_degrees,
        "speed": speed,
        "course": course,
        "heading": heading,
        "timeStamp": timestamp,
    }
    engine_MPA_GET = create_engine(
        gsheet_cred_path, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
    )
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
        if reported_arrival_time and (
            latest_time is None or reported_arrival_time > latest_time
        ):
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
    query = text(
        """
      INSERT INTO MPA_arrivaldeclaration (
          vessel_name, call_sign, imo_number, flag, 
          location, grid, purpose, agent, reported_arrival_time
      ) VALUES (
          :vessel_name, :call_sign, :imo_number, :flag, 
          :location, :grid, :purpose, :agent, :reported_arrival_time
      )
  """
    )

    # Prepare the values
    values = {
        "vessel_name": vessel_data["vesselParticulars"]["vesselName"],
        "call_sign": vessel_data["vesselParticulars"]["callSign"],
        "imo_number": vessel_data["vesselParticulars"]["imoNumber"],
        "flag": vessel_data["vesselParticulars"]["flag"],
        "location": vessel_data["location"],
        "grid": vessel_data["grid"],
        "purpose": vessel_data["purpose"],
        "agent": vessel_data["agent"],
        "reported_arrival_time": vessel_data["reportedArrivalTime"],
    }

    engine_MPA_arrivaldeclaration = create_engine(
        gsheet_cred_path, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
    )
    with engine_MPA_arrivaldeclaration.connect() as conn:
        MPA_arrivaldeclaration = conn.execute(query, values)
    return MPA_arrivaldeclaration

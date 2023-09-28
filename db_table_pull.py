from sqlalchemy import create_engine, text
import pandas as pd
import os
import json
import requests
import time
from datetime import datetime, timedelta
import pytz


def delete_all_rows_table_view(db_creds):
    print("Start of delete_all_rows_table_view 2 tables: MPA_arrivaldeclaration......")
    engine = create_engine(
        db_creds, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
    )
    with engine.connect() as conn:
        query_VM = text("DELETE FROM MPA_arrivaldeclaration where id > 0")
        result_VM = conn.execute(query_VM)
        print("Deleted vessel_movement_UCE where id > 0")
        query_VCP = text("DELETE FROM MPA_vessel_data where id > 0")
        result_VCP = conn.execute(query_VCP)
        print("Deleted MPA_vessel_data where id > 0")
        query_VDA = text("DELETE FROM vessel_due_to_arrive_UCE where id > 0")
        result_VDA = conn.execute(query_VDA)
        print("Deleted vessel_due_to_arrive_UCE; where id > 0")
        query_PS = text("DELETE FROM pilotage_service_UCE where id > 0")
        result_PS = conn.execute(query_PS)
        print("Deleted pilotage_service_UCE where id > 0")


def PULL_pilotage_service(
    url_pilotage_service, input_list, session_participants_id, session_api_key
):
    # Loop through input IMO list
    tic = time.perf_counter()
    for vessel_imo in input_list:
        payload = {
            "participants": [
                {
                    "id": "string",
                    "name": "string",
                    "meta": {"data_ref_id": ""},
                }
            ],
            "parameters": {"pilotage_imo": str(vessel_imo)},
            "on_behalf_of": [{"id": session_participants_id}],
        }

        json_string = json.dumps(
            payload, indent=4
        )  # Convert payload dictionary to JSON string
        # Rest of the code to send the JSON payload to the API
        data = json.loads(json_string)

        response_pilotage_service = requests.post(
            url_pilotage_service,
            json=data,
            headers={"SGTRADEX-API-KEY": session_api_key},
        )
        if response_pilotage_service.status_code == 200:
            # print(f"Response JSON = {response_vessel_current_position.json()}")
            print("Pull pilotage service success.")
        else:
            print(
                f"Failed to PULL pilotage service data. Status code: {response_pilotage_service.status_code}"
            )
    toc = time.perf_counter()
    print(
        f"PULL duration for pilotage service {len(input_list)} in {toc - tic:0.4f} seconds"
    )
    # ========================          END PULL pilotage_service                         ===========================


def PULL_vessel_due_to_arrive(
    url_vessel_due_to_arrive, session_participants_id, session_api_key
):
    # Define your local time zone (UTC+9)
    local_timezone = pytz.timezone("Asia/Singapore")
    # Get the current date and time in UTC
    current_utc_datetime = datetime.now(pytz.utc)
    # Convert the current UTC time to your local time zone
    current_local_datetime = current_utc_datetime.astimezone(local_timezone)
    # Calculate tomorrow's date in your local time zone
    tomorrow_local_datetime = (current_utc_datetime + timedelta(days=1)).astimezone(
        local_timezone
    )
    # Calculate the day after tomorrow's date in your local time zone
    day_after_tomorrow_local_datetime = (
        current_utc_datetime + timedelta(days=2)
    ).astimezone(local_timezone)
    print(
        "Current Local Date and Time:",
        current_local_datetime.strftime("%Y-%m-%d"),
    )
    today_date = current_local_datetime.strftime("%Y-%m-%d")
    print("Tomorrow's Local Date:", tomorrow_local_datetime.strftime("%Y-%m-%d"))
    tomorrow_date = tomorrow_local_datetime.strftime("%Y-%m-%d")
    print(
        "Day After Tomorrow's Local Date:",
        day_after_tomorrow_local_datetime.strftime("%Y-%m-%d"),
    )
    dayafter_date = day_after_tomorrow_local_datetime.strftime("%Y-%m-%d")

    # Loop through 3 days
    tic = time.perf_counter()
    for i in range(3):
        if i == 0:
            pull_date = today_date
        elif i == 1:
            pull_date = tomorrow_date
        elif i == 2:
            pull_date = dayafter_date

        payload = {
            "participants": [
                {
                    "id": "1817878d-c468-411b-8fe1-698eca7170dd",
                    "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
                    "meta": {"data_ref_id": ""},
                }
            ],
            "parameters": {"vda_vessel_due_to_arrive_dt": str(pull_date)},
            "on_behalf_of": [{"id": session_participants_id}],
        }

        json_string = json.dumps(
            payload, indent=4
        )  # Convert payload dictionary to JSON string
        # Rest of the code to send the JSON payload to the API
        data = json.loads(json_string)

        response_vessel_due_to_arrive = requests.post(
            url_vessel_due_to_arrive,
            json=data,
            headers={"SGTRADEX-API-KEY": session_api_key},
        )
        if response_vessel_due_to_arrive.status_code == 200:
            # print(f"Response JSON = {response_vessel_current_position.json()}")
            print("Pull vessel_due_to_arrive success.")
        else:
            print(
                f"Failed to PULL vessel_due_to_arrive data. Status code: {response_vessel_due_to_arrive.status_code}"
            )
    toc = time.perf_counter()
    print(f"PULL duration for vessel_due_to_arrive in {toc - tic:0.4f} seconds")
    # ========================    END PULL vessel_due_to_arrive         ===========================

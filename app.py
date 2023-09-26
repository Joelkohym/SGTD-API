from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_mysqldb import MySQL
from sqlalchemy import create_engine, text
import re
import requests
import json
import pygsheets
from datetime import datetime, timedelta
import pandas as pd
import leafmap.foliumap as leafmap
import folium
import random
import time
import pytz 
import os
from database import load_data_from_db, new_registration, validate_login, receive_details, new_vessel_movement, new_vessel_current_position, get_map_data, delete_all_rows_vessel_location, MPA_GET, new_pilotage_service, MPA_GET_arrivaldeclaration, new_vessel_due_to_arrive
from database_table import get_table_data, delete_all_rows_table_view, get_data_from_vessel_due_to_arrive_and_depart



app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']

app.secret_key = os.urandom(24)

mysql = MySQL(app)

db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(
  db_connection_string,
  connect_args={
  "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"}})


colors = [
"red","blue","green","purple","orange","darkred","lightred","beige","darkblue","darkgreen","cadetblue","darkpurple","white","pink","lightblue","lightgreen","gray","black","lightgray"
]



    
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        msg = ""
        try:
            email = request.form["email"]
            password = request.form["password"]
            login_data = validate_login(email, password)
            # print(f"Validate_login value returned = {validate_login(email, password)}")
            if len(login_data) == 5:
                id = login_data[0]
                API_KEY = login_data[1]
                pID = login_data[2]
                pitstop = login_data[3]
                gSheet = login_data[4]

                session["loggedin"] = True
                session["id"] = id
                session["email"] = email
                session["participant_id"] = pID
                session["pitstop_url"] = pitstop
                session["api_key"] = API_KEY
                session["gc"] = gSheet
                session["IMO_NOTFOUND"] = []

                msg = f"Login success for {email}, please enter Vessel IMO number(s)"
                print(f"Login success for {email}, redirect")
                return redirect(url_for("table_view"))
                # return render_template('vessel_request.html', msg=msg, email=email)
            else:
                msg = "Invalid credentials, please try again.."
                print("Invalid credentials, reset login")
                return render_template("login.html", msg=msg)
        except Exception as e:
            msg = "Invalid credentials, please try again."
            print("Invalid credentials, reset login")
            return render_template("login.html", msg=msg)
            # if request.data['username'] and request.data['password'] in db:
            #   user_data = load_data_from_db()
    if request.method == "GET":
        print("Requets == GET")
        return render_template("login.html")


@app.route("/table_view", methods=["GET", "POST"])
def table_view():
    if g.user:
        email = session["email"]
        return render_template("table_view.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/api/table_pull", methods=["GET", "POST"])
def table_pull():
    if g.user:
        if request.method == "POST":
            session["IMO_NOTFOUND"] = []
            session["TABLE_IMO_NOTFOUND"] = []
            # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
            print(f'Session gc = {session["gc"]}')
            ############################   MIGHT NEED TO UNCOMMENT   ##############
            #delete_all_rows_table_view(session["gc"])
            user_vessel_imo = request.form["imo"]
            # Split vessel_imo list into invdivual records
            input_list = [int(x) for x in user_vessel_imo.split(",")]
            print(f"Pilotage service input_list from html = {input_list}")



          
            # ========================              START PULL pilotage_service by vessel imo                   ===========================
            # url_pilotage_service = (
            #     f"{session['pitstop_url']}/api/v1/data/pull/pilotage_service"
            # )
            # # Loop through input IMO list
            # tic = time.perf_counter()
            # for vessel_imo in input_list:
            #     payload = {
            #         "participants": [
            #             {
            #                 "id": "string",
            #                 "name": "string",
            #                 "meta": {"data_ref_id": session["email"]},
            #             }
            #         ],
            #         "parameters": {"pilotage_imo": str(vessel_imo)},
            #         "on_behalf_of": [{"id": session["participant_id"]}],
            #     }

            #     json_string = json.dumps(
            #         payload, indent=4
            #     )  # Convert payload dictionary to JSON string
            #     # Rest of the code to send the JSON payload to the API
            #     data = json.loads(json_string)

            #     response_pilotage_service = requests.post(
            #         url_pilotage_service,
            #         json=data,
            #         headers={"SGTRADEX-API-KEY": session["api_key"]},
            #     )
            #     if response_pilotage_service.status_code == 200:
            #         # print(f"Response JSON = {response_vessel_current_position.json()}")
            #         print("Pull pilotage service success.")
            #     else:
            #         print(
            #             f"Failed to PULL pilotage service data. Status code: {response_pilotage_service.status_code}"
            #         )
            # toc = time.perf_counter()
            # print(
            #     f"PULL duration for pilotage service {len(input_list)} in {toc - tic:0.4f} seconds"
            # )
            # ========================          END PULL pilotage_service                         ===========================




          
            # ========================          START PULL vessel_due_to_arrive by date            ===========================
            url_vessel_due_to_arrive = (
                f"{session['pitstop_url']}/api/v1/data/pull/vessel_due_to_arrive"
            )
            today_datetime = datetime.now().strftime("%Y-%m-%d")
            # Define your local time zone (UTC+9)
            local_timezone = pytz.timezone("Asia/Singapore")
            # Get the current date and time in UTC
            current_utc_datetime = datetime.now(pytz.utc)
            # Convert the current UTC time to your local time zone
            current_local_datetime = current_utc_datetime.astimezone(local_timezone)
            # Calculate tomorrow's date in your local time zone
            tomorrow_local_datetime = (
                current_utc_datetime + timedelta(days=1)
            ).astimezone(local_timezone)
            # Calculate the day after tomorrow's date in your local time zone
            day_after_tomorrow_local_datetime = (
                current_utc_datetime + timedelta(days=2)
            ).astimezone(local_timezone)
            print(
                "Current Local Date and Time:",
                current_local_datetime.strftime("%Y-%m-%d"),
            )
            today_date = current_local_datetime.strftime("%Y-%m-%d")
            print(
                "Tomorrow's Local Date:", tomorrow_local_datetime.strftime("%Y-%m-%d")
            )
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
                            "meta": {"data_ref_id": session["email"]},
                        }
                    ],
                    "parameters": {"vda_vessel_due_to_arrive_dt": str(pull_date)},
                    "on_behalf_of": [{"id": session["participant_id"]}],
                }

                json_string = json.dumps(payload, indent=4)  # Convert payload dictionary to JSON string
                # Rest of the code to send the JSON payload to the API
                data = json.loads(json_string)

                response_vessel_due_to_arrive = requests.post(url_vessel_due_to_arrive,json=data,headers={"SGTRADEX-API-KEY": session["api_key"]},)
                if response_vessel_due_to_arrive.status_code == 200:
                    print("Pull vessel_due_to_arrive success.")
                else:
                    print(
                        f"Failed to PULL vessel_due_to_arrive data. Status code: {response_vessel_due_to_arrive.status_code}"
                    )
            toc = time.perf_counter()
            print(
                f"PULL duration for vessel_due_to_arrive {len(input_list)} in {toc - tic:0.4f} seconds"
            )
            # ========================    END PULL vessel_due_to_arrive         ===========================
            return redirect(url_for("table_view_request", imo=user_vessel_imo))
        else:
          return redirect(url_for("login"))
    else:
      return redirect(url_for("login"))


@app.route("/table_view_request/<imo>", methods=["GET", "POST"])
def table_view_request(imo):
    if g.user:
        imo_list = imo.split(",")
        print(f"IMO list ==== {imo_list}")

        email = session["email"]
        # GET data from MPA
        today_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url_MPA_due_to_arrive = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/duetoarrive/date/{today_datetime}/hours/99"
        url_MPA_due_to_depart = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/duetodepart/date/{today_datetime}/hours/99"
        MPA_arrive_depart_df = get_data_from_vessel_due_to_arrive_and_depart(
            url_MPA_due_to_arrive, url_MPA_due_to_depart, session["gc"]
        )

        # filter merged_df with imo from input form
        # Filter the DataFrame based on imoNumbers
        filtered_df = MPA_arrive_depart_df[
            MPA_arrive_depart_df["vesselParticulars.imoNumber"].isin(imo_list)
        ]
        print(f"filtered_df = {filtered_df}")
        with open("templates/Banner table.html", "r") as file:
            menu_banner_html = file.read()

        if filtered_df.empty:
            print(f"Empty table_df................")
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            for f in os.listdir("templates/"):
                # print(f)
                if "mytable.html" in f:
                    print(f"*mytable.html file to be removed = {f}")
                    os.remove(f"templates/{f}")
            return render_template("table_view.html")
        else:
            for f in os.listdir("templates/"):
                # print(f)
                if "mytable.html" in f:
                    print(f"*mytable.html file to be removed = {f}")
                    os.remove(f"templates/{f}")
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            newHTML = rf"templates/{current_datetime}mytable.html"
            filtered_df.index = filtered_df.index + 1
            filtered_df.to_html(newHTML)
            with open(newHTML, "r") as file:
                html_content = file.read()
            # Add the menu banner HTML code to the beginning of the file
            html_content = menu_banner_html + html_content

            # Try new method
            html_content = html_content.replace(
                f'<table border="1" class="dataframe">',
                f'<table id="example" class="table table-striped table-bordered">',
            )

            html_content = html_content.replace(
                f"<thead>",
                f'<thead class="table-dark">',
            )
            html_content = html_content.replace(
                f"</table>",
                f'</table></div></div></div></div><script src="/static/js/bootstrap.bundle.min.js"></script><script src="/static/js/jquery-3.6.0.min.js"></script><script src="/static/js/datatables.min.js"></script><script src="/static/js/pdfmake.min.js"></script><script src="/static/js/vfs_fonts.js"></script><script src="/static/js/custom.js"></script></body></html>',
            )

            # Write the modified HTML content back to the file
            with open(newHTML, "w") as file:
                file.write(html_content)

            newHTMLrender = f"{current_datetime}mytable.html"
            return render_template(newHTMLrender)
    else:
        return redirect(url_for("login"))


# Make function for logout session
@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("email", None)
    session.pop("participant_id", None)
    session.pop("pitstop_url", None)
    session.pop("api_key", None)
    session.pop("gc", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):
        data = request.form
        print(data)
        r_status = new_registration(data)
        if r_status == 1:
            msg = "You have successfully registered!, please send Admin gsheet credentials file."
            return render_template("login.html", msg=msg)
        else:
            msg = "Your email exists in database! Please reach out to Admin if you need assistance."
            return render_template("login.html", msg=msg)
    elif request.method == "POST":
        msg = "Please fill out the form !"
        return render_template("login.html", msg=msg)
    if request.method == "GET":
        return render_template("register.html")
    return render_template("register.html")


# https://sgtd-api.onrender.com/api/vessel_current_position_db/receive/test@sgtradex.com
# ==========================================       Vessel data PULL         ============================================
@app.route("/api/vessel", methods=["GET", "POST"])
def Vessel_data_pull():
    if g.user:
        if request.method == "POST":
            current_datetime = datetime.now().strftime("%Y-%m-%d")
            session["IMO_NOTFOUND"] = []
            # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
            delete_all_rows_vessel_location(session["gc"])
            user_vessel_imo = request.form["vessel_imo"]
            # Split vessel_imo list into invdivual records
            input_list = [int(x) for x in user_vessel_imo.split(",")]

            print(f"user_vessel_imo from html = {user_vessel_imo}")
            print(f"input_list from html = {input_list}")
            # Loop through input IMO list
            tic = time.perf_counter()
            for vessel_imo in input_list:
                print(f"IMO Number = {vessel_imo}")

                url_vessel_movement = (
                    f"{session['pitstop_url']}/api/v1/data/pull/vessel_movement"
                )
                url_vessel_current_position = (
                    f"{session['pitstop_url']}/api/v1/data/pull/vessel_current_position"
                )
                url_vessel_due_to_arrive = (
                    f"{session['pitstop_url']}/api/v1/data/pull/vessel_due_to_arrive"
                )
                url_MPA = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/positions/imonumber/{vessel_imo}"
                url_MPA_arrivaldeclaration = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/arrivaldeclaration/imonumber/{vessel_imo}"

                ##################### Make the GET request for MPA_vessel_data table LOCATION VCP ALT  #####################
                API_KEY_MPA = os.environ['MPA_API']
                r_GET = requests.get(url_MPA, headers={"Apikey": API_KEY_MPA})

                # Check the response
                if r_GET.status_code == 200:
                    print("Config Data retrieved successfully!")
                    print(r_GET.text)
                    # Store GET data from MPA into MPA_vessel_data table table
                    MPA_GET(r_GET.text, session["gc"])
                else:
                    NOT_FOUND_LIST = session["IMO_NOTFOUND"]
                    NOT_FOUND_LIST.append(vessel_imo)
                    print(f"SGTD PRINTING IMO_NOTFOUND1 = {NOT_FOUND_LIST}")
                    session["IMO_NOTFOUND"] = NOT_FOUND_LIST
                    print(f"SGTD PRINTING IMO_NOTFOUND2 = {session['IMO_NOTFOUND']}")
                    print(f"r_GET.text = {r_GET.text}")
                    print(
                        f"Failed to get Config Data. Status code: {r_GET.status_code}"
                    )
                    print(r_GET.text)

                ##################### Make the GET request for MPA_arrivaldeclaration table ETA  #####################
                r_GET_arrivaldeclaration = requests.get(
                    url_MPA_arrivaldeclaration, headers={"Apikey": API_KEY_MPA}
                )
                if r_GET_arrivaldeclaration.status_code == 200:
                    print("Config Data retrieved successfully!")
                    print(r_GET_arrivaldeclaration.text)

                    # Store GET data from MPA into MPA_arrivaldeclaration table
                    MPA_GET_arrivaldeclaration(
                        r_GET_arrivaldeclaration.text, session["gc"]
                    )
                else:
                    print(
                        f"Failed to get Config Data for arrivaldeclaration. Status code: {r_GET_arrivaldeclaration.status_code}"
                    )
                    print(r_GET_arrivaldeclaration.text)

                # ========================    PULL payload for vessel_current_position and vessel_movement    ===========================
                payload = {
                    "participants": [
                        {
                            "id": "1817878d-c468-411b-8fe1-698eca7170dd",
                            "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
                            "meta": {"data_ref_id": session["email"]},
                        }
                    ],
                    "parameters": {"vessel_imo_no": str(vessel_imo)},
                    "on_behalf_of": [{"id": session["participant_id"]}],
                }

                payload_VDA = {
                    "participants": [
                        {
                            "id": "1817878d-c468-411b-8fe1-698eca7170dd",
                            "name": "MARITIME AND PORT AUTHORITY OF SINGAPORE",
                            "meta": {"data_ref_id": session["email"]},
                        }
                    ],
                    "parameters": {"vda_vessel_due_to_arrive_dt": current_datetime},
                    "on_behalf_of": [{"id": session["participant_id"]}],
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
                    headers={"SGTRADEX-API-KEY": session["api_key"]},
                )
                if PULL_vessel_current_position.status_code == 200:
                    #print(f"Response JSON = {PULL_vessel_current_position.json()}")
                    print("Pull vessel_current_position success.")
                else:
                    print(
                        f"Failed to PULL vessel_current_position data. Status code: {PULL_vessel_current_position.status_code}"
                    )

                # ========================    PULL vessel_due_to_arrive    ===========================
                PULL_vessel_due_to_arrive = requests.post(
                    url_vessel_due_to_arrive,
                    json=data_VDA,
                    headers={"SGTRADEX-API-KEY": session["api_key"]},
                )
                if PULL_vessel_due_to_arrive.status_code == 200:
                    #print(f"Response JSON = {PULL_vessel_due_to_arrive .json()}")
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

            toc = time.perf_counter()
            print(
                f"PULL duration for vessel map query {len(input_list)} in {toc - tic:0.4f} seconds"
            )
            return redirect(url_for("Vessel_map"))

        return render_template("vessel_request.html")
    return redirect(url_for("login"))


##########################################################RECEIVE in MySQL DB#############################################################################################


# https://sgtd-api.onrender.com/api/vessel_due_to_arrive_db/receive/test@sgtradex.com
@app.route("/api/vessel_due_to_arrive_db/receive/<email_url>", methods=["POST"])
def RECEIVE_Vessel_due_to_arrive(email_url):
    email = email_url
    receive_details_data = receive_details(email)
    # print(f"Vessel_current_position_receive:   Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]

    data = request.data  # Get the raw data from the request body

    #print(f"Vessel_due_to_arrive = {data}")

    data_str = data.decode("utf-8")  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_vessel_due_to_arrive = data_dict["payload"]
    #print(f"row_data_vessel_due_to_arrive = {row_data_vessel_due_to_arrive}")

    result = new_vessel_due_to_arrive(
        row_data_vessel_due_to_arrive, email, gsheet_cred_path
    )
    if result == 1:
        # Append the data as a new row
        return f"vessel_due_to_arrive Data saved to Google Sheets.{row_data_vessel_due_to_arrive}"
    else:
        return f"Email doesn't exists, unable to add data"


@app.route("/api/pilotage_service_db/receive/<email_url>", methods=["POST"])
def RECEIVE_Pilotage_service(email_url):
    email = email_url
    receive_details_data = receive_details(email)
    # print(f"Vessel_current_position_receive:   Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]

    data = request.data  # Get the raw data from the request body

    #print(f"Pilotage service = {data}")

    data_str = data.decode("utf-8")  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_pilotage_service = data_dict["payload"][-1]
    #print(f"row_data_Pilotage service = {row_data_pilotage_service}")

    result = new_pilotage_service(data, email, gsheet_cred_path)
    if result == 1:
        # Append the data as a new row
        return (
            f"pilotage_service Data saved to Google Sheets.{row_data_pilotage_service}"
        )
    else:
        return f"Email doesn't exists, unable to add data"


# https://sgtd-api.onrender.com/api/vessel_current_position_db/receive/test@sgtradex.com
@app.route("/api/vessel_current_position_db/receive/<email_url>", methods=["POST"])
def RECEIVE_Vessel_current_position(email_url):
    email = email_url
    receive_details_data = receive_details(email)
    # print(f"Vessel_current_position_receive:   Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]

    data = request.data  # Get the raw data from the request body

    #print(f"Vessel_current_position = {data}")

    data_str = data.decode("utf-8")  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    row_data_vessel_current_position = data_dict["payload"][-1]
    print(f"row_data_vessel_current_position = {row_data_vessel_current_position}")
    result = new_vessel_current_position(
        row_data_vessel_current_position, email, gsheet_cred_path
    )
    if result == 1:
        # Append the data as a new row
        return f"Vessel Current Location Data saved to Google Sheets.{row_data_vessel_current_position}"
    else:
        return f"Email doesn't exists, unable to add data"


# https://sgtd-api.onrender.com/api/vessel_movement_db/receive/test@sgtradex.com
@app.route("/api/vessel_movement_db/receive/<email_url>", methods=["POST"])
def RECEIVE_Vessel_movement(email_url):
    email = email_url
    receive_details_data = receive_details(email)
    # print(f"Vessel_movement_receive:  Receive_details from database.py {receive_details(email)}")
    API_KEY = receive_details_data[1]
    participant_id = receive_details_data[2]
    pitstop_url = receive_details_data[3]
    gsheet_cred_path = receive_details_data[4]

    data = request.data  # Get the raw data from the request body

    data_str = data.decode("utf-8")  # Decode data as a UTF-8 string
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(data_str)
    # Extract the last item from the "payload" array
    last_payload_item = data_dict["payload"][-1]
    print(last_payload_item)
    try:
        print(
            f"Length of vessel movement end date = {len(last_payload_item['vm_vessel_movement_end_dt'])}"
        )
        row_data_vessel_movement = {
            "vm_vessel_particulars.vessel_nm": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_nm"],
            "vm_vessel_particulars.vessel_imo_no": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_imo_no"],
            "vm_vessel_particulars.vessel_flag": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_flag"],
            "vm_vessel_particulars.vessel_call_sign": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_call_sign"],
            "vm_vessel_location_from": last_payload_item["vm_vessel_location_from"],
            "vm_vessel_location_to": last_payload_item["vm_vessel_location_to"],
            "vm_vessel_movement_height": last_payload_item["vm_vessel_movement_height"],
            "vm_vessel_movement_type": last_payload_item["vm_vessel_movement_type"],
            "vm_vessel_movement_start_dt": last_payload_item[
                "vm_vessel_movement_start_dt"
            ],
            "vm_vessel_movement_end_dt": last_payload_item["vm_vessel_movement_end_dt"],
            "vm_vessel_movement_status": last_payload_item["vm_vessel_movement_status"],
            "vm_vessel_movement_draft": last_payload_item["vm_vessel_movement_draft"],
        }
    except:
        print("================no movement end date, printing exception===============")
        row_data_vessel_movement = {
            "vm_vessel_particulars.vessel_nm": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_nm"],
            "vm_vessel_particulars.vessel_imo_no": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_imo_no"],
            "vm_vessel_particulars.vessel_flag": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_flag"],
            "vm_vessel_particulars.vessel_call_sign": last_payload_item[
                "vm_vessel_particulars"
            ][0]["vessel_call_sign"],
            "vm_vessel_location_from": last_payload_item["vm_vessel_location_from"],
            "vm_vessel_location_to": last_payload_item["vm_vessel_location_to"],
            "vm_vessel_movement_height": last_payload_item["vm_vessel_movement_height"],
            "vm_vessel_movement_type": last_payload_item["vm_vessel_movement_type"],
            "vm_vessel_movement_start_dt": last_payload_item[
                "vm_vessel_movement_start_dt"
            ],
            "vm_vessel_movement_end_dt": "",
            "vm_vessel_movement_status": last_payload_item["vm_vessel_movement_status"],
            "vm_vessel_movement_draft": last_payload_item["vm_vessel_movement_draft"],
        }
    # Append the data to the worksheet
    print(f"row_data_vessel_movement: {row_data_vessel_movement}")

    result = new_vessel_movement(row_data_vessel_movement, email, gsheet_cred_path)
    if result == 1:
        # Append the data as a new row
        return f"Vessel Current Location Data saved to Google Sheets.{row_data_vessel_movement}"
    else:
        return f"Email doesn't exists, unable to add data"


##########################################################MySQL DB#############################################################################################


@app.route("/vessel_request/<msg>", methods=["GET", "POST"])
def vessel_request(msg):
    if g.user:
        email = session["email"]
        return render_template("vessel_request.html", msg=msg, email=email)
    else:
        return redirect(url_for("login"))


# 9490820 / 9929297
# ====================================####################MAP DB##############################========================================
@app.route("/api/vessel_map", methods=["GET", "POST"])
def Vessel_map():
    if g.user:
        print(f"VESSEL MAP PRINTING IMO_NOTFOUND = {session['IMO_NOTFOUND']}")
        email = session["email"]
        DB_queried_data = get_map_data(session["gc"])
        # df1 = pd.DataFrame(DB_queried_data[0])
        df2 = pd.DataFrame(DB_queried_data[0])
        # df1 = get_map_data(gsheet_cred_path)[0]
        # print(f"df1 = {df1}")
        # print(f"df2 = {df2}")
        # print(f"df1 VESSEL MAP = {df1.to_string(index=False, header=True)}")
        # df2 = get_map_data(gsheet_cred_path)[1]
        print(f"df2 VESSEL MAP = {df2.to_string(index=False, header=True)}")
        with open("templates/Banner.html", "r") as file:
            menu_banner_html = file.read()

        if df2.empty:
            print(f"Empty df1 or empty df2................")
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            for f in os.listdir("templates/"):
                # print(f)
                if "mymap.html" in f:
                    print(f"*mymap.html file to be removed = {f}")
                    os.remove(f"templates/{f}")

            m = leafmap.Map(center=[1.257167, 103.897], zoom=9)
            regions = "templates/SG_anchorages.geojson"
            m.add_geojson(
                regions,
                layer_name="SG Anchorages",
                style={
                    "color": (random.choice(colors)),
                    "fill": True,
                    "fillOpacity": 0.05,
                },
            )
            newHTML = f"templates/{current_datetime}mymap.html"
            newHTMLwotemp = f"{current_datetime}mymap.html"
            print(f"new html file created = {newHTML}")
            m.to_html(newHTML)
            with open(newHTML, "r") as file:
                html_content = file.read()
            html_content = menu_banner_html + html_content
            with open(newHTML, "w") as file:
                file.write(html_content)
            return render_template(
                newHTMLwotemp,
                user=session["email"],
                IMO_NOTFOUND=session["IMO_NOTFOUND"],
            )

        else:
            # Edit here, remove df1 and merge df, keep df2. Alter drop coulmns based on print
            print(f"df2 WITHOUT VESSEL MOVEMENT = {df2}")
            # merged_df = pd.merge(
            #     df2,
            #     df1,
            #     left_on=df2["imoNumber"],
            #     right_on=df1["vessel_imo_no"],
            #     how="outer",
            # )
            # print(f"Merged df  VESSEL MAP == {merged_df}")
            # merged_df.drop(
            #     columns=[
            #         "key_0",
            #         "id_x",
            #         "id_y",
            #         "vessel_nm",
            #         "vessel_imo_no",
            #         "vessel_flag",
            #         "vessel_call_sign",
            #         "yearBuilt",
            #     ],
            #     inplace=True,
            # )

            # sort & drop duplicates
            # # sorting by first name
            # merged_df.drop_duplicates(subset="imoNumber", keep="last", inplace=True)

            df = df2
            print(f"Vessel_map Merged DF = {df}")
            print(f"Vessel_map Longitiude = {df['longitudeDegrees']}")
            longitude = list(df["longitudeDegrees"])
            print(f"Latitiude = {df['latitudeDegrees']}")
            latitude = list(df["latitudeDegrees"])
            m = folium.Map(location=[1.257167, 103.897], zoom_start=9)
            color_mapping = {}
            # Add several markers to the map
            for index, row in df.iterrows():
                imo_number = row["imoNumber"]
                # Assign a color to the imoNumber, cycling through the available colors
                if imo_number not in color_mapping:
                    color_mapping[imo_number] = colors[len(color_mapping) % len(colors)]
                icon_color = color_mapping[imo_number]
                icon_html = f'<i class="fa fa-arrow-up" style="color: {icon_color}; font-size: 24px; transform: rotate({row["heading"]}deg);"></i>'
                popup_html = f"<b>Vessel Info</b><br>"
                for key, value in row.items():
                    popup_html += f"<b>{key}:</b> {value}<br>"
                folium.Marker(
                    location=[row["latitudeDegrees"], row["longitudeDegrees"]],
                    popup=folium.Popup(html=popup_html, max_width=300),
                    icon=folium.DivIcon(html=icon_html),
                    angle=float(row["heading"]),
                    spin=True,
                ).add_to(m)
            # Geojson url
            geojson_url = "templates/SG_anchorages.geojson"

            # Desired styles
            style = {"fillColor": "red", "color": "blueviolet"}

            # Geojson
            folium.GeoJson(
                data=geojson_url, name="geojson", style_function=lambda x: style
            ).add_to(m)

            for f in os.listdir("templates/"):
                # print(f)
                if "mymap.html" in f:
                    print(f"*mymap.html file to be removed = {f}")
                    os.remove(f"templates/{f}")

            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            newHTML = rf"templates/{current_datetime}mymap.html"
            m.save(newHTML)
            with open(newHTML, "r") as file:
                html_content = file.read()
            # Add the menu banner HTML code to the beginning of the file
            html_content = menu_banner_html + html_content
            # Write the modified HTML content back to the file
            with open(newHTML, "w") as file:
                file.write(html_content)

            newHTMLrender = f"{current_datetime}mymap.html"
            return render_template(
                newHTMLrender,
                user=session["email"],
                IMO_NOTFOUND=session["IMO_NOTFOUND"],
            )
    print("G.user doesn't exists, redirect to login")
    return redirect(url_for("login"))


####################################  START UPLOAD UCC #############################################
@app.route("/UCC_upload")
def UCC_upload():
    if g.user:
        email = session["email"]
        return render_template("UCC_upload.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/api/triangular_upload", methods=["POST"])
def triangular_upload():
    if g.user:
        if request.method == "POST":
            # Get the list of files from webpage
            files = request.files.getlist("files[]")  # Use "files[]" as the key

            # Iterate for each file in the files list and save them
            for file in files:
                if file and file.filename.endswith(".csv"):  # Check if it's a CSV file
                    print(file.filename)

                    file.save(file.filename)
                else:
                    return "<h1>Invalid file format. Please upload only CSV files.</h1>"
            return "<h1>Files Uploaded Successfully.!</h1>"


####################################  END UPLOAD UCC  ###############################################


@app.before_request
def before_request():
    g.user = None
    if "email" in session:
        g.user = session["email"]


# ====================================####################MAP DB##############################========================================


@app.after_request
def after_request(response):
    response.headers[
        "Cache-Control"
    ] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

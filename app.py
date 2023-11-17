from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, g
from flask_mysqldb import MySQL
from sqlalchemy import create_engine, text
import re
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import leafmap.foliumap as leafmap
import folium
import random
import time
import pytz 
import os
import threading
from db_Vessel_map import get_map_data, display_map, get_data_from_VF_vessels, merged_MPA_VF_df
from db_Vessel_data_pull import delete_all_rows_vessel_location, PULL_GET_VCP_VDA_MPA
from db_table_pull import (
    delete_all_rows_table_view,
    PULL_pilotage_service,
    PULL_vessel_due_to_arrive,
    validate_imo
)
from db_table_view_request import (
    get_data_from_MPA_Vessel_Arrival_Declaration,
    get_data_from_vessel_due_to_arrive_and_depart,
    merge_arrivedepart_declaration_df,
    get_data_from_single_vessel_positions,
)
from database import (
    new_registration,
    validate_login,
    receive_details,
    new_vessel_movement,
    new_vessel_current_position,
    new_pilotage_service,
    new_vessel_due_to_arrive,
)
from flask_swagger_ui import get_swaggerui_blueprint

from db_GNSS import GET_LBO_GNSS_Data, GET_LBO_GNSS_Token, display_lbo_map

application = app = Flask(__name__)

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
    
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        msg = ""
        try:
            email = request.form["email"]
            password = request.form["password"]
            login_data = validate_login(email, password)
            print(f"Login data = {login_data}")
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
                session["LBO_ACCESS_TOKEN"] = []
                session["LBO_REFRESH_TOKEN"] = []

                msg = f"Login success for {email}, please enter Vessel IMO number(s)"
                print(f"Login success for {email}, redirect")
                return redirect(url_for("table_view")), 303
                # return render_template('vessel_request.html', msg=msg, email=email)
            else:
                msg = "Invalid credentials, please try again.."
                print("Invalid credentials, please try again..")
                return render_template("login.html", msg=msg), 401
        except Exception as e:
            msg = "Log in failed, please try again."
            print(f"Log in failed, please try again. Error = {e}")
            print("Log in failed, please contact admin")
            return render_template("login.html", msg=msg), 403
        # if request.data['username'] and request.data['password'] in db:
        #   user_data = load_data_from_db()
    if request.method == "GET":
        print("Request == GET")
        return render_template("login.html")


    # ====================================#################### LBO GNSS MAP ##############################========================================
@app.route("/api/gnss_token", methods=["POST"])
def LBO_GET_GNSS_TOKEN():
    tokens = GET_LBO_GNSS_Token()
    print(tokens)
    if tokens == "0":
        print("Too frequent TOKEN request, please try again later...")
        return render_template(
            "GNSS_request.html",
            msg="Too frequent TOKEN request, please try again later...",
        )
    session["LBO_ACCESS_TOKEN"] = tokens["access_token"]
    session["LBO_REFRESH_TOKEN"] = tokens["refresh_token"]
    return f'Successfuly retrieved token: session["LBO_ACCESS_TOKEN"] = {session["LBO_ACCESS_TOKEN"]}, session["LBO_REFRESH_TOKEN"] = {session["LBO_REFRESH_TOKEN"]}'


@app.route("/lbo_request/<msg>", methods=["GET", "POST"])
def lbo_request(msg):
    if g.user:
        return render_template("GNSS_request.html", msg=msg)
    else:
        return redirect(url_for("login")), 304


@app.route("/api/lbo", methods=["POST"])
def LBO_data_pull():
    if g.user:
        if request.method == "POST":
            session["IMO_NOTFOUND"] = []

            user_vessel_imo = request.form["imo"]
            user_lbo_imei = request.form["lbo_imei"]
            print(f"len(user_vessel_imo) = {len(user_vessel_imo)}")
            if len(user_vessel_imo) == 0 and len(user_lbo_imei) == 0:
              return render_template(
                  "GNSS_request.html",
                  msg="Please enter IMO or IMEI number.",
              )
            if len(user_vessel_imo) > 1:
                # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
                delete_all_rows_vessel_location(session["gc"])
                try:
                    input_list = [int(x) for x in user_vessel_imo.split(",")]
                    print(f"user_vessel_imo from html = {user_vessel_imo}")
                    print(f"input_list from html = {input_list}")
                    # Loop through input IMO list
                    tic = time.perf_counter()
                    # ============= GET 2 API's from MPA: VCP + VDA ===================
                    # ============= PULL 2 API's from SGTD: VCP + VDA =================
                    PULL_GET_VCP_VDA_MPA(
                        input_list,
                        session["pitstop_url"],
                        session["gc"],
                        session["participant_id"],
                        session["api_key"],
                        session["IMO_NOTFOUND"],
                    )
                    toc = time.perf_counter()
                    print(
                        f"PULL duration for vessel map query {len(input_list)} in {toc - tic:0.4f} seconds"
                    )
                    print(
                        f"VESSEL MAP PRINTING IMO_NOTFOUND = {session['IMO_NOTFOUND']}"
                    )
                    DB_queried_data = get_map_data(session["gc"])
                    df2 = pd.DataFrame(DB_queried_data[0])
                    print(f"df1 VESSEL MAP = {df2.to_string(index=False, header=True)}")
  
                    # Get Vessel Finder DF and merge
                    VF_df = get_data_from_VF_vessels(user_vessel_imo)
                    ETA_df = get_data_from_vessel_due_to_arrive_and_depart()
                    if df2.empty and VF_df.empty:
                      return (
                          render_template(
                              "GNSS_request.html",
                              msg=f"No data found. Please try again.",
                          ),
                          406,
                      )
                    elif df2.empty:
                      print(f"df2==empty, only display VF_df, no merge....")
                      VF_df["imoNumber"] = VF_df["imoNumber"].astype(int)
                      ETA_df["vesselParticulars.imoNumber"] = ETA_df[
                          "vesselParticulars.imoNumber"
                      ].astype(int)
                      VF_ETA_df = pd.merge(
                          VF_df,
                          ETA_df,
                          left_on=VF_df["imoNumber"],
                          right_on=ETA_df["vesselParticulars.imoNumber"],
                          how="left",
                      )
                      if VF_ETA_df.empty:
                          df2 = VF_df
                      else:
                          df2 = VF_ETA_df
                    elif VF_df.empty:
                      df2 = df2
                      df2.rename(
                          columns={
                              "vesselName": "NAME",
                          },
                          inplace=True,
                      )
                    else:
                      print(f"All DF are not empty, carrying out merged_MPA_VF_df")
                      merged_df = merged_MPA_VF_df(df2, VF_df, ETA_df)
                      print(f"merged_df LBO MAP == {merged_df}")
                      df2 = merged_df
              
                except Exception as e:
                    return (
                        render_template(
                            "GNSS_request.html",
                            msg=f"Invalid Vessel IMO. Please ensure Vessel IMO is valid. Error = {e}",
                        ),
                        406,
                    )

            # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
            # delete_all_rows_vessel_location(session["gc"])

            print(f"len(user_lbo_imei) = {len(user_lbo_imei )}")
            print(f"len(user_vessel_imo) = {len(user_vessel_imo)}")
            if len(user_lbo_imei) > 1:
                print(f'session["LBO_ACCESS_TOKEN"]  = {session["LBO_ACCESS_TOKEN"]}')
                if len(session["LBO_ACCESS_TOKEN"]) == 0:
                    return render_template(
                        "GNSS_request.html",
                        msg="Please retrieve a TOKEN first... Token is currently empty.",
                    )
            if len(user_lbo_imei) > 1 or len(user_vessel_imo) > 1:
                print(f"len(user_lbo_imei) > 1 or len(user_vessel_imo) > 1:")
                # ============= GET LBO GNSS DATA API's from GETT TECHNOLOGIES ===================

                try:
                    GNSS_df = pd.DataFrame()
                    if len(user_lbo_imei) > 1:
                        print(f"len(user_lbo_imei) > 1 == {len(user_lbo_imei)}")
                        tic = time.perf_counter()
                        GNSS_Data = GET_LBO_GNSS_Data(
                            user_lbo_imei,
                            session["LBO_ACCESS_TOKEN"],
                            session["LBO_REFRESH_TOKEN"],
                        )
                        print(f"user_lbo_imei from html = {GNSS_Data}")
                        GNSS_df = pd.DataFrame(GNSS_Data)
                    # Loop through input IMO list
                    if len(user_vessel_imo) < 2:
                        print(f"len(user_vessel_imo) < 2 == {len(user_vessel_imo)}")
                        df2 = pd.DataFrame()
                    print(f"df2 == {df2}")
                    print(f"GNSS_df == {GNSS_df}")
                    if df2.empty and GNSS_df.empty:
                        return (
                            render_template(
                                "GNSS_request.html",
                                msg="No data found. Please try again.",
                            ),
                            406,
                        )

                    display_data = display_lbo_map(GNSS_df, df2)[1]
                    print(f"display_data = {display_data}")
                    # ============= GET 2 API's from MPA: VCP + VDA ===================
                    # ============= PULL 2 API's from SGTD: VCP + VDA =================
                    toc = time.perf_counter()
                    print(
                        f"PULL duration for vessel map query {len(user_lbo_imei)} in {toc - tic:0.4f} seconds"
                    )
                    if display_data[0] == 1:
                        print(f"LBO GNSS _map return start 1")
                        return render_template(
                            display_data[1],
                        )

                    else:
                        print(f"LBO GNSS_map return start 2")
                        print(display_data)
                        return render_template(display_data), 200

                except Exception as e:
                    return (
                        render_template(
                            "GNSS_request.html",
                            msg=f"Invalid IMEI. Please ensure IMEI is valid. Error = {e}",
                        ),
                        406,
                    )
        return render_template("GNSS_request.html"), 403
    return redirect(url_for("login")), 304
# ====================================#################### END LBO GNSS MAP ##############################========================================


@app.route("/table_view", methods=["GET", "POST"])
def table_view():
    if g.user:
        email = session["email"]
        return render_template("table_view.html", email=email)
    else:
        msg = "Error while getting to table view, redirecting to login"
        print("Error while getting to table view, redirecting to login")
        return redirect(url_for("login", msg=msg)), 304


@app.route("/api/table_pull", methods=["GET", "POST"])
def table_pull():
    if g.user:
        print("+++++++++++G.USER VALID, STARTING /api/table_pull++++++++++++++++++")
        if request.method == "POST":
            session["IMO_NOTFOUND"] = []
            session["TABLE_IMO_NOTFOUND"] = []
            # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
            delete_all_rows_table_view(session["gc"])
            user_vessel_imo = request.form["imo"]
            try:
                # Split vessel_imo list into invdivual records
                input_list = [int(x) for x in user_vessel_imo.split(",")]
                print(f"Pilotage service input_list from html = {input_list}")

                # ========================              START PULL pilotage_service by vessel imo                   ===========================
                # url_pilotage_service = (
                #     f"{session['pitstop_url']}/api/v1/data/pull/pilotage_service"
                # )
                # PULL_pilotage_service(
                #     url_pilotage_service,
                #     input_list,
                #     session["participant_id"],
                #     session["api_key"],
                # )
                # ========================          END PULL pilotage_service                         ===========================

                # ========================          START PULL vessel_due_to_arrive by date            ===========================
                url_vessel_due_to_arrive = (
                    f"{session['pitstop_url']}/api/v1/data/pull/vessel_due_to_arrive"
                )
                print("Start PULL_vessel_due_to_arrive thread...")
                print(datetime.now())
                threading.Thread(
                    target=PULL_vessel_due_to_arrive,
                    args=(
                        url_vessel_due_to_arrive,
                        session["participant_id"],
                        session["api_key"],
                    ),
                ).start()
                print("End PULL_vessel_due_to_arrive thread...")
                print(datetime.now())
                # PULL_vessel_due_to_arrive(
                #     url_vessel_due_to_arrive,
                #     session["participant_id"],
                #     session["api_key"],
                # )
                # ========================    END PULL vessel_due_to_arrive         ===========================

                return redirect(url_for("table_view_request", imo=user_vessel_imo)), 303
            except Exception as e:
                return (
                    render_template(
                        "table_view.html",
                        msg=f"Invalid IMO. Please ensure at IMO is valid. Error = {e}",
                    ),
                    400,
                )
        else:
            print("TABLE_PULL Method <> POST")
            return redirect(url_for("login")), 304
    else:
        print("TABLE_PULL g.user is not valid")
        return redirect(url_for("login")), 304


@app.route("/table_view_request/<imo>", methods=["GET", "POST"])
def table_view_request(imo):
    if g.user:
        print("+++++++++++G.USER VALID, STARTING /table_view_request/<imo>++++++++++++++++++")
        try:
            imo_list = imo.split(",")
            print(f"IMO ==== {imo}")
            print(f"IMO list ==== {imo_list}")

            # ======================== START GET MPA Vessel Arrival Declaration by IMO Number =============
            Declaration_df = get_data_from_MPA_Vessel_Arrival_Declaration(imo_list)
            # ======================== END GET MPA Vessel Arrival Declaration by IMO Number =============
          
            # ======================== START GET MPA Vessel Due to Arrive and Depart by next 99 hours  =============
            MPA_arrive_depart_df = get_data_from_vessel_due_to_arrive_and_depart()
            # ======================== END GET MPA Vessel Due to Arrive and Depart by next 99 hours =============
          
            # ======================== START GET Vessel Finder Vessel Data  =============
            VF_Single_Vessel_Positions_df = get_data_from_single_vessel_positions(imo)
            # ======================== END GET Vessel Finder Vessel Data  =============
          
            # Filter the DataFrame based on imoNumbers
            filtered_df_before = MPA_arrive_depart_df[
                MPA_arrive_depart_df["vesselParticulars.imoNumber"].isin(imo_list)
            ]
            print(f"filtered_df_before = {filtered_df_before}")
            if len(filtered_df_before) == 0 and len(VF_Single_Vessel_Positions_df) == 0:
                msg = "IMO cannot be found, please try another IMO.."
                return render_template("table_view.html", msg=msg), 404
            render_html = merge_arrivedepart_declaration_df(
                filtered_df_before, Declaration_df, VF_Single_Vessel_Positions_df
            )
            if render_html == 1:
                return render_template("table_view.html"), 206
            # change purpose from Y,Y,N,N,N... to #1 indicator – Loading / Unloading Cargo #2 indicator – Loading / Unloading Passengers #3 indicator – Taking Bunker  #4 indicator – Taking Ship Supplies #5 indicator – Changing Crew #6 indicator – Shipyard Repair #7 indicator – Offshore Support #8 indicator – Not Used #9 indicator – Other Afloat Activities
            else:
                print(f"merge_arrivedepart_declaration_df = {render_html}")
                return render_template(render_html)
        except Exception as e:
            print(e)
            print(f"Please check /table_view_request/<imo>. Something went wrong with the data, please ensure IMO Number is valid. Error = {e}")
          
            return (
                render_template(
                    "table_view.html",
                    msg="Something went wrong with the data, please ensure IMO Number is valid.",
                ),
                406,
            )
    else:
        return redirect(url_for("login")), 304


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
    session.pop("IMO_FOUND", None)
    session.pop("IMO_NOT_FOUND", None)
    session.pop("LBO_ACCESS_TOKEN", None)
    session.pop("LBO_REFRESH_TOKEN", None)
    return redirect(url_for("login")), 303


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
            msg = "You have successfully registered!, please approach Admin to setup DB credentials."
            return render_template("login.html", msg=msg)
        else:
            msg = "Your email exists in database! Please reach out to Admin if you need assistance."
            return render_template("login.html", msg=msg), 409
    elif request.method == "POST":
        msg = "Please fill out the form !"
        return render_template("login.html", msg=msg), 406
    if request.method == "GET":
        return render_template("register.html")
    # return render_template("register.html")


# https://sgtd-api.onrender.com/api/vessel_current_position_db/receive/test@sgtradex.com
# ==========================================       Vessel data PULL         ============================================
@app.route("/api/vessel", methods=["POST"])
def Vessel_data_pull():
    if g.user:
        if request.method == "POST":
            session["IMO_NOTFOUND"] = []
            # Clear all rows in vessel_movement_UCE and vessel_current_position_UCE table
            delete_all_rows_vessel_location(session["gc"])
            user_vessel_imo = request.form["vessel_imo"]
            # Split vessel_imo list into invdivual records
            try:
                input_list = [int(x) for x in user_vessel_imo.split(",")]
                print(f"user_vessel_imo from html = {user_vessel_imo}")
                print(f"input_list from html = {input_list}")
                # Loop through input IMO list
                tic = time.perf_counter()
                # ============= GET 2 API's from MPA: VCP + VDA ===================
                # ============= PULL 2 API's from SGTD: VCP + VDA =================
                PULL_GET_VCP_VDA_MPA(
                    input_list,
                    session["pitstop_url"],
                    session["gc"],
                    session["participant_id"],
                    session["api_key"],
                    session["IMO_NOTFOUND"],
                )
                toc = time.perf_counter()
                print(
                    f"PULL duration for vessel map query {len(input_list)} in {toc - tic:0.4f} seconds"
                )
                return redirect(url_for("Vessel_map"))
            except Exception as e:
                return (
                    render_template(
                        "vessel_request.html",
                        msg=f"Invalid IMO. Please ensure IMO is valid. Error = {e}",
                    ),
                    406,
                )
        return render_template("vessel_request.html"), 403
    return redirect(url_for("login")), 304


@app.route("/vessel_request/<msg>", methods=["GET", "POST"])
def vessel_request(msg):
    if g.user:
        email = session["email"]
        return render_template("vessel_request.html", msg=msg, email=email)
    else:
        return redirect(url_for("login")), 304


# 9490820 / 9929297
# ====================================####################MAP DB##############################========================================
@app.route("/api/vessel_map", methods=["GET", "POST"])
def Vessel_map():
    if g.user:
        print(f"VESSEL MAP PRINTING IMO_NOTFOUND = {session['IMO_NOTFOUND']}")
        DB_queried_data = get_map_data(session["gc"])
        df1 = pd.DataFrame(DB_queried_data[0])
        print(f"df1 VESSEL MAP = {df1.to_string(index=False, header=True)}")

        display_data = display_map(df1)
        print(f"Vessel_map display_data = {display_data}")
        if display_data[0] == 1:
            return render_template(
                display_data[1],
                user=session["email"],
                IMO_NOTFOUND=session["IMO_NOTFOUND"],
            )

        else:
            return (
                render_template(
                    display_data[1],
                    user=session["email"],
                    IMO_NOTFOUND=session["IMO_NOTFOUND"],
                ),
                404,
            )
    print("G.user doesn't exists, redirect to login")
    return redirect(url_for("login")), 304


####################################  START UPLOAD UCC #############################################
@app.route("/UCC_upload")
def UCC_upload():
    if g.user:
        email = session["email"]
        # base_url = "https://sgtradexdummy-lbs.pitstop.uat.sgtradex.io/"
        # participant_id_lbs = "848a81a3-7d00-4390-b604-a2ca6251ecc8"
  
        # participant_name_lbs = "SGTraDex Dummy - Licensed Bunker Supplier"
        # participant_sourceSystem_id_lbs = "824dd507-712a-44fb-8989-c00143f00cad"
        # participant_sourceSystem_id_lbs = "70a3f53d-f21e-4cae-aa98-9f3eef4abf17"
        # api_url = "https://sgtradexdummy-lbs.pitstop.uat.sgtradex.io/api/v1/config"  # Replace with the actual API endpoint
        # system_data = get_system_data(api_url, api_key)
        # participant_data = get_participants(system_data)

        return render_template("UCC_upload.html", email=email)
    else:
        return redirect(url_for("login")), 304


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
                    return (
                        "<h1>Invalid file format. Please upload only CSV files.</h1>",
                        415,
                    )
            return "<h1>Files Uploaded Successfully.!</h1>"
    else:
        return redirect(url_for("login")), 304


####################################  END UPLOAD UCC  ###############################################





##########################################################     RECEIVE in MySQL DB#############################################################################################


# https://sgtd-api.onrender.com/api/vessel_due_to_arrive_db/receive/test@sgtradex.com
@app.route("/api/vessel_due_to_arrive_db/receive/<email_url>", methods=["POST"])
def RECEIVE_Vessel_due_to_arrive(email_url):
    
    email = email_url
    print(f"Received Vessel_due_to_arrive from {email_url}")
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
    print(f"Received Pilotage_service from {email_url}")
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
    print(f"Received Vessel_current_position from {email_url}")
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
    print(f"Received Vessel_movement from {email_url}")
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
    except Exception as e:
        print(f"================no movement end date, printing exception. Error = {e}===============")
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


@app.route("/api/others/receive/<email_url>", methods=["POST"])
def RECEIVE_Others(email_url):
    email = email_url
    response_data = {"message": f"Received others from {email_url}"}
    return jsonify(response_data)

##########################################################MySQL DB#############################################################################################
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

# Configure Swagger UI
SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "SGTD Vessel Query API Swagger"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/swagger.json")
def swagger():
    with open("swagger.json", "r") as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

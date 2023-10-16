from sqlalchemy import create_engine, text
import pandas as pd
import os
import json
import requests
from datetime import datetime
import pytz

def get_data_from_MPA_Vessel_Arrival_Declaration(input_list):
    Declaration_df = pd.DataFrame()
    print("Start of get_data_from_MPA_Vessel_Arrival_Declaration.............")
    print(f"input_list = {input_list}")
    for vessel_imo in input_list:
        print(f"vessel_imo = {vessel_imo}")
        url_MPA_arrivaldeclaration = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/arrivaldeclaration/imonumber/{vessel_imo}"
        API_KEY_MPA = "QgCv2UvINPRfFqbbH3yVHRVVyO8Iv5CG"
        r_GET_arrivaldeclaration = requests.get(
            url_MPA_arrivaldeclaration, headers={"Apikey": API_KEY_MPA}
        )
        if r_GET_arrivaldeclaration.status_code == 200:
            print("Config Data retrieved successfully!")
            # print(r_GET_arrivaldeclaration.text)
            data_list = json.loads(r_GET_arrivaldeclaration.text)
            # print(f"API response = {(data_list)}")
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
                Declaration_df = Declaration_df.append(
                    pd.json_normalize(latest_record), ignore_index=True
                )
                print(
                    f"Declaration_df get_data_from_MPA_Vessel_Arrival_Declaration == {Declaration_df}"
                )

            else:
                print("No records with reported arrival times found.")
    # Apply the mapping to the "purpose" column in Declaration_df

    Declaration_df["purpose"] = Declaration_df["purpose"].apply(map_purpose)
    return Declaration_df
    # ======================== END GET MPA Vessel Arrival Declaration by IMO Number =============


def map_purpose(row):
    indicators = [
        "#1 Loading / Unloading Cargo",
        "#2 Loading / Unloading Passengers",
        "#3 Taking Bunker",
        "#4 Taking Ship Supplies",
        "#5 Changing Crew",
        "#6 Shipyard Repair",
        "#7 Offshore Support",
        "#8 Not Used",
        "#9 Other Afloat Activities",
    ]
    selected_indicators = []
    for i, value in enumerate(row.split(",")):
        if value == "Y":
            selected_indicators.append(indicators[i])
    if not selected_indicators:
        return "No Purpose Specified"
    # If none of the values are 'Y', return a default value (you can change this as needed)
    return ", ".join(selected_indicators)


# get VDA from MPA API
def get_data_from_vessel_due_to_arrive_and_depart():
    print("Start of get_data_from_vessel_due_to_arrive_and_depart........")

    # Define your local time zone (UTC+9)
    local_timezone = pytz.timezone("Asia/Singapore")
    # Get the current date and time in UTC
    current_utc_datetime = datetime.now(pytz.utc)
    # Convert the current UTC time to your local time zone
    current_local_datetime = current_utc_datetime.astimezone(local_timezone)
  
    today_datetime = current_local_datetime.strftime("%Y-%m-%d %H:%M:%S")
    url_MPA_due_to_arrive = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/duetoarrive/date/{today_datetime}/hours/99"
    url_MPA_due_to_depart = f"https://sg-mdh-api.mpa.gov.sg/v1/vessel/duetodepart/date/{today_datetime}/hours/99"
    API_KEY_MPA = "QgCv2UvINPRfFqbbH3yVHRVVyO8Iv5CG"
    r_GET_arrive = requests.get(url_MPA_due_to_arrive, headers={"Apikey": API_KEY_MPA})
    # Check the response
    if r_GET_arrive.status_code == 200:
        print("vessel_due_to_arrive Data retrieved successfully!")
        # query and values
        dueToArrive_Data = json.loads(r_GET_arrive.text)
        # print(f"dueToArrive_Data = {dueToArrive_Data}")
        arrive_df = pd.json_normalize(dueToArrive_Data)
        print(f"arrive_df = {arrive_df}")
        print(arrive_df.iloc[400:410])
        # write in mysql
    else:
        print("Failed to get vessel_due_to_arrive data")

    r_GET_depart = requests.get(url_MPA_due_to_depart, headers={"Apikey": API_KEY_MPA})
    # Check the response
    if r_GET_depart.status_code == 200:
        print("vessel_due_to_depart Data retrieved successfully!")
        # query and values
        dueToDepart_Data = json.loads(r_GET_depart.text)
        depart_df = pd.json_normalize(dueToDepart_Data)
    else:
        print("Failed to get vessel_due_to_depart data")

    merged_df = arrive_df.merge(depart_df, on="vesselParticulars.imoNumber", how="left")
    merged_df.drop(
        columns=[
            "vesselParticulars.vesselName_y",
            "vesselParticulars.vesselName_y",
            "vesselParticulars.flag_y",
            "vesselParticulars.callSign_y",
        ],
        inplace=True,
    )
    print(f"get_data_from_vessel_due_to_arrive_and_depart.merge_df = {merged_df}")
    return merged_df


def merge_arrivedepart_declaration_df(filtered_df_before, Declaration_df):
    # Merge Declaration_df with filtered_df
    filtered_df = filtered_df_before.merge(
        Declaration_df,
        how="left",
        on="vesselParticulars.imoNumber",
    )
    filtered_df.drop(
        columns=[
            "vesselParticulars.vesselName",
            "vesselParticulars.callSign",
            "vesselParticulars.flag",
             # to be removed once purpose is fixed
            "location",
            "grid",
            "agent",
            "reportedArrivalTime",
            "locationFrom",
            "purpose",
        ],
        inplace=True,
    )

    filtered_df.rename(
        columns={
            "vesselParticulars.vesselName_x": "vesselName",
            "vesselParticulars.callSign_x": "callSign",
            "vesselParticulars.flag_x": "flag",
            "vesselParticulars.imoNumber": "IMO number",
            "dueToDepart": "dueToDepartTime",
            # To be reviewed in future
            "locationTo": "locationFrom",
        },
        inplace=True,
    )

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
        return 1  # render_template("table_view.html")
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
            f'</table></div></div></div></div><script src="/static/js/bootstrap.bundle.min.js"></script><script src="/static/js/jquery-3.6.0.min.js"></script><script src="/static/js/datatables.min.js"></script><script src="/static/js/pdfmake.min.js"></script><script src="/static/js/vfs_fonts.js"></script><script src="/static/js/custom.js"></script><script src="https://code.jquery.com/jquery-3.6.0.min.js"></script><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script></body></html>',
          )

        # Write the modified HTML content back to the file
        with open(newHTML, "w") as file:
            file.write(html_content)
        print("it has reached here ===================")
        newHTMLrender = f"{current_datetime}mytable.html"
        return newHTMLrender

from sqlalchemy import create_engine, text
import pandas as pd
import os
import json
from datetime import datetime
import folium
import leafmap.foliumap as leafmap
import random
import requests

colors = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "beige",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "darkpurple",
    "white",
    "pink",
    "lightblue",
    "lightgreen",
    "gray",
    "black",
    "lightgray",
]


def get_data_from_VF_vessels(imo_list):
  single_vessel_positions_df = pd.DataFrame()
  print("Start of get_data_from_single_vessel_positions.............")
  print(f"input_list = {imo_list}")

  api_key = "WS-00555FCD-8CD037"

  base_url = f"https://api.vesselfinder.com/vessels?userkey={api_key}"

  VF_ais_response = requests.get(f"{base_url}&imo={imo_list}")
  print(f"VF_ais_response.json() = {VF_ais_response.json()}")
  VF_ais_data = VF_ais_response.json()

  VF_ais_info = [entry["AIS"] for entry in VF_ais_data]
  single_vessel_positions_df = pd.DataFrame(VF_ais_info)
  print(f"single_vessel_positions_df = {single_vessel_positions_df}")
  single_vessel_positions_df.rename(
      columns={
          "MMSI": "mmsiNumber",
          "TIMESTAMP": "timeStamp",
          "LATITUDE": "latitudeDegrees",
          "LONGITUDE": "longitudeDegrees",
          "COURSE": "course",
          "SPEED": "speed",
          "HEADING": "heading",
          "IMO": "imoNumber",
          "CALLSIGN": "callSign",
          "ETA": "ETA - VesselFinder"
      },
      inplace=True,
  )
  single_vessel_positions_df.drop(
      columns=[
          "A",
          "B",
          "C",
          "D",
          "ECA",
          "LOCODE",
          "SRC",
          "DRAUGHT",
          "NAVSTAT",
      ],
      inplace=True,
  )
  # Reorder columns in place
  desired_column_order = [
    "NAME",
    "callSign",
    "imoNumber",
    "mmsiNumber",
    "latitudeDegrees",
    "longitudeDegrees",
    "ETA - VesselFinder",
    "DESTINATION",
    "DISTANCE_REMAINING",
    "course",
    "speed",
    "heading",
    "timeStamp",
  ]
  single_vessel_positions_df = single_vessel_positions_df[desired_column_order]
  # print(VF_ais_info)
  print(single_vessel_positions_df)
  return single_vessel_positions_df


# Merge database data for MAP
def get_map_data(db_creds):
    print("Start of get_map_data......")
    engine = create_engine(
        db_creds, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
    )
    with engine.connect() as conn:
        # Select vessel_movement_UCE
        # query = text("select * from vessel_movement_UCE")
        # result_VM = conn.execute(query)
        # result_all_VM = result_VM.fetchall()
        # column_names_VM = result_VM.keys()
        # print(result_all_VM)
        # print(f"length of result_all_VM = {len(result_all_VM)}")
        # df1 = pd.DataFrame(result_all_VM, columns=column_names_VM)

        # Select MPA_vessel_data
        query = text("select * from MPA_vessel_data")
        result_VCP = conn.execute(query)
        result_all_VCP = result_VCP.fetchall()
        column_names_VCP = result_VCP.keys()
        print(result_all_VCP)
        print(f"length of result_all_VCP = {len(result_all_VCP)}")
        df2 = pd.DataFrame(result_all_VCP, columns=column_names_VCP)
        # sorting by first name
        df2.drop_duplicates(subset="imoNumber", keep="last", inplace=True)

        # Select MPA_arrivaldeclaration
        query = text("select * from MPA_arrivaldeclaration")
        result_ETA = conn.execute(query)
        result_all_ETA = result_ETA.fetchall()
        column_names_ETA = result_ETA.keys()
        print(result_all_ETA)
        print(f"length of result_all_ETA = {len(result_all_ETA)}")
        df3 = pd.DataFrame(result_all_ETA, columns=column_names_ETA)
        df3.drop(columns=["call_sign", "flag", "vessel_name"], inplace=True)
        df3.drop_duplicates(subset="imo_number", keep="last", inplace=True)
        new_df = pd.merge(
            df2, df3, left_on=df2["imoNumber"], right_on=df3["imo_number"], how="inner"
        )
        if "key_0" in new_df.columns:
            new_df.drop(columns=["key_0"], inplace=True)
        new_df.drop(columns=["id_x", "id_y", "imo_number"], inplace=True)
        # print(f"Final Result all vm = {[df1, new_df]}")
        # return [df1, new_df]
        print(f"Final Result all vm = {[new_df]}")
        return [new_df]


def display_map(df1):
    with open("templates/Banner.html", "r") as file:
        menu_banner_html = file.read()

    with open("templates/Banner Vessel Map.html", "r") as file:
        menu_banner_body_html = file.read()
    if df1.empty:
        print(f"disaply map: Empty  VCP df1................")
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        for f in os.listdir("templates/"):
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
        html_content = html_content.replace(
            "<style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>",
            menu_banner_html,
        )
        html_content = html_content.replace("<body>", menu_banner_body_html)
        with open(newHTML, "w") as file:
            file.write(html_content)
        return [1, newHTMLwotemp]  # render_template(
        #     newHTMLwotemp,
        #     user=session["email"],
        #     IMO_NOTFOUND=session["IMO_NOTFOUND"],
        # )

    else:
        # Edit here, remove df1 and merge df, keep df2. Alter drop coulmns based on print
        print(f"df2 WITHOUT VESSEL MOVEMENT = {df1}")
        df = df1
        print(f"Vessel_map Merged DF = {df}")
        print(f"Vessel_map Longitiude = {df['longitudeDegrees']}")
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
            popup_html = f"<b>{row['NAME']} - {row['callSign']}</b><br>"
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
        geojson_layer = folium.GeoJson(
            data=geojson_url,
            name="geojson",
            style_function=lambda x: style,
            highlight_function=lambda x: {"fillOpacity": 0.3},
            popup=folium.GeoJsonPopup(fields=["NAME"], aliases=["Name"]),
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
        html_content = html_content.replace(
            "<style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>",
            menu_banner_html,
        )
        html_content = html_content.replace("<body>", menu_banner_body_html)

        # Write the modified HTML content back to the file
        with open(newHTML, "w") as file:
            file.write(html_content)

        newHTMLrender = f"{current_datetime}mymap.html"
        return [2, newHTMLrender]  # render_template(
        #     newHTMLrender,
        #     user=session["email"],
        #     IMO_NOTFOUND=session["IMO_NOTFOUND"],
        # )

import requests
import time
from datetime import datetime
import pytz
import json
from sqlalchemy import create_engine, text
import pandas as pd
import os
import folium
import leafmap.foliumap as leafmap
import random


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


def GET_LBO_GNSS_Token():
    access_token = ""
    refresh_token = ""
    token_dict = {}
    current_utc_datetime = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(current_utc_datetime)

    GNSS_URL = "https://hk-open.tracksolidpro.com/route/rest"

    access_token_params = {
        "method": "jimi.oauth.token.get",
        "timestamp": current_utc_datetime,
        "app_key": "8FB345B8693CCD00497CDAC6016483DF",
        "sign_method": "md5",
        "v": "0.9",
        "format": "json",
        "user_id": "GETT Technologies Pte Ltd",
        "user_pwd_md5": "e53463411b225eb75d394209ef1f523b",
        "expires_in": "7200",
    }

    tic = time.perf_counter()
    token_GET = requests.get(GNSS_URL, params=access_token_params)

    if token_GET.status_code == 200:
        print("GET GNSS Access Token success.")
        print(token_GET.text)
        token_GET_list = json.loads(token_GET.text)
        if token_GET_list["code"] == 1006:
            print(
                'Too frequent token request, "code":1006,"message":"Illegal access, request frequency is too high","result":null,"data":null}'
            )
            return "0"

        access_token = token_GET_list["result"]["accessToken"]
        refresh_token = token_GET_list["result"]["accessToken"]
        token_dict["access_token"] = access_token
        token_dict["refresh_token"] = refresh_token
        print(token_dict)
    else:
        print(f"Failed to get GNSS Access Token. Status code: {token_GET.status_code}")

    toc = time.perf_counter()
    print(f"PULL duration for GNSS Access Token in {toc - tic:0.4f} seconds")
    print(f"token_dict = {token_dict}")
    return token_dict


def GET_LBO_GNSS_Data(imeis, access_token, refresh_token):
    access_token = access_token
    refresh_token = refresh_token
    GNSS_URL = "https://hk-open.tracksolidpro.com/route/rest"
    current_utc_datetime = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"imeis = {imeis}")
    pull_params = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 7200,
        "imeis": imeis,
        "method": "jimi.device.location.get",
        "timestamp": current_utc_datetime,
        "app_key": "8FB345B8693CCD00497CDAC6016483DF",
        "sign_method": "md5",
        "v": "0.9",
        "format": "json",
        "map_type": "GOOGLE",
    }
    tic = time.perf_counter()
    GNSS_GET = requests.get(GNSS_URL, params=pull_params)
    if GNSS_GET.status_code == 200:
        # print(f"GNSS_GET.text = {GNSS_GET.text}")
        GNSS_GET_list = json.loads(GNSS_GET.text)
    else:
        print(f"Failed to get GNSS Data. Status code: {GNSS_GET.status_code}")
    toc = time.perf_counter()
    print(f"PULL duration for GNSS Data {len(imeis)} in {toc - tic:0.4f} seconds")

    lbo_result = []

    for item in GNSS_GET_list["result"]:
        # print(f'GNSS_GET_list["result"] = {item}')
        imei = item["imei"]
        lat = item["lat"]
        long = item["lng"]
        direction = item["direction"]
        gps_time = item["gpsTime"]
        lbo_dict = {}
        lbo_dict["imei"] = imei
        lbo_dict["lat"] = lat
        lbo_dict["long"] = long
        lbo_dict["direction"] = direction
        lbo_dict["gpsTime"] = gps_time
        lbo_result.append(lbo_dict)
        # print(f"lbo_result = {lbo_result}")
        # print(f"lbo_dict = {lbo_dict}")

    # Print the dictionary
    # print("lbo_result", lbo_result)
    return lbo_result  # Return the list of dictionaries


# GET_LBO_GNSS_Token()
# GET_LBO_GNSS_Data(
#     "864695060027820,864695060032267,864695060024066",
#     "cddd32b08795ab8da8871d324ebcf47a",
#     "cddd32b08795ab8da8871d324ebcf47a",
# )


def display_lbo_map(df1, df2):
  with open("templates/Banner.html", "r") as file:
      menu_banner_html = file.read()

  with open("templates/Banner Vessel Map.html", "r") as file:
      menu_banner_body_html = file.read()
  if df1.empty and df2.empty:
      print(f"disaply map: Empty df1 and df2................")
      current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
      for f in os.listdir("templates/"):
          if "lbomap.html" in f:
              print(f"*lbomap.html file to be removed = {f}")
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
      newHTML = f"templates/{current_datetime}lbomap.html"
      newHTMLwotemp = f"{current_datetime}lbomap.html"
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
      # print(f"df1 LBO_map = {df1}")
      # print(f"df2 Vessel_map = {df2}")
      df = df1
      m = folium.Map(location=[1.257167, 103.897], zoom_start=9)
      color_mapping = {}
      ship_image = "static/images/ship.png"
      # Add several LBO markers to the map
      if not df1.empty:
          for index, row in df.iterrows():
              imo_number = row["imei"]
              # Assign a color to the imoNumber, cycling through the available colors
              if imo_number not in color_mapping:
                  color_mapping[imo_number] = colors[len(color_mapping) % len(colors)]
              icon_color = color_mapping[imo_number]
              icon_html = folium.DivIcon(
                  html=f'<i class="fa fa-arrow-up" style="color: {icon_color}; font-size: 17px; transform: rotate({row["direction"]}deg);"></i>'
              )
              popup_html = f"<b>Vessel Info</b><br>"
              for key, value in row.items():
                  popup_html += f"<b>{key}:</b> {value}<br>"
              folium.Marker(
                  location=[row["lat"], row["long"]],
                  popup=folium.Popup(html=popup_html, max_width=300),
                  icon=icon_html,  # folium.DivIcon(html=icon_html),
                  angle=float(row["direction"]),
                  spin=True,
              ).add_to(m)

      # Add several VESSEL markers to the map
      if not df2.empty:
          for index, row in df2.iterrows():
              imo_number = row["imoNumber"]
              # Assign a color to the imoNumber, cycling through the available colors
              if imo_number not in color_mapping:
                  color_mapping[imo_number] = colors[len(color_mapping) % len(colors)]
              icon_color = color_mapping[imo_number]
              # if int(row["yearBuilt"]) > 2010:
              icon_html = folium.DivIcon(
                  html=f'<i class="fa fa-arrow-circle-up" style="color: {icon_color}; font-size: {int(row["vesselLength"])/10}px; transform: rotate({row["heading"]}deg);"></i>'
              )
              # else:
              #     # icon_html = f'<i class="fa fa-ship" style="color: {icon_color}; font-size: {int(row["vesselLength"])/10}px; transform: rotate({row["heading"]}deg);"></i>'
              #     icon_html = folium.CustomIcon(
              #         icon_image=ship_image,
              #         icon_size=(50, 50),  # You can adjust the size
              #         icon_anchor=(25, 25),
              #     )
              popup_html = f"<b>Vessel Info</b><br>"
              for key, value in row.items():
                  popup_html += f"<b>{key}:</b> {value}<br>"
              folium.Marker(
                  location=[row["latitudeDegrees"], row["longitudeDegrees"]],
                  popup=folium.Popup(html=popup_html, max_width=300),
                  icon=icon_html,  # folium.DivIcon(html=icon_html),
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

      # Add legend
      item_txt = """<br> &nbsp; {item1} &nbsp; <i class="fa fa-arrow-circle-up" style="color:{col1}"></i><br> &nbsp; {item2} &nbsp; <i class="fa fa-arrow-up" style="color:{col2}"></i>"""
      html_itms = item_txt.format(
          item1="Vessel", col1="black", item2="Lighter Boat", col2="black"
      )

      legend_html = """
          <div style="
          position: fixed; 
          bottom: 50px; left: 50px; width: 200px; height: 70px; 
          border:2px solid grey; z-index:9999; 

          background-color:white;
          opacity: .85;

          font-size:14px;
          font-weight: bold;

          ">
          &nbsp; {title} 

          {itm_txt}

          </div> """.format(
          title="Legend html", itm_txt=html_itms
      )
      m.get_root().html.add_child(folium.Element(legend_html))

      for f in os.listdir("templates/"):
          # print(f)
          if "lbomap.html" in f:
              print(f"*lbomap.html file to be removed = {f}")
              os.remove(f"templates/{f}")

      current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
      newHTML = rf"templates/{current_datetime}lbomap.html"
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

      newHTMLrender = f"{current_datetime}lbomap.html"
      return [2, newHTMLrender]  # render_template(
      #     newHTMLrender,
      #     user=session["email"],
      #     IMO_NOTFOUND=session["IMO_NOTFOUND"],
      # )


# data = """{
#   "code": 0,
#   "message": "success",
#   "result": [
#     {
#       "imei": "864695060024066",
#       "deviceName": "PRESIDENT 18",
#       "icon": "ship",
#       "status": "1",
#       "posType": "GPS",
#       "lat": 1.306381,
#       "lng": 103.693502,
#       "hbTime": "2023-10-19 02:31:55",
#       "accStatus": "0",
#       "gpsSignal": "4",
#       "powerValue": null,
#       "batteryPowerVal": "4.14",
#       "speed": "1",
#       "gpsNum": "11",
#       "gpsTime": "2023-10-19 02:32:23",
#       "direction": "79",
#       "activationFlag": "1",
#       "expireFlag": "1",
#       "electQuantity": "100",
#       "locDesc": null,
#       "distance": "-1",
#       "temperature": null,
#       "trackerOil": null,
#       "currentMileage": "8853.604987375656"
#     },
#     {
#       "imei": "864695060027820",
#       "deviceName": "Nautical Island",
#       "icon": "ship",
#       "status": "1",
#       "posType": "GPS",
#       "lat": 1.303131,
#       "lng": 104.068293,
#       "hbTime": "2023-10-19 02:31:08",
#       "accStatus": "0",
#       "gpsSignal": "4",
#       "powerValue": null,
#       "batteryPowerVal": "4.19",
#       "speed": "2",
#       "gpsNum": "6",
#       "gpsTime": "2023-10-19 02:32:19",
#       "direction": "311",
#       "activationFlag": "1",
#       "expireFlag": "1",
#       "electQuantity": "100",
#       "locDesc": null,
#       "distance": "-1",
#       "temperature": null,
#       "trackerOil": null,
#       "currentMileage": "10344.638189896574"
#     },
#     {
#       "imei": "864695060032267",
#       "deviceName": "DM Beta 1",
#       "icon": "ship",
#       "status": "1",
#       "posType": "GPS",
#       "lat": 1.29789,
#       "lng": 103.742542,
#       "hbTime": "2023-10-19 02:29:50",
#       "accStatus": "0",
#       "gpsSignal": "4",
#       "powerValue": null,
#       "batteryPowerVal": "4.19",
#       "speed": "0",
#       "gpsNum": "7",
#       "gpsTime": "2023-10-19 02:32:08",
#       "direction": "208",
#       "activationFlag": "1",
#       "expireFlag": "1",
#       "electQuantity": "100",
#       "locDesc": null,
#       "distance": "-1",
#       "temperature": null,
#       "trackerOil": null,
#       "currentMileage": "6194.976518074939"
#     }
#   ],
#   "data": null
# }"""
#     parsed_data = json.loads(data)

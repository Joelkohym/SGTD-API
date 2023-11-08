import json
import requests
from datetime import datetime
import csv


# Function to retrieve system name and id from the API
def get_system_data(api_url, api_key):
    headers = {"SGTRADEX-API-KEY": api_key}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # file_path = "output.txt"
        # with open(file_path, "w") as file:
        #     file.write(str(data))
        # print(data)
        return data
    else:
        return None


def open_file_dialog(data):
    files = filedialog.askopenfilenames(
        title="Select Files", filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    # create folder and data package
    package_id = create_folder_and_package(data)  # return package_id

    for file in files:
        process_file(file, data, package_id)


def create_folder_and_package(data):
    # print(f'item["id"] = {data["id"]}')
    ## Make the POST request and use the response to create folder and package
    current_datetime = datetime.utcnow()
    formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
    # print(f'[{{{data["id"]}}}, {{{participant_id_lbs}}}]')

    participant_data_1 = {"id": data["id"], "system": {"id": data["system_id"]}}
    participant_data_2 = {
        "id": participant_id_lbs,
        "system": {"id": participant_sourceSystem_id_lbs},
    }
    print(
        f"participant_data_1 & participant_data_2 = {participant_data_1} & {participant_data_2}"
    )
    create_folder_payload = {
        "name": f"test_create_folder {formatted_datetime}",
        "participants": [participant_data_1, participant_data_2],
        "owners": [participant_id_lbs],
    }

    folder_json_string = json.dumps(create_folder_payload, indent=4)
    folder_data = json.loads(folder_json_string)

    create_folder_response = requests.post(
        f"{base_url}api/v1/folder",
        json=folder_data,
        headers={"SGTRADEX-API-KEY": api_key},
    )
    print(f"create_folder_response.status_code = {create_folder_response.status_code}")
    if create_folder_response.status_code == 200:
        # print(f"create_folder_response = {create_folder_response}")
        create_folder_response_json = create_folder_response.json()
        folder_id = create_folder_response_json["folder"]["id"]
        print("Folder ID:", folder_id)

        create_package_payload = {
            "referenceNumber": f"test_create_package",
            "folderId": folder_id,
            "name": "Process Name",
            "participants": [participant_data_1, participant_data_2],
            "owners": [participant_id_lbs],
        }

        package_json_string = json.dumps(create_package_payload, indent=4)
        package_data = json.loads(package_json_string)

        create_package_response = requests.post(
            f"{base_url}api/v1/data-package",
            json=package_data,
            headers={"SGTRADEX-API-KEY": api_key},
        )

        if create_package_response.status_code == 200:
            # print(create_package_response)
            create_package_response_json = create_package_response.json()
            package_id = create_package_response_json["dataPackage"]["id"]
            print("Data Package ID:", package_id)
            return package_id


def process_file(file, data, package_id):
    # Here, you can define what you want to do with each selected file.
    bunker_delivery_note1 = "bdn_bunker_tanker_seal_no"
    bunker_delivery_note2 = "bdn_surveyor_seal_no"
    bunkering_sales_confirmation1 = "bsc_vessel_nm"
    bunkering_sales_confirmation2 = "bsc_confirmation_no"
    sales_invoice_lbs_bunkerbuyer1 = "invoice_lbsbb_invoice_dt"
    sales_invoice_lbs_bunkerbuyer2 = "invoice_lbsbb_sales_contract_no"

    # Specify the CSV file path
    csv_file_path = file
    # create folder and data package
    # package_id = create_folder_and_package(data)  # return package_id

    # Open and read the CSV file
    with open(csv_file_path, newline="") as csv_file:
        csv_reader = csv.reader(csv_file)

        # Read the first row (header) from the CSV file
        header_row = next(csv_reader)

        # Check if the header matches the expected values
        if (
            header_row[0] == bunker_delivery_note1
            and header_row[1] == bunker_delivery_note2
        ):
            print(f"The file '{csv_file_path}' is a bunker_delivery_note DE.")
            dataElement = "bunker_delivery_note"
            fieldsToBeConverted = [
                "bdn_bunker_metering_ticket_no",
                "bdn_gross_tonnage",
                "bdn_supplied_product_viscosity",
                "bdn_supplied_product_coq_density",
                "bdn_supplied_product_water_content",
                "bdn_supplied_product_flash_point",
                "bdn_supplied_product_sulphur_content",
                "bdn_supplied_product_metric_tons_delivered",
                "bdn_customer_feedback",
                "bdn_specified_limit_value",
            ]
            cleanup_PUSH_JSON(
                csv_file_path, data, dataElement, package_id, fieldsToBeConverted
            )

        elif (
            header_row[0] == bunkering_sales_confirmation1
            and header_row[1] == bunkering_sales_confirmation2
        ):
            print(f"The file '{csv_file_path}' is a bunkering_sales_confirmation DE.")
            dataElement = "bunkering_sales_confirmation"
            fieldsToBeConverted = [
                "bsc_imo_no",
                "bsc_grade_quantities.bsc_goods_qty",
                "bsc_grade_quantities.bsc_goods_unit_price",
                "bsc_barging_fee",
                "bsc_commission",
            ]
            cleanup_PUSH_JSON(
                csv_file_path, data, dataElement, package_id, fieldsToBeConverted
            )

        elif (
            header_row[0] == sales_invoice_lbs_bunkerbuyer1
            and header_row[1] == sales_invoice_lbs_bunkerbuyer2
        ):
            print(f"The file '{csv_file_path}' is a sales_invoice_lbs_bunkerbuyer DE.")
            dataElement = "sales_invoice_lbs_bunkerbuyer"
            fieldsToBeConverted = [
                "invoice_lbsbb_goods_particulars.invoice_goods_qty",
                "invoice_lbsbb_goods_particulars.invoice_goods_unit_price",
            ]
            cleanup_PUSH_JSON(
                csv_file_path, data, dataElement, package_id, fieldsToBeConverted
            )

        else:
            print(f"The file '{csv_file_path}' does not match the expected format.")
    print(f"Processing file: {file}")


def cleanup_PUSH_JSON(
    csv_file_path, data, dataElement, package_id, fieldsToBeConverted
):
    # Initialize a variable to count the total rows
    total_rows = 0
    # Create a list to store the data dictionaries
    payload_entries = []
    # Open the CSV file for reading
    with open(csv_file_path, newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        header_row = next(csv_reader)

        # Loop through the remaining rows in the CSV
        for row in csv_reader:
            row_data = {}
            for header, value in zip(header_row, row):
                # Check if the header is in fieldsToBeConverted
                if header in fieldsToBeConverted:
                    # Try to convert the value to an integer, if not possible, keep it as a string
                    if "." in value:
                        try:
                            row_data[header] = float(value)
                        except ValueError:
                            row_data[header] = value
                    else:
                        try:
                            row_data[header] = int(value)
                        except ValueError:
                            row_data[header] = value

                else:
                    row_data[header] = value
            payload_entries.append(row_data)
            total_rows += 1

    print(f"Total rows = {total_rows}")

    payload_entries = convert_keys_to_nested_structure(payload_entries)[0]

    # ================= Start Delete attachment field =================
    # del payload_entries[0]["attachments"]
    # ================= End Delete attachment field =================

    json_result = {
        "participants": [{"id": data["id"]}],
        "parent_node_id": package_id,
        "parent_node_type": "PACKAGE",
        "payload": payload_entries,
    }
    # Drop empty fields
    json_result = remove_empty(json_result)

    print(type(json_result))
    print(f"JSON Result == {json_result}")
    # Make the POST request

    response = requests.post(
        f"{base_url}api/v1/data/push/{dataElement}",
        json=json_result,
        headers={"SGTRADEX-API-KEY": api_key},
    )
    print(f"response.status_code == {response.status_code}")
    # Check the response
    if response.status_code == 200:
        print(f"{dataElement} Data posted successfully!")
        print(response.json())
        pass
    else:
        print(f"{dataElement} FAILED!!! == {response.json()}")


def convert_values(value):
    if value == "TRUE":
        return True
    elif value == "FALSE":
        return False
    return value


def convert_keys_to_nested_structure(data):
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            keys = key.split(".")
            current_dict = result
            for k in keys[:-1]:
                if k not in current_dict:
                    current_dict[k] = {}
                current_dict = current_dict[k]
            current_key = keys[-1]
            if current_key not in current_dict:
                current_dict[current_key] = convert_values(value)
            else:
                if not isinstance(current_dict[current_key], list):
                    current_dict[current_key] = [current_dict[current_key]]
                current_dict[current_key].append(value)
        return [
            {k: convert_keys_to_nested_structure(v) for k, v in result.items()}
        ]  # Wrap the final result in a list
    elif isinstance(data, list):
        return [convert_keys_to_nested_structure(item) for item in data]
    else:
        return data


def remove_empty(obj):
    if isinstance(obj, dict):
        return {
            k: remove_empty(v)
            for k, v in obj.items()
            if v is not None and v != "" and v != {} and v != []
        }
    elif isinstance(obj, list):
        return [
            remove_empty(v)
            for v in obj
            if v is not None and v != "" and v != {} and v != []
        ]
    else:
        return obj


# Function to display data related to the selected participant_id
def display_selected_data():
    selected_index = listbox.curselection()[0]
    selected_participant_id = listbox.get(selected_index)
    output_listbox.delete(0, tk.END)  # Clear the Listbox
    if selected_participant_id in participant_data:
        selected_data = participant_data[selected_participant_id]
        # print(f"selected_data = {selected_data}")
        for data in selected_data:
            # print(f"data = {data}")
            item_id = data["id"]
            item_name = data["name"]
            item_de = data["data_element"]
            output_listbox.insert(
                tk.END, f"Data element: {item_de}\n | Company Name: {item_name}\n\n"
            )
        open_file_dialog(data)


def get_participants(system_data):
    participant_data = {}
    for item in system_data["data"]["produces"]:
        to_list = item["to"]
        for participant in to_list:
            # print(f"participant = {participant}")
            participant_name = participant["name"]
            participant_id = participant["id"]
            data_element = item["id"]
            system_id = participant["systems"][0]["id"]
            if participant_name not in participant_data:
                participant_data[participant_name] = []
            participant_data[participant_name].append(
                {
                    "id": participant_id,
                    "name": participant_name,
                    "data_element": data_element,
                    "system_id": system_id,
                }
            )
    return participant_data

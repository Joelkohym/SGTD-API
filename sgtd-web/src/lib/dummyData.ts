 export const columns = [
    { Header: "Due To Arrive Time", accessor: "duetoArriveTime", sortable: true },
    { Header: "Location From", accessor: "locationFrom", sortable: true },
    { Header: "Vessel Name", accessor: "vesselName", sortable: true },
    { Header: "Call Sign", accessor: "callSign", sortable: true },
    { Header: "IMO Number", accessor: "IMOnumber", sortable: true },
    { Header: "Flag", accessor: "flag", sortable: true },
    { Header: "Due To Depart Time", accessor: "dueToDepartTime", sortable: true },
  ];

export const PDFColumns = [
    { header: "Due To Arrive Time", dataKey: "duetoArriveTime" },
    { header: "Location From", dataKey: "locationFrom" },
    { header: "Vessel Name", dataKey: "vesselName" },
    { header: "Call Sign", dataKey: "callSign" },
    { header: "IMO Number", dataKey: "IMOnumber" },
    { header: "Flag", dataKey: "flag" },
    { header: "Due To Depart Time", dataKey: "dueToDepartTime"},
];
  
export const tableData : any[] = [
    {
        "index": 0,
        "duetoArriveTime": "2023-10-18 13:00:00",
        "locationFrom": "PILOT EAST BOARD GRD A",
        "vesselName": "MONACO",
        "callSign": "A8IF2",
        "IMOnumber": "9314961",
        "flag": "LR",
        "dueToDepartTime": null,
        "location": "PASIR PANJANG BERTH 09",
        "grid": "",
        "purpose": "#1 Loading / Unloading Cargo, #5 Changing Crew",
        "agent": "SAMUDERA SHIPPING LINE LTD",
        "reportedArrivalTime": "2023-10-11 00:10:00"
    },
    {
        "index": 1,
        "duetoArriveTime": "2023-10-19 00:00:00",
        "locationFrom": "PILOT WEST BOARD GRD A",
        "vesselName": "SEASPAN ADONIS",
        "callSign": "VRTF4",
        "IMOnumber": "9468293",
        "flag": "HK",
        "dueToDepartTime": null,
        "location": "PASIR PANJANG BERTH 26",
        "grid": "",
        "purpose": "#1 Loading / Unloading Cargo, #3 Taking Bunker, #5 Changing Crew",
        "agent": "OCEAN NETWORK EXPRESS PTE LTD",
        "reportedArrivalTime": "2023-09-25 17:15:00"
    }
]
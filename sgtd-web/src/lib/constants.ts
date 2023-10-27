export const formFieldTypes = {
    input: "input",
    text: "text",
    email: "email",
    password: "password",
    button: "button",
    submit: "submit",
    url: "url",
  };

export const AppRoutes = {
  Home : "/home",
  Login : "/",
  Register: "/register",
  VesselQuery: "/vesselQuery",
  TableView : "/tableView",
  TriangularModule: "/triangularModule",
  VesselMap: "/VesselMap",
  VesselETA: "/VesselETA"
}

export const API_ENDPOINT = "https://sgtd-api-test.onrender.com"

export const API_Methods = {
  Login: '/login',
  Register: '/register',
  Table_view: '/api/table_pull'
}

export const API_Response_Success = 304;
export const API_Response_OK = 200

export const Response_Message = {
  Success: "Success",
  Error : "Error"
}

export const AlertType = {
  Success: "Success",
  Error : "Error"
}

export const tileLayer = {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
  url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
}
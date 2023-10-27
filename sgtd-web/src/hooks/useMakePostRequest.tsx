import { API_ENDPOINT, API_Response_Success, Response_Message } from "../lib/constants";


export function useMakePOSTRequest() {
  function makePOSTRequest(methodEndpoint: any, params?: any) {
    return new Promise((resolve, reject) => {
      let data = "";
      for (let key in params) {
        data += key + "=" + params[key] + "&";
      }
     const requestOptions: any = {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: data,
      };

      fetch(API_ENDPOINT + methodEndpoint, requestOptions)
        .then((response) => response.json())
          .then( (response) => {
           resolve(response)
        }
        )
        .catch((error) => reject(error));
    });
  }
  return [makePOSTRequest]
}

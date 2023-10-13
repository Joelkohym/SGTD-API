import { API_ENDPOINT } from "../lib/constants";

export function useMakeGETRequest() {
  function makeGETRequest(methodEndpoint: any, params?: any) {
    return new Promise((resolve, reject) => {
      let data = "";
      params && Object.keys(params).forEach((key) => {
        data += key + "=" + params[key] + "&";
      });
      const requestOptions: any = {
        method: "GET",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      };
      fetch(API_ENDPOINT + methodEndpoint + "?" + data, requestOptions)
        .then((res) => {
          console.log("Response...",res)
        })
        .catch((error) => reject(error));
    });
  }
  return [makeGETRequest];
}

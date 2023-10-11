
import { formFieldTypes } from "./constants"

export function validateInput(value: string, fieldName: string, type : string){
        if(value == ""){
          return `${fieldName} cannot be empty`
        } else if( type == formFieldTypes.email){
          let isValid = !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value) ? false : true
          if (!isValid) {
            return "Not a valid Email address"
          }
        }
}
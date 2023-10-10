import {atomWithReset} from "jotai/utils"
import { AlertType } from "../lib/constants";

const popupAtom = atomWithReset({isOpen: false, message: "", type: AlertType.Error, btnHandler:()=>{}})

export { 
  popupAtom, 
};
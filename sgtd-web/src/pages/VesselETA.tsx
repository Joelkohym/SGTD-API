import React, { useRef } from "react";
import Layout from "../components/Layout";
import { API_Methods, AlertType, AppRoutes, Response_Message, formFieldTypes } from "../lib/constants";
import styled from "styled-components";
import AppColors from "../styles/colors";
import FormController from "../components/FormController";
import { sharedButtonStyle, sharedFlexCenter } from "../styles/global";
import { useMakePOSTRequest } from "../hooks/useMakePostRequest";
import { useNavigate } from "react-router-dom";
import { useResetAtom } from "jotai/utils";
import { popupAtom } from "../jotai/store";
import { useAtom } from "jotai";

const VesselETA: React.FC = () => {
  const { input, submit, text } = formFieldTypes;
  const [getVesselTableData] = useMakePOSTRequest()
  const navigate = useNavigate();
  const resetPopup = useResetAtom(popupAtom);
  const [popupData, setPopupData] = useAtom(popupAtom);
  const alertMessage = useRef("")

  const formFields = {
    fields: [
      {
        name: "vessel_imo",
        label: "Vessel IMO for Table View",
        placeholder: "Enter Vessel IMO for Table View",
        defaultValue: "",
        type: input,
        inputType: text,
      },
    ],
    buttons: [
      {
        name: "Search",
        type: submit,
        onSubmitHandler: (data: any) => handleVesselQuery(data),
        style: sharedButtonStyle,
      },
    ],
  };

  const handleVesselQuery = async(data: any) => {
    navigate(AppRoutes.TableView)
    try {
      let res = await getVesselTableData(API_Methods.Table_view, {
       imo: data.vessel_imo,
      });
      if (res == Response_Message.Success) {
        
      } else {
        alertMessage.current = "Login Failed! Try Again";
        handlePopData();
      }
    } catch (error) {
      alertMessage.current = "Login Failed! Try Again";
      handlePopData();
    }
  }

  function handlePopData() {
    setPopupData({
      isOpen: true,
      message: alertMessage.current,
      type: AlertType.Error,
      btnHandler: resetPopup,
    });
  }
  
  return (
    <Layout>
      <FormContainer>
        <Title>Table view for IMO</Title>
        <FormController formFields={formFields} />
      </FormContainer>
    </Layout>
  );
};

export default VesselETA;

export const FormContainer = styled.div`
  background: ${AppColors.White};
  width: 25rem;
  height: 20rem;
  ${sharedFlexCenter}
  flex-direction: column;
  box-shadow: 2px 2px 10px 2px ${AppColors.ThemePurple};
`;

export const Title = styled.h3`
  padding: 1rem;
`;

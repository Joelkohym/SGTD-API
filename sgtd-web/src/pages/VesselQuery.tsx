import React from "react";
import Layout from "../components/Layout";
import FormController from "../components/FormController";
import { sharedButtonStyle } from "../styles/global";
import { AppRoutes, formFieldTypes } from "../lib/constants";
import { useNavigate } from "react-router-dom";
import { FormContainer, Title } from "./VesselETA";

const VesselQuery: React.FC = () => {
  const navigate = useNavigate();
  const { input, submit, text } = formFieldTypes;

  const formFields = {
    fields: [
      {
        name: "vessel_imo",
        label: "Vessel IMO Number",
        placeholder: "i.e. 9000000,9111111,92222222",
        defaultValue: "",
        type: input,
        inputType: text,
      },
    ],
    buttons: [
      {
        name: "Request",
        type: submit,
        onSubmitHandler: (data: any) => handleVesselQueryRequest(data),
        style: sharedButtonStyle,
      },
    ],
  };

  function handleVesselQueryRequest(data: any) {
    navigate(AppRoutes.VesselMap)
  }
  return (
    <Layout>
      <FormContainer>
        <Title>Vessel Request form</Title>
        <FormController formFields={formFields} />
      </FormContainer>
    </Layout>
  );
};

export default VesselQuery;
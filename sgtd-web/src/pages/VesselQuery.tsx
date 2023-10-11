import React from "react";
import Layout from "../components/Layout";
import { FormContainer, Title } from "./TableView";
import FormController from "../components/FormController";
import { sharedButtonStyle } from "../styles/global";
import { formFieldTypes } from "../lib/constants";

const VesselQuery: React.FC = () => {
  const { input, submit, text, email } = formFieldTypes;

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
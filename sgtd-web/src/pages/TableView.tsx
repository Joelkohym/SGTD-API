import React from "react";
import Layout from "../components/Layout";
import { formFieldTypes } from "../lib/constants";
import styled from "styled-components";
import AppColors from "../styles/colors";
import FormController from "../components/FormController";
import { sharedButtonStyle, sharedFlexCenter } from "../styles/global";

const TableView: React.FC = () => {
  const { input, submit, text } = formFieldTypes;

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

  function handleVesselQuery(data: any) {}
  return (
    <Layout>
      <FormContainer>
        <Title>Table view for IMO</Title>
        <FormController formFields={formFields} />
      </FormContainer>
    </Layout>
  );
};

export default TableView;

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

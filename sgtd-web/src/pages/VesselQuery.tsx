import React from 'react'
import Layout from '../components/Layout'
import { FormContainer, Title } from './TableView'
import FormController from '../components/FormController'
import { sharedButtonStyle } from '../styles/global';
import { formFieldTypes } from '../lib/constants';
import styled from 'styled-components';

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
      {
        name: "email",
        label: "Email",
        placeholder: "Email",
        defaultValue: "test@sgtradex.com",
        type: input,
        inputType: email,
        disabled : true
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

  function handleVesselQueryRequest( data:any)  {
    
  }
  return (
    <Layout>
       <Container>
          <Title>Vessel Request form</Title>
          <FormController formFields={formFields} />
        </Container>
    </Layout>
  )
}

export default VesselQuery

const Container = styled(FormContainer)`
  width: 30rem;
  height: 25rem;
`
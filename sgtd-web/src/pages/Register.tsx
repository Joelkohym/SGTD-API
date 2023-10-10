import React from 'react'
import { sharedButtonStyle, sharedFlexCenter,Image, sharedFlexSpaceBetween } from '../styles/global'
import FormController from '../components/FormController'
import { AppRoutes, formFieldTypes } from '../lib/constants';
import styled, { css } from 'styled-components';
import AppColors from '../styles/colors';
import { FormTitle, Link, LogoContainer } from './Login';

function Register() {
    const { input, password, email, submit, text } = formFieldTypes;
    const formFields = {
        fields: [
          {
            name: "Email",
            label: "Email",
            placeholder: "Email",
            defaultValue: "",
            type: input,
            inputType: email,
            style: InputStyle,
            enableInputStyleWithValue : true
          }, {
            name: "password",
            label: "Password",
            placeholder: "Password",
            defaultValue: "",
            inputType: password,
            type: password,
            style: InputStyle,
            enableInputStyleWithValue : true
          }, {
            name: "ApiKey",
            label: "API Key",
            placeholder: "Enter SGTD pitstop API KEY",
            defaultValue: "",
            type: input,
            inputType: text,
            style: InputStyle,
            enableInputStyleWithValue : true
          }, {
            name: "ParticipantID",
            label: "Participant ID",
            placeholder: "Enter SGTD pitstop Participant ID",
            defaultValue: "",
            type: input,
            inputType: text,
            style: InputStyle,
            enableInputStyleWithValue : true
          }, {
            name: "credPath",
            label: "Gsheet cred path",
            placeholder: "Enter gsheet_cred_path",
            defaultValue: "",
            type: input,
            inputType: text,
            style: InputStyle,
            enableInputStyleWithValue : true
          }, {
            name: "PitstopURL",
            label: "Pitstop URL",
            placeholder: "Enter Pitstop URL",
            defaultValue: "",
            type: input,
            inputType: text,
            style: InputStyle,
            enableInputStyleWithValue : true
          }
        ],
        buttons: [
          {
            name: "Register",
            type: submit,
            onSubmitHandler: (data: any) => register(data),
            style: btnStyle,
          },
        ],
      };

    const register = (data:any) => {
        console.log("register",data)
    }
  return (
    <RegisterPage>
        <Header>
            <LogoContainer>
                <Image src = "https://sgtradex.com/images/sgtradex-logo.svg"/>
            </LogoContainer>
            <SideTitle>Already have an account? <SideLink href={AppRoutes.Login}> Login</SideLink> </SideTitle>
        </Header>
        <FormContainer>
        <Title>REGISTRATION FORM</Title>
        <FormController formFields={formFields} isFormRow/>
        </FormContainer>
    </RegisterPage>
  )
}

export default Register

const RegisterPage = styled.div`
height: 100vh;
background: linear-gradient(
  135deg,
  ${AppColors.ThemeBlue},
  ${AppColors.ThemeLightPurple}
);
`

const Header = styled.div`
    width:100%;
    ${sharedFlexSpaceBetween}
    align-self: flex-start;
`

const Title = styled(FormTitle)`
    color: ${AppColors.White}
`

const SideTitle = styled.div`
    align-self: flex-end;
    padding: 0 2rem 3rem 0;
`

const FormContainer = styled.div`
    ${sharedFlexCenter}
    flex-direction: column;
`

const InputStyle = css`
    background-color: ${AppColors.ThemeLightTransparencyBlack};
    padding: 0.75rem 1rem;
    border-width: 0 0 2px 0px;
    margin: 0.5rem 0;
    border-color: ${AppColors.ThemeBlack};
    border-radius: 1rem;
    outline:none;
    width: 90%;
    &:focus {
    border-color: ${AppColors.ThemeBlue};
    outline: 2px solid transparent;
    outline-offset: 2px
    }
    &::placeholder{
        color: ${AppColors.ThemeLightBlack}
    }
`

const btnStyle = css`
    ${sharedButtonStyle}
    width:15rem;
    margin: 2rem;
`

const SideLink = styled(Link)`
color: ${AppColors.White};
`

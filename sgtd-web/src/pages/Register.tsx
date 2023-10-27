import React, { useRef } from "react";
import {
  sharedButtonStyle,
  sharedFlexCenter,
  Image,
  sharedFlexSpaceBetween,
} from "../styles/global";
import FormController from "../components/FormController";
import { API_Methods, AlertType, AppRoutes, Response_Message, formFieldTypes } from "../lib/constants";
import styled, { css } from "styled-components";
import AppColors from "../styles/colors";
import { FormTitle, Link, LogoContainer } from "./Login";
import { useNavigate } from "react-router-dom";
import { useMakePOSTRequest } from "../hooks/useMakePostRequest";
import { useResetAtom } from "jotai/utils";
import { popupAtom } from "../jotai/store";
import { useAtom } from "jotai";
import Popup from "../components/Popup";

function Register() {
  const navigate = useNavigate();
  const [registerUser] = useMakePOSTRequest();
  const resetPopup = useResetAtom(popupAtom);
  const [popupData, setPopupData] = useAtom(popupAtom);
  const alertMessage = useRef({
    type: "",
    message: "",
    action: () => {}
  });
  const { input, password, email, submit, text, url } = formFieldTypes;

  const formFields = {
    fields: [
      {
        name: "email",
        label: "Email",
        placeholder: "Email",
        defaultValue: "",
        type: input,
        inputType: email,
        style: InputStyle,
        enableInputStyleWithValue: true,
      },
      {
        name: "password",
        label: "Password",
        placeholder: "Password",
        defaultValue: "",
        inputType: password,
        type: password,
        style: InputStyle,
        enableInputStyleWithValue: true,
      }, {
        name: "api_key",
        label: "API Key",
        placeholder: "Enter SGTD pitstop API KEY",
        defaultValue: "",
        type: input,
        inputType: text,
        style: InputStyle,
        enableInputStyleWithValue: true,
      }, {
        name: "participant_id",
        label: "Participant ID",
        placeholder: "Enter SGTD pitstop Participant ID",
        defaultValue: "",
        type: input,
        inputType: text,
        style: InputStyle,
        enableInputStyleWithValue: true,
      },
      {
        name: "gsheet_cred_path",
        label: "Gsheet cred path",
        placeholder: "Enter gsheet_cred_path",
        defaultValue: "",
        type: input,
        inputType: text,
        style: InputStyle,
        enableInputStyleWithValue: true,
      },
      {
        name: "pitstop_url",
        label: "Pitstop URL",
        placeholder: "Enter Pitstop URL",
        defaultValue: "",
        type: url,
        inputType: url,
        style: InputStyle,
        enableInputStyleWithValue: true,
      },
    ],
    buttons: [
      {
        name: "Register",
        type: submit,
        onSubmitHandler: (data: any) => handleRegister(data),
        style: btnStyle,
      },
    ],
  };

  const handleRegister = async (data: any) => {
    if (
      (data.email == "" ||
        data.password == "" ||
        data.api_key == "" ||
        data.participant_id == "",
      data.gsheet_cred_path == "" || data.pitstop_url == "")
    ) {
      alertMessage.current = {
        type: AlertType.Error,
        message: "Fields cannot be empty",
        action: resetPopup
      }
      handlePopup();
      return;
    }
    try {
      let requestData = {
        email: data.email,
        password: data.password,
        api_key: data.api_key,
        participant_id: data.participant_id,
        gsheet_cred_path: data.gsheet_cred_path,
        pitstop_url: data.pitstop_url,
      };
      let res:any = await registerUser(API_Methods.Register,requestData)
      if (res.status == 200) {
        alertMessage.current = {
          type: AlertType.Success,
          message: "Registered SuccessFully, Login now",
          action: () => {
            navigate(AppRoutes.Login)
            resetPopup()
          }
        }
        handlePopup()
      } else if (res.status == 409) {
        alertMessage.current = {
          type: AlertType.Error,
          message: "Your email exists in database! Please reach out to Admin if you need assistance",
          action: resetPopup
        }
        handlePopup();
      }
    } catch (error) {
      alertMessage.current = {
        type: AlertType.Error,
        message: "Something went wrong. Try again",
        action: resetPopup
      }
      handlePopup();
    }
  };

  function handlePopup() {
    setPopupData({
      isOpen: true,
      message: alertMessage.current.message,
      type: alertMessage.current.type,
      btnHandler: alertMessage.current.action,
    });
  }

  return (
    <RegisterPage>
      <Header>
        <LogoContainer>
          <Image src="https://sgtradex.com/images/sgtradex-logo.svg" />
        </LogoContainer>
        <SideTitle>
          Already have an account?{" "}
          <SideLink href={AppRoutes.Login}> Login</SideLink>{" "}
        </SideTitle>
      </Header>
      <FormContainer>
        <Title>REGISTRATION FORM</Title>
        <FormController formFields={formFields} isFormRow />
      </FormContainer>
      {popupData.isOpen && <Popup />}
    </RegisterPage>
  );
}

export default Register;

const RegisterPage = styled.div`
  height: 100vh;
  background: linear-gradient(
    135deg,
    ${AppColors.ThemeBlue},
    ${AppColors.ThemeLightPurple}
  );
`;

const Header = styled.div`
  width: 100%;
  ${sharedFlexSpaceBetween}
  align-self: flex-start;
`;

const Title = styled(FormTitle)`
  color: ${AppColors.White};
`;

const SideTitle = styled.div`
  align-self: flex-end;
  padding: 0 2rem 3rem 0;
`;

const FormContainer = styled.div`
  ${sharedFlexCenter}
  flex-direction: column;
`;

const InputStyle = css`
  background-color: ${AppColors.ThemeLightTransparencyBlack};
  padding: 0.75rem 1rem;
  border-width: 0 0 2px 0px;
  margin: 0.5rem 0;
  border-color: ${AppColors.ThemeBlack};
  border-radius: 1rem;
  outline: none;
  width: 90%;
  &:focus {
    border-color: ${AppColors.ThemeBlue};
    outline: 2px solid transparent;
    outline-offset: 2px;
  }
  &::placeholder {
    color: ${AppColors.ThemeLightBlack};
  }
`;

const btnStyle = css`
  ${sharedButtonStyle}
  width:15rem;
  margin: 2rem;
`;

const SideLink = styled(Link)`
  color: ${AppColors.White};
`;

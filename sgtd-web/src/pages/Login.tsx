import styled from "styled-components";
import {
  sharedButtonStyle,
  Image,
  sharedFlexSpaceBetween,
  Section,
} from "../styles/global";
import AppColors from "../styles/colors";
import FormController from "../components/FormController";
import { API_Methods, AlertType, AppRoutes, Response_Message, formFieldTypes } from "../lib/constants";
import { useNavigate } from "react-router-dom";
import { useMakePOSTRequest } from "../hooks/useMakePostRequest";
import Popup from "../components/Popup";
import { useResetAtom } from "jotai/utils";
import { popupAtom } from "../jotai/store";
import { useAtom } from "jotai";
import { useRef } from "react";

function Login() {
  const navigate = useNavigate();
  const [getLogin] = useMakePOSTRequest();
  const { input, password, email, submit } = formFieldTypes;
  const resetPopup = useResetAtom(popupAtom);
  const [popupData, setPopupData] = useAtom(popupAtom);
  const alertMessage = useRef("")

  const formFields = {
    fields: [
      {
        name: "email",
        label: "Email",
        placeholder: "Email",
        defaultValue: "",
        type: input,
        inputType: email,
      },
      {
        name: "password",
        label: "Password",
        placeholder: "Password",
        defaultValue: "",
        inputType: password,
        type: password,
      },
    ],
    buttons: [
      {
        name: "Login",
        type: submit,
        onSubmitHandler: (data: any) => handleLogin(data),
        style: sharedButtonStyle,
      },
    ],
  };

  const handleLogin = async(data: any) => {
    if (data.email == ""){
      alertMessage.current = "Email cannot be empty"
      handlePopData()
      return
    } else if(data.password == ""){
      alertMessage.current = "Password cannot be empty"
      handlePopData()
      return
    }
    try {
    let res = await getLogin(API_Methods.Login,{
      email: data.email,
      password: data.password,
    })
    if (res == Response_Message.Success) {
      navigate('/home')
    } else {
      alertMessage.current = "Login Failed! Try Again"
      handlePopData()
    }
  } catch (error){
    alertMessage.current = "Login Failed! Try Again"
    handlePopData()
  }  
  };

  function handlePopData() {
    setPopupData({
      isOpen: true,
      message: alertMessage.current,
      type: AlertType.Error,
      btnHandler: resetPopup
    });
  }



  return (
    <Section>
      <LogoContainer>
        <Image src="https://sgtradex.com/images/sgtradex-logo.svg" />
      </LogoContainer>
      <FormContainer>
        <FormTitle>LOGIN</FormTitle>
        <FormController formFields={formFields} />
        <Footer>
          {" "}
          Don't have an account? <Link href = {AppRoutes.Register}>Register</Link>
        </Footer>
      </FormContainer>
      {popupData.isOpen && <Popup />}
    </Section>
  );
}

export default Login;

export const LogoContainer = styled.div`
  width: 8rem;
  padding: 1rem;
`;

const FormContainer = styled.div`
  background: ${AppColors.White};
  width: 28rem;
  height: 25rem;
  border-radius: 2rem;
  ${sharedFlexSpaceBetween}
  flex-direction: column;
`;
export const FormTitle = styled.h1`
  padding: 1rem 2rem;
`;

const Footer = styled.div`
  font-size: 1rem;
  padding: 1rem;
`;
export const Link = styled.a`
  color: ${AppColors.ThemeBlue};
  font-weight: 700;
  cursor: pointer;
  text-decoration:none;
`;

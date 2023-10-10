import styled from "styled-components";
import {
  sharedButtonStyle,
  Image,
  sharedFlexSpaceBetween,
  Section,
} from "../styles/global";
import AppColors from "../styles/colors";
import FormController from "../components/FormController";
import { API_Methods, AppRoutes, Response_Message, formFieldTypes } from "../lib/constants";
import { useNavigate } from "react-router-dom";
import { useMakePOSTRequest } from "../hooks/useMakePostRequest";

function Login() {
  const navigate = useNavigate();
  const [getLogin] = useMakePOSTRequest();
  const { input, password, email, submit } = formFieldTypes;
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
    try {
    let res = await getLogin(API_Methods.Login,{
      email: data.email,
      password: data.password,
    })
    if (res == Response_Message.Success) {
      console.log("Success")
    } else {
      console.log("Failed")
    }
  } catch (error){
    console.log("Failed")
  }
    
  };
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

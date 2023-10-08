import styled from 'styled-components'
import { sharedButtonStyle, sharedFlexCenter,Image, sharedFlexSpaceBetween } from '../styles/global';
import AppColors from '../styles/colors';
import FormController from '../components/FormController';
import { formFieldTypes } from '../lib/constants';

function Login() {
  const { input, password, email, submit } = formFieldTypes;
  const formFields = {
    fields: [
      {
        name: "Email",
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
      }
    ],
    buttons: [
      {
        name: "Login",
        type: submit,
        onSubmitHandler: (data: any) => login(data),
        style: sharedButtonStyle
      },
    ],
  }

  const login = (data: any) => {
      console.log(".....",data)
  }
  return (
    <Section>
        <FormBackground>
          <LogoContainer>
            <Image src="https://sgtradex.com/images/sgtradex-logo.svg" />
          </LogoContainer>
           
            <FormContainer>
                <Header>LOGIN</Header>
                <FormController formFields={formFields} />
            </FormContainer>
        </FormBackground>

    </Section>
  )
}

export default Login;

const Section = styled.div`
width: 100vw;
height: 100vh;
background: ${AppColors.ThemeLightGrey};
${sharedFlexCenter}

`
const FormBackground = styled.div`
  width:60rem;
  height:30rem;
  border-radius: 4rem;
  background: linear-gradient(135deg, ${AppColors.ThemeBlue}, ${AppColors.ThemeLightPurple});
  box-shadow: 5px 5px 5px 10px ${AppColors.ThemeBlueShadow};
  ${sharedFlexSpaceBetween}
  flex-direction: column;
`
const LogoContainer = styled.div`
  width:8rem;
  margin-left: 5rem;
  align-self: flex-start
`

const FormContainer = styled.div`
    background: ${AppColors.White};
    width:28rem;
    height: 25rem;
    border-radius: 2rem 2rem 0 0;
`
const Header = styled.h1`
  padding: 1rem 2rem;
`


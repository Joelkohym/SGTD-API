import styled, { css } from "styled-components";
import AppColors from "./colors";

const sharedFlexCenter = css`
    display: flex;
    align-items: center;
    justify-content: center;
`

const sharedFlexSpaceBetween = css`
    display: flex;
    align-items: center;
    justify-content: space-between;
`
const sharedButtonStyle = css`
    width: 12rem;
    background: ${AppColors.ThemeLightPurple};
    padding: 1rem;
    &:hover{
        background: ${AppColors.ThemePurple};
    }
`
const Image = styled.img`
    width:100%;
    height:100%;
`
export const Section = styled.div`
  width: 100vw;
  height: 100vh;
  background: linear-gradient(
    135deg,
    ${AppColors.ThemeBlue},
    ${AppColors.ThemeLightPurple}
  );
  ${sharedFlexCenter}
  flex-direction: column;
`;

export{
    sharedFlexCenter,
    sharedFlexSpaceBetween,
    sharedButtonStyle,
    Image
}
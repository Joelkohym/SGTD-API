import React from 'react';
import styled, { RuleSet } from 'styled-components';
import AppColors from '../styles/colors';

interface ButtonProps {
    title: String;
    buttonStyle?:  RuleSet<object>;
    clickHandler : React.MouseEventHandler<HTMLButtonElement>;
    }


const Button: React.FC<ButtonProps> = ({title, buttonStyle,clickHandler}) =>{
    return  <CustomButton onClick={clickHandler} $style={buttonStyle}>{title}</CustomButton>
}

export default Button

const CustomButton = styled.button<{$style?: RuleSet<Object>}>`
    padding: 0.5rem 1rem;
    font-weight: 600;
    border-radius: 0.25rem;
    margin: 0.25rem;
    border:none;
    --shadow: 0 4px 6px -1px ${AppColors.ThemePrimaryTransparencyBlack},
    0 2px 4px -1px ${AppColors.ThemeLightTransparencyBlack};
    box-shadow: 0 0 ${AppColors.ThemeBlack}, 0 0 ${AppColors.ThemeBlack}, 0 0 var(--black),
    0 0 ${AppColors.ThemeBlack}, var(--shadow);
    color: ${AppColors.White};
    cursor: pointer;
    ${(props)=> props.$style}
`
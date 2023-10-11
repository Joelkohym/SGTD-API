import React from 'react'
import styled from 'styled-components'
import { sharedFlexCenter } from '../styles/global'
import AppColors from '../styles/colors'
import {BsFillCheckCircleFill} from 'react-icons/bs'
import {BiSolidError} from 'react-icons/bi'
import { useAtomValue } from 'jotai'
import { popupAtom } from '../jotai/store'
import { AlertType } from '../lib/constants'
import { useResetAtom } from 'jotai/utils'

const PopupData = {
    Success: {
        color: AppColors.ThemeSuccess,
        icon: <BsFillCheckCircleFill size={25}/>,
        title: "Success"
    },
    Error: {
        color: AppColors.ThemeError,
        icon: <BiSolidError size={25}/>,
        title: "Alert"
    }
}

const Popup : React.FC = () => {
  const { type , message, btnHandler }  = useAtomValue(popupAtom);
  const resetPopup = useResetAtom(popupAtom);
  const data = type == AlertType.Success ? PopupData.Success : PopupData.Error
  return (
    <OverlayLayer onClick={resetPopup}>
        <PopupContainer>
            <PopupHeader $color={data.color}>
                {data.icon} 
                <Text>{` ${data.title}`}</Text>
            </PopupHeader>
            <Description>{message}</Description>
            <PopupBtn $color= {data.color} onClick={btnHandler}>OK</PopupBtn>
        </PopupContainer>
    </OverlayLayer>
  )
}

export default Popup

const OverlayLayer = styled.div`
  position: absolute;
  top: 0px;
  left: 0px;
  z-index: 50;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  ${sharedFlexCenter}
  align-self: center;
  background: ${AppColors.ThemeTransparencyBlack}
 
`

const PopupContainer = styled.div`
    width: 25rem;
    height: 20rem;
    background: ${AppColors.White};
    border-radius: 1rem;
    ${sharedFlexCenter};
    justify-content: flex-start;
    flex-direction: column;
`
const PopupHeader = styled.div<{$color: AppColors}>`
    width:100%;
    height: 5rem;
    background: ${props => props.$color};
    ${sharedFlexCenter}
    border-radius: 1rem 1rem 0 0;
`
const Text = styled.h1`
    padding: 0 1rem;
`

const Description = styled.div`
    padding: 3rem;
    font-weight: 600;
    ${sharedFlexCenter}
    align-self:center;
`

const PopupBtn = styled.button<{$color: AppColors}>`
    ${sharedFlexCenter}
    align-self:center;
    width: 9rem;
    background: ${props => props.$color};
    font-size: 1.2rem;
    padding: 1rem 0;
    font-weight:600;
    border:none;    
`
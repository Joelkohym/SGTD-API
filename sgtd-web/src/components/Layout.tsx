import React, { useState } from "react";
import { FaExpand, FaSignOutAlt, FaTable } from "react-icons/fa";
import { MdClose } from "react-icons/md";
import { TbBrandGoogleBigQuery, TbTriangleSquareCircle } from "react-icons/tb";
import styled from "styled-components";
import AppColors from "../styles/colors";
import { Image, sharedFlexCenter } from "../styles/global";
import { useLocation, useNavigate } from "react-router-dom";
import { AppRoutes } from "../lib/constants";

interface LayoutProps {
  children?: any;
}

const NavButtonData = [
  {
    label: "Vessel Query",
    link: AppRoutes.VesselQuery,
    icon: <TbBrandGoogleBigQuery size={25} />,
    isPublic: true,
  },
  {
    label: "Vessel ETA",
    link: AppRoutes.VesselETA,
    icon: <FaTable size={25} />,
    isPublic: true,
  },
  {
    label: "Logout",
    link: ``,
    icon: <FaSignOutAlt size={25} />,
    isPublic: true,
  },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [showMenu, setShowMenu] = useState(true);
  const navigate = useNavigate()
  const location = useLocation();
  return (
    <DrawerContainer>
      <SideMenu $showMenu={showMenu}>
        <DrawerIconContainer
          $showMenu={showMenu}
          $isActive={false}
          onClick={() => {
            setShowMenu(!showMenu);
          }}
        >
          {showMenu ?  <MdClose size={25}/> :<FaExpand size={20}/> }
        </DrawerIconContainer>
        <LogoContainer $showMenu={showMenu}>
            <Image src="https://sgtradex.com/images/sgtradex-logo.svg"/>
        </LogoContainer>
        <NavItem>
          {NavButtonData.map(
            (btnData, index) =>
              btnData.isPublic && (
                    <NavLink
                    $isActive={location.pathname == btnData.link}
                    $showMenu={showMenu}
                    onClick={() => navigate(btnData.link)}
                    key={index}
                  >
                    <div>{btnData.icon}</div>
                    {showMenu && <NavTitle>{btnData.label}</NavTitle>}
                  </NavLink>
                                )
          )}
        </NavItem>
      </SideMenu>
      <Page>
        <PageContent>{children}</PageContent>
      </Page>
    </DrawerContainer>
  );
};

export default Layout;

const DrawerContainer = styled.div`
  display: flex;
  width: 100vw;
  height: 100vh;
`;
const NavLink = styled.a<{ $showMenu: boolean; $isActive: boolean }>`
    display: flex;
    align-items: center;
    color: ${AppColors.White};
    font-weight: 600;
    width: 100%;
    font-size: 0.875rem;
    line-height: 1.25rem;
    padding: 0.8rem 0;
    justify-content: ${(props) => (props.$showMenu ? `flex-start` : `center`)};
    background: ${(props) => (props.$isActive ? AppColors.ThemeLightTransparencyBlack : "")};
    text-decoration: none;
    margin: 0.1rem 0;
    &:hover{
      background: ${AppColors.ThemeLightTransparencyBlack};
    }
`;

const DrawerIconContainer = styled(NavLink)`
  cursor: pointer;
  width: max-content;
  align-self: ${(props) => (props.$showMenu ? `flex-end` : `center`)}
`;

const LogoContainer = styled.div<{$showMenu: boolean}>`
    ${sharedFlexCenter}
    height: ${(props) => props.$showMenu ? "12%": "5%"};
    padding-top: 2.5rem;
`

const SideMenu = styled.div<{ $showMenu: boolean }>`
  height: 100vh;
  ${sharedFlexCenter}
  flex-direction: column;
  background-color: ${AppColors.ThemeBlue};
  background: linear-gradient(
  180deg,
  ${AppColors.ThemeBlue},
  ${AppColors.ThemeLightPurple});
  box-shadow: 0 8px 2px -2px ${AppColors.ThemeLightGrey};
  width: ${(props) => (props.$showMenu ? `15%` : `5%`)}
`;

const NavItem = styled.div`
  height: 90%;
  width: 95%;
  display:flex;
  align-Items: center;
  flex-direction: column;
  padding-top: 2.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  
`;

const NavTitle = styled.div`
  margin-left: 1.25rem;
`;

const Page = styled.div`
  width: 100%;
`;

const PageContent = styled.div`
  height: 95%;
  flex-direction: column;
  ${sharedFlexCenter}
  width: 98%;
`;


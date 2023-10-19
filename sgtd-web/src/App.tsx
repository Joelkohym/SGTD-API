import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './pages/Login';
import Register from "./pages/Register";
import Home from "./pages/Home";
import { AppRoutes } from "./lib/constants";
import VesselQuery from "./pages/VesselQuery";
import TableView from "./pages/TableView";
import TriangularModule from "./pages/TriangularModule";
import VesselMap from "./pages/VesselMap";

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path={AppRoutes.Login} element={<Login />}/>
      <Route path={AppRoutes.Register} element={<Register />}/>
      <Route path = {AppRoutes.Home} element = {<Home/>} />
      <Route path = {AppRoutes.VesselQuery} element = {<VesselQuery/>} />
      <Route path = {AppRoutes.TableView} element = {<TableView/>} />
      <Route path = {AppRoutes.TriangularModule} element = {<TriangularModule/>} />
      <Route path = {AppRoutes.VesselMap} element = {<VesselMap />} />
    </Routes>
  </BrowserRouter>
  );
}

export default App;

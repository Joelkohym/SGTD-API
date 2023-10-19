import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { tileLayer } from "../lib/constants";
import { LatLngExpression } from "leaflet";
import Layout from "../components/Layout";
import styled from "styled-components";
import { mapData } from "../lib/mapData";
import PolygonMarker from "../components/PolygonMarker";
import { sharedFlexCenter } from "../styles/global";
import VesselMarker from "../components/VesselMarker";

const VesselMap = () => {
  const center: LatLngExpression = [1.257167, 103.897];

  return (
    <Layout>
      <Container>
        <MapSection>
          <MapContainer
            center={center}
            zoom={11}
            scrollWheelZoom={true}
            style={{ width: "45rem", height: "35rem" }}
          >
            <TileLayer {...tileLayer} />
            {/* <Marker position={[51.505, -0.09]}>
       
      </Marker> */}
            {mapData.map((data) => {
              return (
                <PolygonMarker
                  coordinates={data.coordinates}
                  name={data.name}
                />
              );
            })}
            <VesselMarker coordinates={[1.20442, 103.81]} />
          </MapContainer>
        </MapSection>
      </Container>
    </Layout>
  );
};

export default VesselMap;

const MapSection = styled.div`
  width: 45rem;
  height: 35rem;
  border: 2px solid black;
`;
const Container = styled.div`
  width: 100%;
  height: 100vh;
  ${sharedFlexCenter}
`;

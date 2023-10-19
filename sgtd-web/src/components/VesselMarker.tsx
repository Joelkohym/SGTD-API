import React from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import customIcon from '../assets/arrow.png'
interface VesselMarkerProps {
  coordinates: any;
  name?: string;
}

const VesselMarker: React.FC<VesselMarkerProps> = ({ coordinates, name }) => {
    const customMarkerIcon = new L.Icon({
        iconUrl: customIcon,
        iconSize: [32, 32], // Set the icon size
        iconAnchor: [16, 32], // Set the anchor point
      });
  
  return (
    <Marker position={coordinates} icon={customMarkerIcon}>
      <Popup>
        Data is in progress
      </Popup>
    </Marker>
  );
};

export default React.memo(VesselMarker);

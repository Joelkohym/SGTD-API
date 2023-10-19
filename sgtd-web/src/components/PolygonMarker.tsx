import React from "react";
import { useMemo, useState } from "react";
import { Polygon, Popup } from "react-leaflet";
import AppColors from "../styles/colors";

interface PolygonMarkerProps {
  coordinates: any;
  name: string;
}

const PolygonMarker: React.FC<PolygonMarkerProps> = ({ coordinates, name }) => {
  const [pathoption, setPathOption] = useState<any>({
    color: AppColors.ThemePurple,
    fillColor: AppColors.ThemeLightRed,
  });
  const eventHandlers = useMemo(
    () => ({
      mouseover() {
        setPathOption({ ...pathoption, fillColor: AppColors.ThemeSuccess });
      },
      mouseout() {
        setPathOption({ ...pathoption, fillColor: AppColors.ThemeLightRed });
      },
    }),
    []
  );
  return (
    <Polygon
      positions={coordinates}
      eventHandlers={eventHandlers}
      pathOptions={pathoption}
    >
      <Popup><b>Name:</b>{" "}{name}</Popup>
    </Polygon>
  );
};

export default React.memo(PolygonMarker);

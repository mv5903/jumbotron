import IPixel from "../interfaces/Pixel";

const PIXELSIZE = "1.2vh";

const Pixel = ({ pixel }: { pixel: IPixel }) => {
  return (
    <div
      title={`Brightness: ${pixel.brightness}`}
      className="border-white"
      style={{
        width: PIXELSIZE,
        height: PIXELSIZE,
        backgroundColor: `rgb(${pixel.r}, ${pixel.g}, ${pixel.b})`,
      }}
    ></div>
  );
};

export default Pixel;

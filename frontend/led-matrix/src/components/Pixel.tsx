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
        opacity: pixel.brightness as number / 255,
      }}
    ></div>
  );
};

export default Pixel;

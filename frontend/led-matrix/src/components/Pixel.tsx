import IPixel from "../interfaces/Pixel";


const Pixel = ({ pixel, mini }: { pixel: IPixel, mini: boolean }) => {
  const PIXELSIZE = mini ? ".2vh" : "1.2vh";
  return (
    <div className="tooltip" data-tip={`Brightness: ${pixel.brightness}`}>
      <div
        className="border-white"
        style={{
          width: PIXELSIZE,
          height: PIXELSIZE,
          backgroundColor: `rgb(${pixel.r}, ${pixel.g}, ${pixel.b})`,
          opacity: pixel.brightness as number / 255,
        }}
      ></div>
    </div>
  );
};

export default Pixel;

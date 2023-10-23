import IPixel from "../interfaces/Pixel";


const Pixel = ({ pixel, mini }: { pixel: IPixel, mini: boolean }) => {
  const PIXELSIZE = mini ? ".2vh" : "1.2vh";
  const DISPLAY_FACTOR = 5;
  return (
    <div className="tooltip" data-tip={`Brightness: ${pixel.brightness}`}>
      <div
        className="border-white"
        style={{
          width: PIXELSIZE,
          height: PIXELSIZE,
          backgroundColor: `rgb(${pixel.r}, ${pixel.g}, ${pixel.b})`,
          opacity: pixel.brightness as number / 255 * DISPLAY_FACTOR,
        }}
      ></div>
    </div>
  );
};

export default Pixel;

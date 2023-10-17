import { useContext, useEffect, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import Pixel from "./Pixel";
import IPixel from "../interfaces/Pixel";

export default function Jumbotron() {
  const [pixels, setPixels] = useState<IPixel[][]>();

  const jumbotronContext = useContext(JumbotronContext);
  if (!jumbotronContext) {
    throw new Error("Jumbotron Context not found");
  }

  const { jumbotron, setJumbotron } = jumbotronContext;
  console.log(jumbotron);

  useEffect(() => {
    let rowSize = jumbotron.rows;
    let colSize = jumbotron.columns;

    let jumbotronArr = [];
    for (let row = 0; row < rowSize; row++) {
      let tempArr = [];
      for (let col = 0; col < colSize; col++) {
        tempArr[col] = { r: 0, g: 0, b: 0, brightness: 0 } as IPixel;
      }
      jumbotronArr.push(tempArr);
    }
    setPixels(jumbotronArr);
  }, [jumbotron]);

  return (
    <>
      <h2>Jumbotron</h2>
      <div className="grid grid-cols-64 gap-1">
        {pixels?.map((pixelArr, index) => (
          <div key={index}>
            {pixelArr.map((pixel, i) => (
              <Pixel key={i} pixel={pixel} />
            ))}
          </div>
        ))}
      </div>
    </>
  );
}

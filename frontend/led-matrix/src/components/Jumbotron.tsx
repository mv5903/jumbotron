import { useContext, useEffect, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import Pixel from "./Pixel";
import IPixel from "../interfaces/Pixel";
import io from 'socket.io-client';  

export default function Jumbotron() {
  const [pixels, setPixels] = useState<IPixel[][]>();

  const jumbotronContext = useContext(JumbotronContext);
  if (!jumbotronContext) {
    throw new Error("Jumbotron Context not found");
  }

  const { jumbotron, setJumbotron } = jumbotronContext;
  console.log(jumbotron);

  useEffect(() => {
    let rowSize = Number(jumbotron.rows);
    let colSize = Number(jumbotron.columns);

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

  useEffect(() => {
      // Connect to the server
      const socket = io(`http://${jumbotron.ip}:5000/jumbotron`);

      // Register an event listener for the 'array_update' event
      socket.on('array_update', (update) => {
        console.log(update);
      });

      // Clean up the effect by disconnecting the socket when the component is unmounted
      return () => socket.disconnect();
  }, []);  // The empty dependency array means this effect will only run once, similar to componentDidMount

  //Huge Commit
  return (
    <div className="mt-12">
      <h2 className="mb-2 text-lg">Live View: Jumbotron</h2>
      <div className="grid grid-cols-64 gap-1 border-2 border-red-500 p-4">
        {pixels?.map((pixelArr, rowIndex) => 
          pixelArr.map((pixel, colIndex) => (
            <Pixel key={`${rowIndex}-${colIndex}`} pixel={pixel} />
          ))
        )}
      </div>
    </div>
  );
}

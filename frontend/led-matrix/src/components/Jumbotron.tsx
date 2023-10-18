import { useContext, useEffect, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import Pixel from "./Pixel";
import IPixel from "../interfaces/Pixel";
import io from 'socket.io-client';  
import { FaInfoCircle } from "react-icons/fa";

export default function Jumbotron() {
  const [pixels, setPixels] = useState<IPixel[][]>();
  const [latency, setLatency] = useState<string>("");
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [tryAgain, setTryAgain] = useState<boolean>(false);

  const jumbotronContext = useContext(JumbotronContext);
  if (!jumbotronContext) {
    throw new Error("Jumbotron Context not found");
  }

  const { jumbotron, setJumbotron } = jumbotronContext;

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
    socket.on('array_update', (response: { data: IPixel[][], timestamp: number }) => {
      setIsConnected(true);
      let latency = (Date.now() - (response.timestamp / 1000000));
      setLatency(latency.toFixed(0));
      setPixels(response.data);
    });

    // Handle disconnection
    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('connect_error', () => {
      setIsConnected(false);
    });

    socket.on('connect_timeout', () => {
      setIsConnected(false);
    });

    socket.on('reconnect_failed', () => {
      setIsConnected(false);
    });

    // Clean up the effect by disconnecting the socket when the component is unmounted
    return () => {
      socket.disconnect();
    }
  }, [tryAgain]);  // The empty dependency array means this effect will only run once, similar to componentDidMount

  //Huge Commit
  return (
    <div className="mt-12">
      <div className="stat">
        {
          parseInt(latency) / 1000 > 3 || !isConnected 
          ?
          <div>
            <div className="stat-value text-red-500 mb-9">Connection Failed</div>
            <div className="flex gap-2 justify-center place-items-center">
              <button className="bg-yellow-600" onClick={() => setTryAgain(!tryAgain)}>Try Again</button>
              <button className="bg-red-600" onClick={() => setJumbotron(null)}>Exit</button>
            </div>
          </div>
          :
          <>
            <div className="mb-4">
              <h2 className="mb-2 text-lg">Live View: Jumbotron</h2>
              <div className="stat-title">Latency</div>
              <div className="stat-desc">{latency}ms</div>
            </div>
            <div className="grid grid-cols-64 gap-1 border-2 border-red-500 p-4">
              {pixels?.map((pixelArr, rowIndex) => 
                pixelArr.map((pixel, colIndex) => (
                  <Pixel key={`${rowIndex}-${colIndex}`} pixel={pixel} />
                ))
              )}
            </div>
          </>
        }
      </div>
    </div>
  );
}

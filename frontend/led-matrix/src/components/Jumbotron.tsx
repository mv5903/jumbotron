import { useContext, useEffect, useRef, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import Pixel from "./Pixel";
import IPixel from "../interfaces/Pixel";
import io from 'socket.io-client';

export default function Jumbotron({ editable, mini, pixelClicked } : { editable: boolean, mini: boolean, pixelClicked: Function }) {
  const [pixels, setPixels] = useState<IPixel[][]>();
  const [latency, setLatency] = useState<string>("");
  const [pollingRate, setPollingRate] = useState<number>(0); 
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [tryAgain, setTryAgain] = useState<boolean>(false);

  const PIXELSIZE = mini ? ".2vh" : "1.2vh";

  const jumbotronContext = useContext(JumbotronContext);
  if (!jumbotronContext) {
    throw new Error("Jumbotron Context not found");
  }

  const { jumbotron, setJumbotron } = jumbotronContext;

  const tempCounter = useRef<number>(0);

  useEffect(() => {
    let rowSize = Number(jumbotron.rows);
    let colSize = Number(jumbotron.columns);

    let jumbotronArr = [];
    for (let row = 0; row < rowSize; row++) {
      let tempArr = [];
      for (let col = 0; col < colSize; col++) {
        tempArr[col] = { r: 0, g: 0, b: 0, brightness: 255 } as IPixel;
      }
      jumbotronArr.push(tempArr);
    }
    setPixels(jumbotronArr);
  }, [jumbotron]);

  useEffect(() => {
    //if (editable) return;
    // Connect to the server
    const socket = io(`http://${jumbotron.ip}:5000/jumbotron`);

    const intervalId = setInterval(() => {
      setPollingRate(tempCounter.current);
      tempCounter.current = 0;
    }, 1000);

    // Register an event listener for the 'array_update' event
    socket.on('array_update', (response: { data: IPixel[][], timestamp: number }) => {
      setIsConnected(true);
      let latency = (Date.now() - (response.timestamp / 1000000));
      setLatency(latency.toFixed(0));
      setPixels(response.data);
      tempCounter.current++;
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
      clearInterval(intervalId);
    }
  }, [tryAgain]);  // The empty dependency array means this effect will only run once, similar to componentDidMount

  //Huge Commit
  return (
    <div className="mt-12">
      <div className="stat">
        {
           !isConnected 
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
          {
            !editable && 
            <div className="absolute right-4 mb-4 flex-col items-start">
              <div className="stat-desc">Ping: {latency}ms</div>
              <div className="stat-desc">Rate: {pollingRate} updates/sec</div>
            </div>
          }
          {
            mini 
            ?
            <div className="absolute right-4" style={{ height: '5vh', zIndex: 10, top: '12vh' }}>
              <p>Live View</p>
              <div className="grid grid-cols-64 border-2 border-blue-500 p-1" style={{ gap: '.1rem' }}>
                {pixels?.map((pixelArr, rowIndex) => 
                  pixelArr.map((pixel, colIndex) => (
                    <Pixel key={`${rowIndex}-${colIndex}`} mini={true} pixel={pixel} />
                  ))
                )}
              </div>
              <div>
                <div className="stat-desc">Ping: {latency}ms</div>
                <div className="stat-desc">Rate: {pollingRate} updates/sec</div>
              </div>
            </div>
            :
            <div className="grid grid-cols-64 gap-1 border-2 border-red-200 pb-4 px-2">
              {pixels?.map((pixelArr, rowIndex) => 
                pixelArr.map((pixel, colIndex) => (
                  <div className="m-0 p-0 cursor-pointer" style={{ display: 'inline-block', height: PIXELSIZE }} onClick={() => pixelClicked(rowIndex, colIndex)} >
                    <Pixel key={`${rowIndex}-${colIndex}`} mini={false} pixel={pixel} />
                  </div>
                ))
              )}
            </div>
          }
          </>
        }
      </div>
    </div>
  );
}

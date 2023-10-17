import { useState, useRef } from "react";
import "./App.css";
import Jumbotron from "./components/Jumbotron";
import Navbar from "./components/nav/Navbar";
import JumbotronContext from "./providers/JumbotronContext";

export interface Jumbotron {
  rows: Number;
  columns: Number;
  ip: string;
}

enum InfoType {
  ERROR = "text-error",
  SUCCESS = "text-success",
  INFO = "text-info",
}

interface JumbotronConnectionString {
  text: string;
  type: InfoType;
}

function App() {
  const ipFieldRef = useRef<HTMLInputElement>(null);
  const [jumbotron, setJumbotron] = useState<Jumbotron | null>();
  const [connectMessage, setConnectMessage] =
    useState<JumbotronConnectionString | null>();

  function connectTest() {
    setConnectMessage({ text: "Connecting...", type: InfoType.INFO });
    let ip = ipFieldRef.current?.value;
    if (ip) {
      fetch(`http://${ip}:5000/jumbotron`)
        .then((response) => response.json())
        .then((data) => {
          if (data && data.isAlive && data.rows && data.columns) {
            setConnectMessage({ text: `Connected!`, type: InfoType.SUCCESS });
            setTimeout(() => {
              setJumbotron({
                rows: data.rows,
                columns: data.columns,
                ip: ip as string,
              });
            }, 1000);
          }
        })
        .catch((error) => {
          setConnectMessage({
            text: `Error connecting to Jumbotron: ${error.message}`,
            type: InfoType.ERROR,
          });
        });
    }
  }

  function setJumbotronHelper() {
    setConnectMessage(null);
    setJumbotron(null);
  }

  if (!jumbotron) {
    return (
      <div className="flex flex-col place-items-center gap-4">
        <h1>Jumbotron!</h1>
        <h3>Enter the IP address of your Jumbotron to get started:</h3>
        <input
          ref={ipFieldRef}
          onKeyDown={(e) => {
            if (e.key === "Enter") connectTest();
          }}
          type="text"
          placeholder="IP Address"
          className="input input-bordered w-full max-w-xs"
        />
        {connectMessage && (
          <p className={connectMessage.type}>{connectMessage.text}</p>
        )}
        <button onClick={() => connectTest()}>Connect</button>
        <p className="text-gray-300 text-opacity-25">
          You can also press <kbd className="kbd kbd-sm">Enter</kbd> !
        </p>
      </div>
    );
  }
  return (
    <div>
      <JumbotronContext.Provider
        value={{ jumbotron: jumbotron, setJumbotron: setJumbotronHelper }}
      >
        <Navbar />
        <Jumbotron />
      </JumbotronContext.Provider>
    </div>
  );
}

export default App;

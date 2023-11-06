import { useState, useRef } from "react";
import "./App.css";
import Jumbotron from "./interfaces/Jumbotron";
import Navbar from "./components/nav/Navbar";
import JumbotronContext from "./providers/JumbotronContext";
import Editor from "./components/Editor";
import {
  BrowserRouter as Router,
  Route,
  Routes,
} from 'react-router-dom';

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
  const portFieldRef = useRef<HTMLInputElement>(null);
  const [jumbotron, setJumbotron] = useState<Jumbotron | null>();
  const [connectMessage, setConnectMessage] =
    useState<JumbotronConnectionString | null>();
  const [port, setPort] = useState<string>("5000");

  function connectTest() {
    setConnectMessage({ text: "Connecting...", type: InfoType.INFO });
    let ip = ipFieldRef.current?.value;
    if (ip && port) {
      fetch(`http://${ip}:${port}/jumbotron`)
        .then((response) => response.json())
        .then((data) => {
          if (data && data.isAlive && data.rows && data.columns) {
            setConnectMessage({ text: `Connected!`, type: InfoType.SUCCESS });
            setTimeout(() => {
              setJumbotron({
                rows: data.rows,
                columns: data.columns,
                ip: ip as string,
                port
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

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPort(event.target.value);
  };

  if (!jumbotron) {
    return (
      <div className="flex flex-col place-items-center gap-4">
        <h1>Jumbotron!</h1>
        <h3>Enter the details of your Jumbotron server to get started:</h3>
        <div className="flex gap-2 place-items-center">
          <p>http://</p>
          <input
            ref={ipFieldRef}
            onKeyDown={(e) => {
              if (e.key === "Enter") connectTest();
            }}
            type="text"
            placeholder="Hostname"
            className="input input-bordered w-full max-w-xs"
          />
          <p>:</p>
          <input
            ref={portFieldRef}
            onKeyDown={(e) => {
              if (e.key === "Enter") connectTest();
            }}
            value={port}
            onChange={handleInputChange}
            type="text"
            placeholder="Port"
            className="input input-bordered w-full max-w-xs"
          />
          <p>/jumbotron</p>
        </div>
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
    <Router>
      <Routes>
        <Route path="/">
          <div>
            <JumbotronContext.Provider
              value={{ jumbotron: jumbotron, setJumbotron: setJumbotronHelper }}
            >
              <Navbar />
              <Editor />
            </JumbotronContext.Provider>
          </div>
        </Route>
        <Route path="/tablet">
          <p>Tablet view</p>
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

import { useState, useRef } from "react";
import "./App.css";
import Jumbotron from "./interfaces/Jumbotron";
import Navbar from "./components/nav/Navbar";
import JumbotronContext from "./providers/JumbotronContext";
import Editor from "./components/Editor";

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
  const [isDesktopView, setIsDesktopView] = useState<boolean | null>(null);

  function connectTest(view: string) {
    setConnectMessage({ text: "Connecting...", type: InfoType.INFO });
    let ip = ipFieldRef.current?.value;
    if (ip && port) {
      fetch(`http://${ip}:${port}/jumbotron`)
        .then((response) => response.json())
        .then((data) => {
          if (data && data.isAlive && data.rows && data.columns) {
            setConnectMessage({ text: `Connected!`, type: InfoType.SUCCESS });
            saveSessionToLocalStorage(ip as string, port);
            setTimeout(() => {
              setJumbotron({
                rows: data.rows,
                columns: data.columns,
                ip: ip as string,
                port
              });
              setIsDesktopView(view == 'desktop');
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

  function saveSessionToLocalStorage(ip: string, port: string) {
    // Store all sessions in local storage in one json object
    let sessions = localStorage.getItem("sessions");
    let newSession = {
      ip,
      port,
    };
    // Make sure this entry doesn't exist already
    if (sessions) {
      let sessionsJson = JSON.parse(sessions);
      let sessionExists = sessionsJson.find((session: any) => {
        return session.ip === newSession.ip && session.port === newSession.port;
      });
      if (sessionExists) {
        return;
      }
    }
    if (sessions) {
      let sessionsJson = JSON.parse(sessions);
      sessionsJson.push(newSession);
      localStorage.setItem("sessions", JSON.stringify(sessionsJson));
    } else {
      localStorage.setItem("sessions", JSON.stringify([newSession]));
    }
  }

  function setJumbotronHelper() {
    setConnectMessage(null);
    setJumbotron(null);
  }

  function getPreviousConnections() {
    let sessions = localStorage.getItem("sessions");
    if (sessions) {
      let sessionsJson = JSON.parse(sessions);
      return sessionsJson;
    } else {
      return [];
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPort(event.target.value);
  };

  function DesktopView() {
    return (
      <div className="desktop">
        {
          jumbotron 
          ?
          <JumbotronContext.Provider value={{ jumbotron: jumbotron, setJumbotron: setJumbotronHelper }} >
            <Navbar />
            <Editor />
          </JumbotronContext.Provider>
          :
          <div className="flex flex-col place-items-center gap-4">
            <h1>Jumbotron!</h1>
            <h3>Enter the details of your Jumbotron server to get started:</h3>
            <div className="flex gap-2 place-items-center">
              <p>http://</p>
              <input
                ref={ipFieldRef}
                onKeyDown={(e) => {
                  if (e.key === "Enter") connectTest('desktop');
                }}
                type="text"
                placeholder="Hostname"
                className="input input-bordered w-full max-w-xs"
              />
              <p>:</p>  
              <input
                ref={portFieldRef}
                onKeyDown={(e) => {
                  if (e.key === "Enter") connectTest('desktop');
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
            <div className="flex flex-col gap-3">
              <button onClick={() => connectTest('desktop')} >Connect with Desktop View</button>
              <button onClick={() => connectTest('tablet')}>Connect with Tablet View</button>
            </div>
            <p className="text-gray-300 text-opacity-25">
              You can also press <kbd className="kbd kbd-sm">Enter</kbd>!
            </p>
            <div className="divider">OR</div>
            <h2 className="text-2xl mb-2">Recent Connections</h2>
            <div>
              {
                getPreviousConnections().length > 0
                ?
                getPreviousConnections().map((session: any) => {
                  return (
                    <button className="">
                      <div className="flex gap-2 justify-content-center" onClick={() => {
                        ipFieldRef.current!.value = session.ip;
                        portFieldRef.current!.value = session.port;
                        let isTabletMode = confirm('Click "OK" to continue in Tablet Mode')
                        connectTest(isTabletMode ? 'tablet' : 'desktop');
                      }}>
                        <p><span>{session.ip}</span>:<span>{session.port}</span></p>
                      </div>
                    </button>
                  );
                })
                :
                <div>
                  <p className="text-gray-400">No recent connections found.</p>
                </div>
              }
            </div>
          </div>
        }
      </div>
    );
  }

  function TabletView() {
    if (!jumbotron) {
      return (
        <p>No jumbotron detected.</p>
      );
    }
    return (
      <div className="mobile">
        <JumbotronContext.Provider value={{ jumbotron: jumbotron, setJumbotron: setJumbotronHelper }} >
          <button className="bg-red-600" onClick={() => { setIsDesktopView(true); setJumbotronHelper() }}>
            Exit
          </button>
          <p>Mobile View</p>
        </JumbotronContext.Provider>
      </div>
    );
  }

  return (
    <div>
      {
        isDesktopView == true || isDesktopView == null
        ?
        <DesktopView/>
        :
        <TabletView/>
      }
    </div>
  );
}

export default App;

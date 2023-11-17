import { useState, useRef } from "react";
import "./App.css";
import Jumbotron from "./interfaces/Jumbotron";
import Navbar from "./components/nav/Navbar";
import JumbotronContext from "./providers/JumbotronContext";
import Editor from "./components/Editor";
import { FaTrash } from "react-icons/fa";
import { useLocalStorage } from "./helpers/useLocalStorage";
import TabletViewMode from "./components/TabletViewMode";

enum InfoType {
  ERROR = "text-error",
  SUCCESS = "text-success",
  INFO = "text-info",
}

interface JumbotronConnectionString {
  text: string;
  type: InfoType;
}

interface JumbotronDetails {
  ip: string;
  port: string;
}

function App() {
  const ipFieldRef = useRef<HTMLInputElement>(null);
  const portFieldRef = useRef<HTMLInputElement>(null);
  const [jumbotron, setJumbotron] = useState<Jumbotron | null>();
  const [connectMessage, setConnectMessage] =
    useState<JumbotronConnectionString | null>();
  const [port, setPort] = useState<string>("5000");
  const [isDesktopView, setIsDesktopView] = useState<boolean | null>(null);
  const [connections, setConections] = useLocalStorage('connections', [] as JumbotronDetails[]);

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
    let newConnection = { ip, port } as JumbotronDetails;
    // Make sure this connection isn't already saved
    let connectionExists = connections.find((connection) => {
      return connection.ip == ip && connection.port == port;
    });
    if (connectionExists) return;
    setConections([newConnection, ...connections]);
  }

  function setJumbotronHelper() {
    setConnectMessage(null);
    setJumbotron(null);
  }

  function deletePreviousConnection(ip: string, port: string) {
    let newConnections = connections.filter((connection) => {
      return connection.ip != ip || connection.port != port;
    });
    setConections(newConnections);
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
                connections.length > 0
                ?
                connections.map((session: any) => {
                  return (
                    <button className="flex justify-content-center place-items-center gap-3">
                      <div className="flex gap-2 justify-content-center" onClick={() => {
                        ipFieldRef.current!.value = session.ip;
                        portFieldRef.current!.value = session.port;
                        let isTabletMode = confirm('Click "OK" to continue in Tablet Mode')
                        connectTest(isTabletMode ? 'tablet' : 'desktop');
                      }}>
                        <p><span>{session.ip}</span>:<span>{session.port}</span></p>
                      </div>
                      <a className="btn btn-error btn-sm" onClick={() => {
                        let confirmDelete = confirm('Are you sure you want to delete this connection?');
                        if (confirmDelete)
                          deletePreviousConnection(session.ip, session.port);
                      }}><FaTrash/></a>
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
          <button className="absolute top-2 right-4 bg-red-600" onClick={() => { setIsDesktopView(true); setJumbotronHelper() }}>
            Exit
          </button>
          <TabletViewMode />
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

import { useContext } from "react";
//import { Jumbotron } from "../../App";
import JumbotronContext from "../../providers/JumbotronContext";

export default function Navbar() {
  const jumbotronContext = useContext(JumbotronContext);
  if (!jumbotronContext) {
    throw new Error("Jumbotron Context not found");
  }

  const { jumbotron, setJumbotron } = jumbotronContext;
  return (
    <nav className="bg-gray-900 p-4 min-w-full absolute top-0 left-0 right-0 z-50 flex">
      <div className="container mx-auto gap-4 flex justify-between items-center">
        <h2 className="text-green-300 text-xl">{`${jumbotron.rows}R x ${jumbotron.columns}C`}</h2>
        <h2 className="text-blue-400 text-xl">{jumbotron.ip}</h2>
        <button className="bg-red-600" onClick={() => setJumbotron(null)}>
          Exit
        </button>
      </div>
    </nav>
  );
}

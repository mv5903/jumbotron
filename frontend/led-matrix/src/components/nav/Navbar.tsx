import { Jumbotron } from "../../App";

export default function Navbar({ jumbotron, setJumbotron }: { jumbotron: Jumbotron, setJumbotron: Function }) {
    return (
        <nav className="bg-gray-900 p-4 min-w-full absolute top-0 left-0 right-0 z-50 flex">
            <div className="container mx-auto gap-4 flex justify-between items-center">
                <h2 className="text-green-300 text-xl">{`${jumbotron.rows}R x ${jumbotron.columns}C`}</h2>
                <h2 className="text-blue-400 text-xl">{jumbotron.ip}</h2>
                <button className="bg-red-600" onClick={() => setJumbotron(null)}>Exit</button>
            </div>
        </nav>
    );
}
import { useContext, useState } from "react";
import Jumbotron from "./Jumbotron";
import { FaArrowsAltH, FaArrowsAltV, FaBorderAll, FaEdit, FaEye, FaSquareFull } from "react-icons/fa";
import JumbotronContext from "../providers/JumbotronContext";

enum EditMode {
    ROW,
    COLUMN,
    PIXEL,
    ALL
}

export default function Editor() {
    const [editable, setEditable] = useState<boolean>(false);

    const jumbotronContext = useContext(JumbotronContext);
    if (!jumbotronContext) {
        throw new Error("Jumbotron Context not found");
    }

    const { jumbotron } = jumbotronContext;

    //Edits
    const [color, setColor] = useState<string>("#000000");
    const [brightness, setBrightness] = useState<number>(100);
    const [editMode, setEditMode] = useState<EditMode>(EditMode.PIXEL);

    const handleBrightnessChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setBrightness(Number(event.target.value));
    };

    const handleColorChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setColor(event.target.value);
    };

    function pixelClicked(row: number, column: number) {
        const hexToRgb = (hex: string) => ({ r: parseInt(hex.slice(1, 3), 16), g: parseInt(hex.slice(3, 5), 16), b: parseInt(hex.slice(5, 7), 16) });
        const {r, g, b} = hexToRgb(color);
        switch (editMode) {
            case EditMode.PIXEL:
                fetch(`http://${jumbotron.ip}:5000/jumbotron/pixel/${row}/${column}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.ROW:
                fetch(`http://${jumbotron.ip}:5000/jumbotron/row/${row}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.COLUMN:
                fetch(`http://${jumbotron.ip}:5000/jumbotron/column/${column}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.ALL:
                fetch(`http://${jumbotron.ip}:5000/jumbotron/all/${r}/${g}/${b}/${brightness}`);
                break;
        }
    }

    function resetBoard() {
        let response = confirm("Are you sure you want to reset the board?");
        if (response) {
            fetch(`http://${jumbotron.ip}:5000/jumbotron/reset`)
        }
    }
    
    return (
        <div>
            <div className="join absolute left-14 mt-6">
                <button className={`btn join-item ${!editable && 'btn-active'}`} onClick={() => setEditable(false)}><FaEye /> View</button>
                <button className={`btn join-item ${editable && 'btn-active'}`} onClick={() => setEditable(true)}><FaEdit /> Edit</button>
            </div>
            {
                editable
                ?
                <>
                    <Jumbotron editable={true} mini={false} pixelClicked={pixelClicked} />
                    <Jumbotron editable={false} mini={true} pixelClicked={pixelClicked} />
                </>
                :
                <Jumbotron editable={false} mini={false} pixelClicked={pixelClicked} />
            }
            {
                editable &&
                <div className="absolute left-4 top-0 p-2 rounded-md bg-base-100 shadow-xl" style={{ marginTop: '20vh', width: '16vw' }}>
                    <h2 className="text-2xl">Edit</h2>
                    <div className="flex justify-between mt-2">
                        <h2>Color</h2>
                        <input type="color" value={color} onChange={handleColorChange} />
                    </div>
                    <div className="flex justify-between mt-2">
                        <h2>Brightness</h2>
                        <input type="range" min={0} max="255" value={brightness} onChange={handleBrightnessChange} className="range w-1/2" />
                    </div>  
                    <div className="join mt-4">
                        <button className={`btn tooltip join-item ${editMode == EditMode.PIXEL && 'btn-active'}`} data-tip="Pixel" onClick={() => setEditMode(EditMode.PIXEL)} style={{ borderRadius: 'revert' }}><FaSquareFull /></button>
                        <button className={`btn tooltip join-item ${editMode == EditMode.ROW && 'btn-active'}`} data-tip="Row" onClick={() => setEditMode(EditMode.ROW)} style={{ borderRadius: 'revert' }}><FaArrowsAltH /></button>
                        <button className={`btn tooltip join-item ${editMode == EditMode.COLUMN && 'btn-active'}`} data-tip="Column" onClick={() => setEditMode(EditMode.COLUMN)} style={{ borderRadius: 'revert' }}><FaArrowsAltV /></button>
                        <button className={`btn tooltip join-item ${editMode == EditMode.ALL && 'btn-active'}`} data-tip="All" onClick={() => setEditMode(EditMode.ALL)} style={{ borderRadius: 'revert' }}><FaBorderAll /></button>
                    </div>
                    <div>
                        <button className="btn btn-outline btn-warning mt-4" onClick={() => resetBoard()}>Reset</button>
                    </div>
                </div>
            }
        </div>
    );
}
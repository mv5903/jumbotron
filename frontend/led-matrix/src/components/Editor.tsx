import { useContext, useEffect, useRef, useState } from "react";
import Jumbotron from "./Jumbotron";
import { FaArrowsAltH, FaArrowsAltV, FaBorderAll, FaEdit, FaEraser, FaEye, FaPencilAlt } from "react-icons/fa";
import JumbotronContext from "../providers/JumbotronContext";
import Saver from "./Saver";

enum EditMode {
    ROW,
    COLUMN,
    PIXEL,
    ALL,
    ERASER
}

export default function Editor() {
    const [editable, setEditable] = useState<boolean>(false);

    const jumbotronContext = useContext(JumbotronContext);
    if (!jumbotronContext) {
        throw new Error("Jumbotron Context not found");
    }

    const { jumbotron } = jumbotronContext;

    //Edits
    const [color, setColor] = useState<string>("#FFFFFF");
    const [brightness, setBrightness] = useState<number>(0);
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
                fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/pixel/${row}/${column}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.ROW:
                fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/row/${row}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.COLUMN:
                fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/column/${column}/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.ALL:
                fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/all/${r}/${g}/${b}/${brightness}`);
                break;
            case EditMode.ERASER:
                fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/pixel/${row}/${column}/0/0/0/255`);
                break;
        }
    }

    function resetBoard() {
        let response = confirm("Are you sure you want to reset the board?");
        if (response) {
            fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/reset`)
        }
    }

    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const handleImageUpload = async () => {
        const file = fileInputRef.current?.files?.[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        // Check if file is video or image
        const isVideo = file.type.startsWith("video");
        if (isVideo) {
            try {
                await fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/playvideo/${brightness}`, {
                    method: "POST",
                    body: formData
                })
            } catch (error) {
                console.error("Error uploading video:", error);
            }
        } else {
            try {
                await fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/upload/${brightness}`, {
                    method: "POST",
                    body: formData
                });
            } catch (error) {
                console.error("Error uploading image:", error);
            }
        }
    };
    
    return (
        <div>
            <div className="join absolute left-14 top-0" style={{ marginTop: '12vh' }}>
                <button className={`btn join-item ${!editable && 'btn-primary'}`} onClick={() => setEditable(false)}><FaEye /> View</button>
                <button className={`btn join-item ${editable && 'btn-primary'}`} onClick={() => setEditable(true)}><FaEdit /> Edit</button>
            </div>
            {
                editable
                ?
                <>
                    <div className="ms-8">
                        <Jumbotron editable={true} mini={false} pixelClicked={pixelClicked} />
                    </div>
                    <Jumbotron editable={false} mini={true} pixelClicked={pixelClicked} />
                    <Saver isTablet={false} />
                </>
                :
                <Jumbotron editable={false} mini={false} pixelClicked={pixelClicked} />
            }
            {
                editable &&
                <div className="absolute left-4 top-0 p-2 py-4 rounded-md bg-base-300 " style={{ marginTop: '20vh', width: '18vw' }}>
                    <div>
                        <h2>Direct Edit</h2>
                        <div className="flex justify-between mt-2">
                            <h2>Color</h2>
                            <input type="color" value={color} onChange={handleColorChange} />
                        </div>
                        <div className="flex justify-between mt-2">
                            <h2>Brightness</h2>
                            <div className="flex">
                                <p>0</p>
                                <div className="tooltip" data-tip={brightness}>
                                    <input type="range" min={0} max="40" value={brightness} onChange={handleBrightnessChange} className="range w-20 mx-2" />
                                </div>
                                <p>40</p>
                            </div>
                        </div>  
                        <div className="join join-horizontal mt-4 text-sm shadow-md">
                            <button className={`btn tooltip join-item ${editMode == EditMode.PIXEL && 'btn-primary'}`} data-tip="Pencil" onClick={() => setEditMode(EditMode.PIXEL)} style={{ borderRadius: 'revert' }}><FaPencilAlt /></button>
                            <button className={`btn tooltip join-item ${editMode == EditMode.ROW && 'btn-primary'}`} data-tip="Row" onClick={() => setEditMode(EditMode.ROW)} style={{ borderRadius: 'revert' }}><FaArrowsAltH /></button>
                            <button className={`btn tooltip join-item ${editMode == EditMode.COLUMN && 'btn-primary'}`} data-tip="Column" onClick={() => setEditMode(EditMode.COLUMN)} style={{ borderRadius: 'revert' }}><FaArrowsAltV /></button>
                            <button className={`btn tooltip join-item ${editMode == EditMode.ALL && 'btn-primary'}`} data-tip="All" onClick={() => setEditMode(EditMode.ALL)} style={{ borderRadius: 'revert' }}><FaBorderAll /></button>
                            <button className={`btn tooltip join-item ${editMode == EditMode.ERASER && 'btn-primary'}`} data-tip="Erase" onClick={() => setEditMode(EditMode.ERASER)} style={{ borderRadius: 'revert' }}><FaEraser /></button>
                        </div>
                    </div>
                    <div className="divider">OR</div>
                    <div className="">
                        <div className="mt-4">
                            <h2>Upload Image/Video</h2>
                            <div className="flex flex-col gap-2 justify-center place-items-center">
                                <input 
                                    type="file" 
                                    ref={fileInputRef}
                                    accept="image/*, video/*"
                                    className="file-input file-input-bordered file-input-xs w-full max-w-xs text-sm my-3"
                                />
                                <button className="btn btn-outline btn-info" onClick={() => handleImageUpload()}>Send</button>
                            </div>
                        </div>
                        <div className="divider">OR</div>
                    </div>
                    <h2 className="text-error">Destructive!</h2>
                    <div>
                        <button className="btn btn-outline btn-error mt-2" onClick={() => resetBoard()}>Reset</button>
                    </div>
                </div>
            }
        </div>
    );
}
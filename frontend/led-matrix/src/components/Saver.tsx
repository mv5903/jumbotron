import { useContext, useEffect, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import { FaRedo, FaTrash } from "react-icons/fa";

export default function Saver() {

    const [savedMatricies, setSavedMatricies] = useState<string[]>([]);

    const jumbotronContext = useContext(JumbotronContext);
    if (!jumbotronContext) {
        throw new Error("Jumbotron Context not found");
    }

    const { jumbotron } = jumbotronContext;

    function saveMatrix() {
        fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/save_current_matrix`, {
            method: 'POST'
        }).then(response => response.json()).then(data => {
            if(data.success) {
                alert('Saved successfully!');
                // Optionally refresh the list of saved matrices here
            } else {
                alert('Failed to save.');
            }
        });
    }

    function getSavedMatricies() {
        fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/get_saved_matrices`, {
                method: 'GET'
            }).then(response => response.json()).then(data => {
                if (data) {
                    setSavedMatricies(data);
                }
            });
    }

    return (
        <div className="absolute right-4 top-0 bg-base-300 p-3" style={{ marginTop: '40vh', width: '16vw' }}>
            <button className="bg-green-600" onClick={() => saveMatrix()}>Save Current Matrix</button>
            <div className="divider">OR</div>
            <div>
                <div className="flex place-items-center gap-2 mb-2">
                    <h2 className="text-lg">Saved Matricies:</h2>
                    <button className="bg-primary" onClick={() => getSavedMatricies()}><FaRedo/></button>
                </div>
                <div className="flex flex-col place-items-center">
                    {
                        savedMatricies && savedMatricies.map((matrix, index) => {
                            return(
                                <div className="flex place-items-center gap-2" key={index}>
                                    <FaTrash/>
                                    <p>{matrix}</p>
                                </div>
                            );
                        })
                    }
                </div>
            </div>
        </div>
    );
}
import { useContext, useEffect, useState } from "react";
import JumbotronContext from "../providers/JumbotronContext";
import { FaRedo, FaTrash } from "react-icons/fa";

const AFTER_ACTION_TIMEOUT = 50;

export default function Saver() {

    const [savedMatricies, setSavedMatricies] = useState<string[]>([]);
    const [hoveredImageURL, setHoveredImageURL] = useState<string | null>(null);


    const jumbotronContext = useContext(JumbotronContext);
    if (!jumbotronContext) {
        throw new Error("Jumbotron Context not found");
    }

    const { jumbotron } = jumbotronContext;

    function saveMatrix() {
        let name = prompt('Enter a name for this matrix:');
        if(!name) {
            return;
        }
        fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/save_current_matrix/${name}`, {
            method: 'POST'
        }).then(response => response.json()).then(data => {
            if(data.success) {
                alert('Saved successfully!');
                setTimeout(getSavedMatricies, AFTER_ACTION_TIMEOUT);
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

    async function getImagePreview(name: string): Promise<string | null> {
        try {
            const response = await fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/get_saved_matrix_image/${name}`, {
                method: 'GET'
            });
            const data = await response.blob();
            const url = window.URL.createObjectURL(data);
            return url;
        } catch (error) {
            console.error("Error fetching image preview:", error);
            return null;
        }
    }

    function deleteSavedMatrix(name: string) {
        fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/delete_saved_matrix/${name}`, {
            method: 'DELETE'
        }).then(response => response.json()).then(data => {
            if(data.success) {
                alert('Deleted successfully!');
                setTimeout(getSavedMatricies, AFTER_ACTION_TIMEOUT);
            } else {
                alert('Failed to delete.');
            }
        });
    }

    function activateMatrix(name: string) {
        fetch(`http://${jumbotron.ip}:${jumbotron.port}/jumbotron/activate_saved_matrix/${name}`, {
            method: 'POST'
        }).then(response => response.json()).then(data => {
            if(data.success) {
                alert('Activated successfully!');
            } else {
                alert('Failed to activate.');
            }
        });
    }


    useEffect(() => {
        if (jumbotron) {
            getSavedMatricies();
        }
    }, [jumbotron])

    return (
        <div className="absolute right-4 top-0 bg-base-300 p-3" style={{ marginTop: '40vh', width: '16vw' }}>
            <button className="bg-green-600" onClick={() => saveMatrix()}>Save Current Matrix</button>
            <div className="divider">OR</div>
            <div>
                <div className="flex justify-center place-items-center gap-4 mb-2">
                    <h2 className="text-lg">Saved Matricies:</h2>
                    <button className="bg-primary" onClick={() => getSavedMatricies()}><FaRedo/></button>
                </div>
                <div className="flex flex-col place-items-center gap-2">
                    {
                        savedMatricies && savedMatricies.map((matrix, index) => {
                            return(
                                <div className="flex place-items-center gap-2 border-2 border-b-gray-600 p-2" key={index}>
                                    <p 
                                        onMouseEnter={async () => {
                                            const imageUrl = await getImagePreview(matrix);
                                            setHoveredImageURL(imageUrl);
                                        }}
                                        onMouseLeave={() => setHoveredImageURL(null)}
                                        onClick={() => activateMatrix(matrix)}
                                        className="cursor-help"
                                    >
                                        {matrix.split('.')[0]}
                                    </p>
                                    <div className="cursor-pointer" onClick={() => deleteSavedMatrix(matrix)}>
                                        <FaTrash/>
                                    </div>
                                    {hoveredImageURL && (
                                        <div className="absolute top-0 left-0 z-50">
                                            <img src={hoveredImageURL} alt={`Preview of ${matrix}`} width="100" />
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    }
                </div>
            </div>
        </div>
    );
}
import { createContext } from "react";
import Jumbotron from "../interfaces/Jumbotron";

interface JumbotronContextType {
  jumbotron: Jumbotron;
  setJumbotron: (jumbotron: Jumbotron | null) => void;
}

const JumbotronContext = createContext<JumbotronContextType | undefined>(
  undefined
);

export default JumbotronContext;

import { createContext } from "react";

interface Jumbotron {
  rows: Number;
  columns: Number;
  ip: string;
}

interface JumbotronContextType {
  jumbotron: Jumbotron;
  setJumbotron: (jumbotron: Jumbotron | null) => void;
}

const JumbotronContext = createContext<JumbotronContextType | undefined>(
  undefined
);

export default JumbotronContext;

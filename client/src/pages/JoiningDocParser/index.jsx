import { Outlet } from "react-router-dom";

export default function JoiningDocParser() {
  return (
    <div>
      <Outlet /> {/* Renders the child routes (JoiningDocParserHome or subpages) */}
    </div>
  );
}
import { useState } from "react";
import Dashboard from "./Dashboard";
import UploadStatement from "./UploadStatement"; 

import { GoHome } from "react-icons/go";
import { FaRegFilePdf } from "react-icons/fa";
import { LuNotepadText } from "react-icons/lu";
import { IoMdGitCompare } from "react-icons/io";
import { GrConfigure } from "react-icons/gr";
import { IoIosArrowBack } from "react-icons/io";
import { IoIosArrowForward } from "react-icons/io";

const Menus = [
  { title: "Inicio", src: <GoHome /> },
  { title: "Cargar estado de cuenta", src: <FaRegFilePdf /> },
  { title: "Resultado", src: <LuNotepadText />, gap: true },
  { title: "Comparar con bauchers ", src: <IoMdGitCompare /> },
  { title: "Configuraciones", src: <GrConfigure /> },
];

export default function Sidebar() {
  const [open, setOpen] = useState(true);

  return (
    <div className="flex">
      <div
        className={` ${
          open ? "w-60" : "w-20"
        } bg-dark-purple h-screen p-5  pt-8 relative duration-300`}
        style={{ backgroundColor: "#19304C" }}
      >
        <div
          className={`text-2xl absolute cursor-pointer -right-3 top-9 w-7
            flex items-center justify-center text-black rounded-full`}
          onClick={() => setOpen(!open)}
        >
          {open ? <IoIosArrowBack /> : <IoIosArrowForward />}
        </div>
        <div className="flex gap-x-4 items-center">
          <img
            src="./src/assets/react.svg"
            className={`cursor-pointer duration-500 ${
              open && "rotate-[360deg]"
            }`}
          />
          <h1
            className={`text-white origin-left font-medium text-xl duration-200 ${
              !open && "scale-0"
            }`}
          >
            BaucherMatch
          </h1>
        </div>
        <ul className="pt-6">
          {Menus.map((Menu, index) => (
            <li
              key={index}
              className={`flex rounded-md p-2 cursor-pointer hover:bg-light-white text-white text-sm items-center gap-x-4 
              ${Menu.gap ? "mt-4" : "mt-2"} ${index === 0 && "bg-[#34435d]"} `}
            >
              <div className="text-2xl">{Menu.src}</div>
              <span className={`${!open && "hidden"} origin-left duration-200`}>
              {Menu.title}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="h-screen flex-1 p-7">
        <h1 className="text-2xl font-bold">Inicio</h1>
        <Dashboard />
        <UploadStatement />
      </div>
    </div>
  );
}

import React from "react";

interface CardProps {
  title?: string;
  children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, children }) => {
  return (
    <div className="bg-gray-100 shadow-lg rounded-2xl p-4">
      {title && <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">{title}</h2>}
      <div className="text-gray-800 dark:text-black text-sm">{children}</div>
    </div>
  );
};

export default Card;

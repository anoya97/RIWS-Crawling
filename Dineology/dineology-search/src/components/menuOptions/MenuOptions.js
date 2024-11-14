import React from 'react';
import './MenuOptions.css';

const MenuOptions = ({ options, description }) => (
  <div className="menuOptionsContainer">
    <h2>Opciones de menú</h2>
    {description && <p className="shortMenuDescription">{description}</p>}
    <div className="menuCardsContainer">
      {options.map((menu, index) => (
        <div className="menuCard" key={index}>
          <h3 className="menuName">{menu.name}</h3>
          <p className="menuPrice">{menu.price ? menu.price : "Precio a consultar"}</p>
          {menu.description && <p className="menuDescription">{menu.description}</p>}
        </div>
      ))}
    </div>
  </div>
);

export default MenuOptions;

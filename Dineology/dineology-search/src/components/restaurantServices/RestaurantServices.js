import React from 'react';
import './RestaurantServices.css';

const RestaurantServices = ({ services }) => (
  <div className="restaurantServices">
    <h2>Servicios del restaurante</h2>
    <div className="servicesList">
      {services.map((service, index) => (
        <div className="serviceCard" key={index}>
          <p>{service}</p>
        </div>
      ))}
    </div>
  </div>
);

export default RestaurantServices;

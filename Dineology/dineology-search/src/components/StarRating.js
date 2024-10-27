import React from 'react';

const StarRating = ({ rating }) => {
  const stars = Array(3).fill(0); // Cambiar a 3 estrellas como máximo

  return (
    <div className="starRating">
      {stars.map((_, index) => (
        <span key={index} className={index < rating ? 'star filled' : 'star'}>
          ★
        </span>
      ))}
    </div>
  );
};

export default StarRating;

import React from 'react';
import estrellaIcon from '../../assets/estrellaIcon.png';
import solIcon from '../../assets/solIcon.png';
import './RestaurantInfoCard.css';

const renderIcons = (num, iconSrc, altText) => {
  if (num === 0) return null;
  return (
    <>
      {Array.from({ length: num }).map((_, index) => (
        <img
          key={index}
          src={iconSrc}
          alt={altText}
          style={{ width: 15, height: 15, marginRight: 4 }}
        />
      ))}
    </>
  );
};

const RestaurantInfoCard = ({ restaurant }) => (
  <div className="restaurantCard">
    <div className="imageWrapper">
      <img
        src={restaurant.restaurant_photo_url || "https://play-lh.googleusercontent.com/D-7VBAD71gJsTno_3uZYCEOt4TF7uf_FAesVtXBNkyjRbdJOh7y806mGu63Z3U1HYQ"}
        alt={restaurant.name || "Foto del restaurante"}
        className="restaurantImage"
      />
    </div>
    <div className="restaurantInfo">
      {restaurant.name && <h1 className="detailsTitle">{restaurant.name}</h1>}
      {restaurant.description && <p className="detailsDescription">{restaurant.description}</p>}
      <div className="detailsData">
        {restaurant.price && <p className="detailsPrice">Precio: {restaurant.price}</p>}
        {Array.isArray(restaurant.meal_type) && (
          <p className="detailsMealType">Tipo de comida: {restaurant.meal_type.join(', ')}</p>
        )}
        {restaurant.star_number !== undefined && (
          <p className="detailsRating">Estrellas: {renderIcons(restaurant.star_number, estrellaIcon, 'estrella')}</p>
        )}
        {restaurant.soles_number !== undefined && (
          <p className="detailsRating">Soles: {renderIcons(restaurant.soles_number, solIcon, 'sol')}</p>
        )}
        {Array.isArray(restaurant.owners_name) && (
          <p className="detailsOwners">Propietarios: {restaurant.owners_name.join(', ')}</p>
        )}
        {restaurant.instagram_user && (
          <p className="detailsInstagram">
            Usuario de Instagram: <a href={`https://www.instagram.com/${restaurant.instagram_user}`} target="_blank" rel="noopener noreferrer" className="instagramLink">@{restaurant.instagram_user}</a>
          </p>
        )}
        {restaurant.contact_number && <p className="detailsContact">Contacto: {restaurant.contact_number}</p>}
        {restaurant.direction && <p className="detailsDirection">Dirección: {restaurant.direction}</p>}
        {restaurant.web_url && (
          <a href={restaurant.web_url} className="detailsWeb" target="_blank" rel="noopener noreferrer">
            Visitar Web
          </a>
        )}
      </div>
    </div>
  </div>
);

export default RestaurantInfoCard;

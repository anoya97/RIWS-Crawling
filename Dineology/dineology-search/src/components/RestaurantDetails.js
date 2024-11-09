// RestaurantDetails.js
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './RestaurantDetails.css';
import estrellaIcon from '../estrellaIcon.png';
import solIcon from '../solIcon.png';

function RestaurantDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const restaurant = location.state?.restaurant;

  // Recuperar query y results de location.state
  const previousSearchQuery = location.state?.query || ''; // Almacena el query
  const previousResults = location.state?.previousResults || []; // Almacena los resultados

  const [coordinates, setCoordinates] = useState(null);
  const [loading, setLoading] = useState(true); // Estado de carga para el mapa

  useEffect(() => {
    const fetchCoordinates = async (address) => {
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${address}`);
        const data = await response.json();
        if (data.length > 0) {
          setCoordinates({
            lat: parseFloat(data[0].lat),
            lon: parseFloat(data[0].lon)
          });
        }
      } catch (error) {
        console.error("Error fetching coordinates:", error);
      } finally {
        setLoading(false); // Cambiar el estado de carga al finalizar
      }
    };

    if (restaurant && restaurant.direction) {
      fetchCoordinates(restaurant.direction);
    }
  }, [restaurant]);

  if (!restaurant) {
    return <p>Datos del restaurante no disponibles.</p>;
  }

  const handleBackClick = () => {
    navigate('/', { state: { query: previousSearchQuery, previousResults } }); // Pasar el query y los resultados al navegar de vuelta
  };

  const renderIcons = (num, iconSrc, altText) => {
    if (num === 0) return null; // No mostrar nada si son 0 estrellas
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

  return (
    <div className="detailsContainer">
      <button className="backButton" onClick={handleBackClick}>
        &#8592; Volver
      </button>
      <div className="restaurantCard">
        <div className="imageWrapper">
          <img
              src={restaurant.restaurant_photo_url || "default-image.jpg"}
              alt={restaurant.name || "Foto del restaurante"}
              className="restaurantImage"
          />
        </div>
        <div className="restaurantInfo">
          {restaurant.name && <h1 className="detailsTitle">{restaurant.name}</h1>}
          {restaurant.description && <p className="detailsDescription">{restaurant.description}</p>}
          <div className="detailsData">
            {restaurant.price && <p className="detailsPrice">Precio: {restaurant.price}</p>}
            {Array.isArray(restaurant.meal_type) && restaurant.meal_type.length > 0 && (
                <p className="detailsMealType">
                  Tipo de comida: {restaurant.meal_type.join(', ')}
                </p>
            )}
            {restaurant.star_number !== undefined && (
              <p className="detailsRating">
                Estrellas: {renderIcons(restaurant.star_number, estrellaIcon, 'estrella')}
              </p>
            )}
            {restaurant.soles_number !== undefined && (
              <p className="detailsRating">
                Soles: {renderIcons(restaurant.soles_number, solIcon, 'sol')}
              </p>
            )}
            {restaurant.instagram_user && (
              <p className="detailsInstagram">
                Usuario de Instagram:{' '}
                <a
                  href={`https://www.instagram.com/${restaurant.instagram_user}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="instagramLink"
                >
                  @{restaurant.instagram_user}
                </a>
              </p>
            )}
            {restaurant.contact_number && (
                <p className="detailsContact">Contacto: {restaurant.contact_number}</p>
            )}
            {restaurant.direction && <p className="detailsDirection">Dirección: {restaurant.direction}</p>}
            {restaurant.web_url && (
                <a
                    href={restaurant.web_url}
                    className="detailsWeb"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                  Visitar Web
                </a>
            )}
          </div>
        </div>
      </div>

      <div className="workingScheduleContainer">
        <div className="workingSchedule">
          <h2>Horario de trabajo</h2>
          <div className="workingScheduleAndMapContainer">
            <table className="workingScheduleTable">
              <thead>
              <tr>
                <th>Día</th>
                <th>Horario</th>
              </tr>
              </thead>
              <tbody>
              {restaurant.working_schedule && Object.keys(restaurant.working_schedule).length > 0 ? (
                  // Convertir el horario en un objeto, si existe
                  Object.entries(restaurant.working_schedule).map(([day, hours]) => (
                      <tr key={day}>
                        <td>{day}</td>
                        <td>
                          {hours.length > 0 ? (
                              hours.map((hour, index) => (
                                  <div
                                      style={{
                                        marginBottom: index !== hours.length - 1 ? '8px' : '0' // Solo aplica margen si no es la última hora
                                      }}
                                      key={index}
                                  >
                                    {hour}
                                  </div> // Usar <div> para separar las horas por línea
                              ))
                          ) : (
                              "No disponible"
                          )}
                        </td>
                      </tr>
                  ))
              ) : (
                  // Si no hay horario, mostrar todos los días con "-"
                  ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].map((day) => (
                      <tr key={day}>
                        <td>{day}</td>
                        <td>-</td>
                      </tr>
                  ))
              )}
              </tbody>
            </table>
            <div className="mapContainer">
              {loading ? ( // Mostrar carga mientras se obtienen las coordenadas
                  <p>Cargando mapa...</p>
              ) : coordinates ? (
                  <iframe
                      src={`https://www.openstreetmap.org/export/embed.html?bbox=${coordinates.lon - 0.01},${coordinates.lat - 0.01},${coordinates.lon + 0.01},${coordinates.lat + 0.01}&layer=mapnik&marker=${coordinates.lat},${coordinates.lon}`}
                  width="100%"
                  height="600px"
                  style={{ border: 0 }}
                  allowFullScreen=""
                  loading="lazy"
                  title="Mapa"
                />
              ) : (
                <p>Coordenadas no disponibles.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="restaurantServices">
        <h2>Servicios</h2>
        <ul>
          {restaurant.restaurant_services && restaurant.restaurant_services.length > 0 ? (
            restaurant.restaurant_services.map((service, index) => (
              <li key={index}>{service}</li>
            ))
          ) : (
            <p>No hay servicios disponibles</p>
          )}
        </ul>
      </div>
    </div>
  );
}

export default RestaurantDetails;

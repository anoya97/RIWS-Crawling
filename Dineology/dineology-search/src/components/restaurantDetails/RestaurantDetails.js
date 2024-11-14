import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './RestaurantDetails.css';
import RestaurantInfoCard from '../restaurantInfoCard/RestaurantInfoCard';
import WorkingScheduleAndMap from '../workingScheduleAndMap/WorkingScheduleAndMap';
import useFetchCoordinates from './useFetchCoordinates';
import { renderMenuOptions, renderRestaurantServices } from './renderers';

function RestaurantDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const restaurant = location.state?.restaurant;
  const previousSearchQuery = location.state?.query || '';
  const previousResults = location.state?.previousResults || [];
  const { coordinates, loading, fetchCoordinates } = useFetchCoordinates();

  useEffect(() => {
    if (restaurant?.direction) {
      fetchCoordinates(restaurant.direction);
    }
  }, [restaurant, fetchCoordinates]); // fetchCoordinates ya no cambia de referencia

  const handleBackClick = () => {
    navigate('/', { state: { query: previousSearchQuery, previousResults } });
  };

  if (!restaurant) {
    return <p>Datos del restaurante no disponibles.</p>;
  }

  return (
    <div className="detailsContainer">
      <button className="backButton" onClick={handleBackClick}>
        &#8592; Volver
      </button>
      <RestaurantInfoCard restaurant={restaurant} />
      {renderMenuOptions(restaurant)}
      {renderRestaurantServices(restaurant)}
      <WorkingScheduleAndMap
        schedule={restaurant.working_schedule}
        coordinates={coordinates}
        loading={loading}
      />
    </div>
  );
}

export default RestaurantDetails;

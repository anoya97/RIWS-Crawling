import React from 'react';
import MenuOptions from '../menuOptions/MenuOptions';
import RestaurantServices from '../restaurantServices/RestaurantServices';

export const renderMenuOptions = (restaurant) => {
  return (
    restaurant.menu_options && restaurant.menu_options.length > 0 && (
      <MenuOptions
        options={restaurant.menu_options}
        description={restaurant.short_menu_description}
      />
    )
  );
};

export const renderRestaurantServices = (restaurant) => {
  return (
    restaurant.restaurant_services && restaurant.restaurant_services.length > 0 && (
      <RestaurantServices services={restaurant.restaurant_services} />
    )
  );
};

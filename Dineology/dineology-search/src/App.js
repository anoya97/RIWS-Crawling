import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import logo from './Logo.png';
import RestaurantDetails from './components/RestaurantDetails';
import solIcon from './solIcon.png';
import estrellaIcon from './estrellaIcon.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [notFound, setNotFound] = useState(false);
  const [filters, setFilters] = useState({
    starsOrSoles: 'both',
    priceRange: '',
    mealType: '',
    starNumber: '',
  });
  const [filterOptions, setFilterOptions] = useState({
    priceRanges: [],
  });
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();
  const location = useLocation(); // Para acceder a la ubicación actual

  // Manejo de búsqueda
  const handleSearch = async (e) => {
    e.preventDefault();
    await fetchResults(query); // Llama a la función para buscar resultados
  };

  // Función para obtener resultados de búsqueda
 const fetchResults = useCallback(async (searchQuery) => {
    if (!searchQuery) return;
    try {
      const response = await axios.post('http://localhost:9200/restaurants/_search', {
        size: 1000,
        query: {
          bool: {
            should: [
              { wildcard: { "name": `*${searchQuery.toLowerCase()}*` } },
              { wildcard: { "meal_type": `*${searchQuery.toLowerCase()}*` } }
            ]
          }
        }
      });

      // Función para convertir el precio medio en símbolos €
      const getPriceSymbols = (averagePrice) => {
        if (averagePrice <= 50) return '€';
        if (averagePrice <= 100) return '€€';
        if (averagePrice <= 150) return '€€€';
        return '€€€€';
      };

      // Procesar los hits para añadir precios faltantes
      const processedHits = response.data.hits.hits.map(hit => {
        const restaurant = hit._source;

        // Si no tiene price pero tiene menu_options con precios
        if (!restaurant.price && restaurant.menu_options?.length > 0) {
          // Extraer los precios numéricos del menú
          const menuPrices = restaurant.menu_options
            .map(menu => {
              if (!menu.price) return 0;
              // Extraer solo los números del string de precio
              const priceStr = menu.price.replace(/[^0-9.,]/g, '');
              return parseFloat(priceStr.replace(',', '.')) || 0;
            })
            .filter(price => price > 0);

          // Si hay precios válidos, calcular el promedio y convertirlo a símbolos
          if (menuPrices.length > 0) {
            const averagePrice = menuPrices.reduce((a, b) => a + b, 0) / menuPrices.length;
            restaurant.price = getPriceSymbols(averagePrice);
          }
        }

        return {
          ...hit,
          _source: restaurant
        };
      });

      setResults(processedHits);
      setFilteredResults(processedHits);
      setNotFound(processedHits.length === 0);

      // Procesar las opciones de filtro con los nuevos precios
      const allMealTypes = processedHits.reduce((types, hit) => {
        const mealTypes = processMealTypes(hit._source.meal_type);
        return [...types, ...mealTypes];
      }, []);

      const uniqueMealTypes = [...new Set(allMealTypes)].sort();

      setFilterOptions({
        priceRanges: [...new Set(processedHits.map((hit) => hit._source.price).filter(price => price))]
    .sort((a, b) => a.length - b.length),
        mealTypes: uniqueMealTypes,
      });

    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }, []);



  // useEffect para manejar el estado al regresar a la página principal
  useEffect(() => {
    if (location.state && location.state.query) {
      setQuery(location.state.query); // Restablece el query
      fetchResults(location.state.query); // Ejecuta la búsqueda con el query
    }
  }, [location.state, fetchResults]); // Ejecutar cuando el estado de la ubicación cambie

  // Manejo del clic en el resultado
  const handleResultClick = (restaurant) => {
    const restaurantName = restaurant._source.name.replace(/\s+/g, '-').toLowerCase();
    navigate(`/${restaurantName}`, { state: { query, restaurant: restaurant._source } }); // Pasar el query y el restaurante
  };


  const processMealTypes = (mealTypeValue) => {
  if (typeof mealTypeValue === 'string') {
    return mealTypeValue.split(' ').filter(type => type.trim());
  }
  if (Array.isArray(mealTypeValue)) {
    return mealTypeValue;
  }
  return [];
};

  // Borrar filtros
  const clearFilters = () => {
  setFilters({
    starsOrSoles: 'both',
    priceRange: '',
    mealType: '',
    starNumber: '',
  });
  setFilteredResults(results); // Restaura los resultados originales
};

  // Aplicar filtros a los resultados
  const applyFilters = () => {
    let filtered = results;

      if (filters.starsOrSoles === 'estrellas') {
         filtered = filtered.filter((result) => (result._source.star_number > 0) );
      } else if (filters.starsOrSoles === 'soles') {
        filtered = filtered.filter((result) => (result._source.soles_number > 0));
      }
    if (filters.priceRange) {
      filtered = filtered.filter((result) => result._source.price === filters.priceRange);
    }

    if (filters.mealType) {
      filtered = filtered.filter((result) => {
        const restaurantMealTypes = processMealTypes(result._source.meal_type);
        return restaurantMealTypes.includes(filters.mealType);});
    }

  if (filters.starNumber) {
    const starNum = parseInt(filters.starNumber);
    filtered = filtered.filter((result) => {
      const stars = result._source.star_number || 0;
      const soles = result._source.soles_number || 0;

      // Casos para cada número:
      // 1. Solo estrellas igual al número seleccionado
      // 2. Solo soles igual al número seleccionado
      // 3. Ambos igual al número seleccionado
      return (
          (stars === starNum && soles === 0) || // Solo estrellas
          (soles === starNum && stars === 0) || // Solo soles
          (stars === starNum && soles === starNum) // Ambos iguales
      );
    });
  }
    setFilteredResults(filtered);
  };

  // Función para renderizar imágenes de estrellas y soles
  const renderStarsAndSoles = (soles, stars) => {
    const starImages = stars > 0 ? Array.from({ length: stars }, (_, i) => (
      <img key={`star-${i}`} src={estrellaIcon} alt="Estrella" className="icon-star" />
    )) : null;

    const sunImages = soles > 0 ? Array.from({ length: soles }, (_, i) => (
      <img key={`sun-${i}`} src={solIcon} alt="Sol" className="icon-sun" />
    )) : null;

    return (
      <div className="starsAndSoles">
        {stars > 0 && (
          <div className="stars">
            <span className="titleText">Estrellas:</span>
            <span style={{ marginLeft: '5px' }}>{starImages}</span>
          </div>
        )}
        {soles > 0 && (
          <div className="soles">
            <span className="titleText">Soles:</span>
            <span style={{ marginLeft: '5px' }}>{sunImages}</span>
          </div>
        )}
      </div>
    );
  };

  const formatMealType = (mealType) => {
  if (typeof mealType === 'string') {
    // Dividir por mayúsculas y unir con espacios
    return mealType.replace(/([A-Z])/g, ' $1').trim();
  } else if (Array.isArray(mealType)) {
    return mealType.join(', ');
  }
  return '';
  };

  // Función para restablecer el estado
  const resetState = () => {
    setQuery('');
    setResults([]);
    setFilteredResults([]);
    setNotFound(false);
    setFilters({
      starsOrSoles: 'both',
      priceRange: '',
      mealType: '',
      starNumber: '',
    });
    setFilterOptions({
      priceRanges: [],
      mealTypes: [],
    });
  };

  return (
    <div className="App">
      <img
        src={logo}
        alt="Logo"
        className="App-logo"
        onClick={resetState} // Agregar manejador de clics
        style={{ cursor: 'pointer' }}
      />
      <form onSubmit={handleSearch} className="form">
        <input
          type="text"
          placeholder="Search for restaurants..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="input"
        />
        <button type="submit" className="button">Buscar</button>

        <button type="button" className="button" onClick={() => setShowFilters(!showFilters)}>
          <FontAwesomeIcon icon={faFilter} />
        </button>
      </form>

      {showFilters && (
        <div className="filters">
          <div className="filterGroup">
            <div className="filter">
              <select
                  value={filters.starsOrSoles}
                  onChange={(e) => setFilters({...filters, starsOrSoles: e.target.value})}>
                <option value="both">Tipo de galardon</option>
                <option value="estrellas">Estrellas</option>
                <option value="soles">Soles</option>
              </select>
            </div>
            <div className="filter">
              <select
                  value={filters.priceRange}
                  onChange={(e) => setFilters({...filters, priceRange: e.target.value})}>
                <option value="">Rango de precios</option>
                {filterOptions.priceRanges.map((price, index) => (
                    <option key={index} value={price}>{price}</option>
                ))}
              </select>
            </div>
            <div className="filter">
              <select
                  value={filters.mealType}
                  onChange={(e) => setFilters({...filters, mealType: e.target.value})}>
                <option value="">Tipo de comida</option>
                {filterOptions.mealTypes.map((mealType, index) => (
                    <option key={index} value={mealType}>{mealType}</option>
                ))}
              </select>
            </div>
            <div className="filter">
              <select
                  value={filters.starNumber}
                  onChange={(e) => setFilters({...filters, starNumber: e.target.value})}>
                <option value="">Número de galardones</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
              </select>
            </div>
            <div className="filterB">
              <button  onClick={clearFilters} className="buttonBorrar">
                <FontAwesomeIcon icon={faTrash} size="xs"/>
              </button>
              <button onClick={applyFilters} className="button">Aplicar Filtros</button>
            </div>
          </div>
        </div>
      )}

      {notFound && (
          <p className="notFound">No se encontraron resultados para "{query}".</p>
      )}

      <div className="resultsGrid">
      {filteredResults.map((result) => (
            <div
                key={result._id}
                className="resultCard"
                onClick={() => handleResultClick(result)}
                style={{ cursor: 'pointer' }}
          >
            <img
              src={result._source.restaurant_photo_url || "https://play-lh.googleusercontent.com/D-7VBAD71gJsTno_3uZYCEOt4TF7uf_FAesVtXBNkyjRbdJOh7y806mGu63Z3U1HYQ"}
              alt={result._source.name}
              className="restaurantPhoto"
            />
            <div className="resultInfo">
              <h2 className="resultName">{result._source.name}</h2>
              <p className="resultLocation">{result._source.direction}</p>
              <p className="resultPrice">{result._source.price}</p>
              <p className="resultMealType">{formatMealType(result._source.meal_type)}</p>
              {renderStarsAndSoles(result._source.soles_number, result._source.star_number)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AppWrapper() {
  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/:restaurantName" element={<RestaurantDetails />} />
    </Routes>
  );
}

export default AppWrapper;

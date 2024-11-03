import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import logo from './Logo.png';
import RestaurantDetails from './components/RestaurantDetails';
import solIcon from './solIcon.png';
import estrellaIcon from './estrellaIcon.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [notFound, setNotFound] = useState(false);
  const [filters, setFilters] = useState({
    starsOrSoles: 'both',
    community: '',
    priceRange: '',
    mealType: '',
    starNumber: '',
  });
  const [filterOptions, setFilterOptions] = useState({
    communities: [],
    priceRanges: [],
    mealTypes: [],
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
  const fetchResults = async (searchQuery) => {
    if (!searchQuery) return; // No hacer nada si no hay búsqueda
    try {
      const response = await axios.post('http://localhost:9200/restaurants/_search', {
        query: {
          bool: {
            should: [
              { wildcard: { "name": `*${searchQuery.toLowerCase()}*` } },
              { wildcard: { "meal_type": `*${searchQuery.toLowerCase()}*` } }
            ]
          }
        }
      });
      const hits = response.data.hits.hits;
      setResults(hits);
      setFilteredResults(hits); // Inicialmente, los resultados filtrados son todos los resultados
      setNotFound(hits.length === 0);

      // Rellenar opciones de filtros basados en los resultados de la búsqueda
      setFilterOptions({
        communities: [...new Set(hits.map((hit) => hit._source.community))],
        priceRanges: [...new Set(hits.map((hit) => hit._source.price))],
        mealTypes: [...new Set(hits.map((hit) => hit._source.meal_type))],
      });
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // useEffect para manejar el estado al regresar a la página principal
  useEffect(() => {
    if (location.state && location.state.query) {
      setQuery(location.state.query); // Restablece el query
      fetchResults(location.state.query); // Ejecuta la búsqueda con el query
    }
  }, [location.state]); // Ejecutar cuando el estado de la ubicación cambie

  // Manejo del clic en el resultado
  const handleResultClick = (restaurant) => {
    const restaurantName = restaurant._source.name.replace(/\s+/g, '-').toLowerCase();
    navigate(`/${restaurantName}`, { state: { query, restaurant: restaurant._source } }); // Pasar el query y el restaurante
  };

  // Aplicar filtros a los resultados
  const applyFilters = () => {
    let filtered = results;

      if (filters.starsOrSoles === 'estrellas') {
         filtered = filtered.filter((result) => (result._source.star_number > 0 && !result._source.soles_number));
      } else if (filters.starsOrSoles === 'soles') {
         filtered = filtered.filter((result) => (result._source.soles_number > 0 && !result._source.star_number));
      }

    if (filters.community) {
      filtered = filtered.filter((result) => result._source.community === filters.community);
    }
    if (filters.priceRange) {
      filtered = filtered.filter((result) => result._source.price === filters.priceRange);
    }
    if (filters.mealType) {
      filtered = filtered.filter((result) => result._source.meal_type === filters.mealType);
    }
    if (filters.starNumber) {
      filtered = filtered.filter((result) => result._source.star_number === parseInt(filters.starNumber));
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

  // Función para restablecer el estado
  const resetState = () => {
    setQuery('');
    setResults([]);
    setFilteredResults([]);
    setNotFound(false);
    setFilters({
      starsOrSoles: 'both',
      community: '',
      priceRange: '',
      mealType: '',
      starNumber: '',
    });
    setFilterOptions({
      communities: [],
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
        style={{ cursor: 'pointer' }} // Cambiar cursor para indicar que es clickeable
      />
      <form onSubmit={handleSearch} className="form">
        <input
          type="text"
          placeholder="Search for restaurants..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="input"
        />
        <button type="submit" className="button">Search</button>

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
                onChange={(e) => setFilters({ ...filters, starsOrSoles: e.target.value })}>
                <option value="both">Tipo de estrellas</option>
                <option value="estrellas">Solo Estrellas</option>
                <option value="soles">Solo Soles</option>
              </select>
            </div>
            <div className="filter">
              <select
                value={filters.community}
                onChange={(e) => setFilters({ ...filters, community: e.target.value })}>
                <option value="">Comunidades</option>
                {filterOptions.communities.map((community, index) => (
                  <option key={index} value={community}>{community}</option>
                ))}
              </select>
            </div>
            <div className="filter">
              <select
                value={filters.priceRange}
                onChange={(e) => setFilters({ ...filters, priceRange: e.target.value })}>
                <option value="">Rango de precios</option>
                {filterOptions.priceRanges.map((price, index) => (
                  <option key={index} value={price}>{price}</option>
                ))}
              </select>
            </div>
            <div className="filter">
              <select
                value={filters.mealType}
                onChange={(e) => setFilters({ ...filters, mealType: e.target.value })}>
                <option value="">Tipo de comida</option>
                {filterOptions.mealTypes.map((mealType, index) => (
                  <option key={index} value={mealType}>{mealType}</option>
                ))}
              </select>
            </div>
            <div className="filter">
              <select
                value={filters.starNumber}
                onChange={(e) => setFilters({ ...filters, starNumber: e.target.value })}>
                <option value="">Número de estrellas</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
              </select>
            </div>
          </div>
          <button onClick={applyFilters} className="button">Aplicar Filtros</button>
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
              src={result._source.restaurant_photo_url}
              alt={result._source.name}
              className="restaurantPhoto"
            />
            <div className="resultInfo">
              <h2 className="resultName">{result._source.name}</h2>
              <p className="resultLocation">Madrid, España</p>
              <p className="resultPrice">{result._source.price}</p>
              <p className="resultMealType">{result._source.meal_type}</p>
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

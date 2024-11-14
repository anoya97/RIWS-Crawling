import { useState, useCallback } from 'react';

const COORDINATE_API_URL = 'https://nominatim.openstreetmap.org/search?format=json&q=';

const useFetchCoordinates = () => {
  const [coordinates, setCoordinates] = useState(null);
  const [loading, setLoading] = useState(true);

  // useCallback se asegura de que la función sea estable y no cambie en cada renderizado
  const fetchCoordinates = useCallback(async (address) => {
    setLoading(true);
    try {
      const response = await fetch(`${COORDINATE_API_URL}${address}`);
      const data = await response.json();
      if (data.length > 0) {
        setCoordinates({
          lat: parseFloat(data[0].lat),
          lon: parseFloat(data[0].lon),
        });
      }
    } catch (error) {
      console.error("Error fetching coordinates:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  return { coordinates, loading, fetchCoordinates };
};

export default useFetchCoordinates;

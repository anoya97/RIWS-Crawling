import React, { useState } from 'react';
import axios from 'axios';
import logo from './Dineology_logo.jpeg'; // Asegúrate de tener el logo en la carpeta src

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:9200/restaurants/_search', {
        query: {
          multi_match: {
            query: query,
            fields: ['name', 'meal_type', 'description'],
          },
        },
      });
      setResults(response.data.hits.hits);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <div className="App" style={styles.container}>
      <img src={logo} alt="Logo" style={styles.logo} />
      <form onSubmit={handleSearch} style={styles.form}>
        <input
          type="text"
          placeholder="Search for restaurants..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>Search</button>
      </form>

      <ul style={styles.resultsList}>
        {results.map((result) => (
          <li key={result._id} style={styles.resultItem}>
            <h2 style={styles.resultName}>Name: {result._source.name}</h2>
            <p style={styles.resultPrice}>Price: {result._source.price}</p>
            <p style={styles.resultMealType}>Type: {result._source.meal_type}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center',
    padding: '50px',
    backgroundColor: '#f5f5f5',
  },
  logo: {
    width: '300px', // Ajusta el tamaño del logo
    marginBottom: '30px',
  },
  form: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '20px',
  },
  input: {
    width: '400px', // Ajusta el ancho del buscador
    padding: '10px',
    fontSize: '16px',
    border: '1px solid #ccc',
    borderRadius: '5px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    marginLeft: '10px',
    border: 'none',
    borderRadius: '5px',
    backgroundColor: '#4285f4', // Color similar al de Google
    color: '#fff',
    cursor: 'pointer',
  },
  resultsList: {
    listStyleType: 'none',
    padding: 0,
  },
  resultItem: {
    padding: '10px',
    borderBottom: '1px solid #ccc',
  },
  resultName: {
    fontSize: '20px',
    margin: 0,
  },
  resultMealType: {
    margin: '5px 0',
  },
  resultPrice: {
    margin: '5px 0',
    fontWeight: 'bold',
  },
};

export default App;

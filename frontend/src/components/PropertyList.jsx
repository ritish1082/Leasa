import { useState, useEffect } from 'react';
import { getProperties } from '../services/api';

const PropertyList = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        setLoading(true);
        const data = await getProperties();
        
        // Debugging: Log the fetched data
        console.log('Fetched data:', data); 
        
        // Handle non-array response
        if (Array.isArray(data)) {
          setProperties(data);
        } else if (data?.properties && Array.isArray(data.properties)) {
          setProperties(data.properties);
        } else {
          console.warn("Unexpected data format from getProperties:", data);
          setProperties([]); // Ensure it resets if the data is unexpected
        }

        setError(null);
      } catch (err) {
        setError('Failed to fetch properties. Please try again later.');
        console.error(err);
        setProperties([]); // Reset properties if an error occurs
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  if (loading) {
    return <div className="loading">Loading properties...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (properties.length === 0) {
    console.log('No properties to display'); // Debugging line
    return (
      <div className="no-properties">
        <h2>No properties available</h2>
        <p>Be the first to add a property!</p>
      </div>
    );
  }

  return (
    <div className="property-list">
      <h2>Available Properties</h2>
      <div className="properties-grid">
        {properties.map((property) =>
          property && property.id ? (
            <div key={property.id} className="property-card">
              <h3>{property.address || 'No Address Provided'}</h3>
              <p className="description">{property.description || 'No description'}</p>
              <div className="specifications">
                <h4>Landlord Specifications:</h4>
                <p>{property.specifications || 'N/A'}</p>
              </div>
              <div className="property-footer">
                <span className="property-id">ID: {property.id}</span>
                <span className="property-date">
                  Added: {new Date(property.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ) : null
        )}
      </div>
    </div>
  );
};

export default PropertyList;

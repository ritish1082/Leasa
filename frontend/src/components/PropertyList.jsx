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
        setProperties(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch properties. Please try again later.');
        console.error(err);
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
        {properties.map((property) => (
          <div key={property.id} className="property-card">
            <h3>{property.address}</h3>
            <p className="description">{property.description}</p>
            <div className="specifications">
              <h4>Landlord Specifications:</h4>
              <p>{property.specifications}</p>
            </div>
            <div className="property-footer">
              <span className="property-id">ID: {property.id}</span>
              <span className="property-date">
                Added: {new Date(property.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PropertyList;

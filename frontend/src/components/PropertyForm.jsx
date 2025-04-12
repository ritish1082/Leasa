import { useState } from 'react';
import { createProperty } from '../services/api';
import { useNavigate } from 'react-router-dom';

const PropertyForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    address: '',
    description: '',
    specifications: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Simple validation
    if (!formData.address || !formData.description || !formData.specifications) {
      setError('All fields are required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await createProperty(formData);
      
      // Reset form
      setFormData({
        address: '',
        description: '',
        specifications: '',
      });
      
      // Redirect to properties list
      navigate('/properties');
    } catch (err) {
      setError('Failed to create property. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="property-form-container">
      <h2>Add New Property</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form className="property-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="address">Property Address</label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="123 Main St, City, State, ZIP"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Property Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe the property (size, rooms, amenities, etc.)"
            rows={4}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="specifications">Landlord Specifications</label>
          <textarea
            id="specifications"
            name="specifications"
            value={formData.specifications}
            onChange={handleChange}
            placeholder="Specify tenant requirements (e.g., no pets, minimum income, etc.)"
            rows={4}
            disabled={loading}
          />
        </div>
        
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Adding Property...' : 'Add Property'}
        </button>
      </form>
    </div>
  );
};

export default PropertyForm;

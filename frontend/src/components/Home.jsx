import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Welcome to Leasa</h1>
        <h2>Your AI-Powered Real Estate Assistant</h2>
        <p>
          Finding the perfect property has never been easier. Leasa uses advanced AI to match
          tenants with properties that meet both their requirements and landlord preferences.
        </p>
        <div className="cta-buttons">
          <Link to="/chat" className="cta-button primary">
            Chat with Leasa
          </Link>
        </div>
      </div>

      <div className="features-section">
        <h2>How Leasa Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Smart Property Matching</h3>
            <p>
              Our AI analyzes your requirements and matches you with properties that meet your
              needs and the landlord's specifications.
            </p>
          </div>
          <div className="feature-card">
            <h3>Conversational Interface</h3>
            <p>
              Chat naturally with our AI agent to describe what you're looking for, ask questions,
              and get personalized recommendations.
            </p>
          </div>
          <div className="feature-card">
            <h3>For Landlords</h3>
            <p>
              List your properties with detailed specifications to find the perfect tenants who
              meet your requirements.
            </p>
          </div>
          <div className="feature-card">
            <h3>For Tenants</h3>
            <p>
              Describe your ideal property and let our AI find the best matches for you, saving
              time and effort in your property search.
            </p>
          </div>
        </div>
      </div>

      <div className="get-started-section">
        <h2>Get Started Today</h2>
        <p>
          Whether you're a landlord looking to list your property or a tenant searching for your
          next home, Leasa is here to help.
        </p>
        <div className="cta-buttons">
          <Link to="/add-property" className="cta-button primary">
            Add Your Property
          </Link>
          <Link to="/chat" className="cta-button secondary">
            Start Searching
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;

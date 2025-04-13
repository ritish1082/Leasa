import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <Link to="/">
          <h1 className="logo">Leasa</h1>
        </Link>
        <nav className="nav">
          <ul>
            <li>
              <Link to="/properties">Properties</Link>
            </li>
            <li>
              <Link to="/add-property">Add Property</Link>
            </li>
            <li>
              <Link to="/chat">Chat with Agent</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/Header.css';

const Header = () => {
    const navigate = useNavigate();

    const onSearch = (e) => {
        if (e.key === 'Enter') {
            navigate(`/search?q=${encodeURIComponent(e.target.value)}`);
        }
    };

    return (
    <header className="navbar navbar-expand-lg navbar-light bg-white shadow-sm custom-header">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          Crypta
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <Link className="nav-link" to="/database">Database</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/change-log">Change Log</Link>
            </li>
          </ul>
          <form className="d-flex me-3">
            <input
              className="form-control form-control-sm me-2"
              type="search"
              placeholder="Search"
              aria-label="Search"
              onKeyDown={onSearch}
            />
          </form>
          <ul className="navbar-nav">
            <li className="nav-item dropdown">
              <a
                className="nav-link dropdown-toggle"
                href="#"
                id="userDropdown"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="fas fa-user-circle fa-lg" />
              </a>
              <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li><Link className="dropdown-item" to="/profile">Profile</Link></li>
                <li><Link className="dropdown-item" to="/settings">Settings</Link></li>
                <li><hr className="dropdown-divider" /></li>
                <li><button className="dropdown-item">Logout</button></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </header>
    );
};

export default Header;
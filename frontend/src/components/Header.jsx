import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';
import profilePic from '../assets/images/profilePic.jpg';
import logo from '../assets/images/logo.png';
import '../styles/Header.css';

const Header = () => {
    const navigate = useNavigate();
    const [menuOpen, setMenuOpen] = useState(false);
    const [alertsOpen, setAlertsOpen] = useState(false);
    const [profileMenu, setProfileMenu] = useState(false);

    useEffect(() => {
      const handleClickOutside = (event) => {
        const trigger = document.getElementById('menuTrigger');
        const nav = document.getElementById('menuNav');
        const alerts = document.getElementById('alertsMenu')
        const profile = document.getElementById('profileDropdown')

        if (menuOpen && trigger && nav && !trigger.contains(event.target) && !nav.contains(event.target)) {
          setMenuOpen(false);
        }
        if (alertsOpen && alerts && !alerts.contains(event.target)) {
          setAlertsOpen(false);
        }
        if (profileMenu && profile && !profile.contains(event.target)) {
          setProfileMenu(false);
        }
      };
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }, [menuOpen, alertsOpen, profileMenu])

    const handleLogout = () => {
      localStorage.clear();
      navigate('/login');
    };

    return (
    <header className="custom-header fixed-top w-100 shadow-sm">
      <div className="container-fluid">
        <div className="d-flex align-items-center justify-content-between position-relative">
          <div className="menu-box-wrapper">
            <div
              id="menuTrigger" 
              className="menu-trigger"
              type="button"
              onClick={() => setMenuOpen(open => !open)}
              aria-expanded={menuOpen}
              >
               <div className="hamburger">
                <span></span>
                <span></span>
                <span></span>
               </div>
              <span className="toggler-label ms-2">MENU</span>
            </div>
            <nav 
              id="menuNav" 
              className={`menu-nav${menuOpen ? " active" : ""}`}
              >
              <ul className="nav flex-column">
                <li className="nav-item">
                  <Link className="nav-link" to="/">Home</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/database">Database</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/change-log">Change Log</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/auth-admin">User Admin</Link>
                </li>
                <li className="nav-item">
                  <a 
                    className="nav-link" 
                    href="https://nimbus.rcdoc.org/" 
                    target="_blank"
                    rel="noopener noreferrer"
                    >Nimbus</a>
                </li>
              </ul>
            </nav>
          </div>

          <div className="app-logo ms-3 d-flex align-items-center">
            <img src={logo}
                  alt="App Logo"
                  className="app-logo-img"/>
            <span className="org-title">Crypta 2.0</span>
          </div>

          <SearchBar
            className='search-form mx-auto'
            placeholder='Search...'
          />
          <div className="header-icons d-flex align-items-center">
            <a className="header-icon me-3" href="#"><i className="far fa-comment"/></a>
            <div 
              className="dropdown me-3" 
              id='alertsMenu'>
              <a
                className="header-icon position-relative"
                href="#"
                role="button"
                id="alertsDropdown"
                aria-expanded={alertsOpen}
                onClick={(e) => { e.preventDefault(); setAlertsOpen(open => !open); }}
                >
                <i className="fas fa-bell"></i>
                <span
                  className="position-absolute top-0 start-75 translate-middle badge rounded-pill bg-danger bell-badge"
                >
                  1
                  <span className="visually-hidden">unread alerts</span>
                </span>
                </a>
              <ul
                className={`dropdown-menu dropdown-menu-end p-2${alertsOpen ? ' show' : ''}`}
                aria-labelledby="alertsDropdown"
                style={{ minWidth: '200px'}}
              >
                <li>
                  <a className="dropdown-item" href="#">
                    <strong>RTFV:</strong> Pending Approval Tech Services.
                  </a>
                </li>
              </ul>
            </div>
            <a className="header-icon me-3" href="#"><i className="fas fa-inbox"></i></a>
            <div className="dropdown me-3">
              <a
                href="#"
                className="header-icon dropdown-toggle"
                id="profileDropdown"
                data-bs-toggle="dropdown"
                aria-expanded={profileMenu}
                onClick={(e) => { e.preventDefault(); setProfileMenu(open => !open); }}
              >
                <img
                  src={profilePic}
                  alt="Profile"
                  className="profile-pic rounded-circle"
                />
              </a>
              <ul
                className={`dropdown-menu dropdown-menu-end${profileMenu ? ' show' : ''}`}
                aria-labelledby="profileDropdown"
                style={{ minWidth: '150px' }}
              >
                <li>
                  <a className="dropdown-item" href="#">
                    Profile
                  </a>
                </li>
                <li>
                  <a className="dropdown-item" href="#">
                    Security
                  </a>
                </li>
                <li><hr className="dropdown-divider"/></li>
                <li>
                  <button className="dropdown-item" onClick={handleLogout}>
                    Log Out 
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </header>
    );
};

export default Header;
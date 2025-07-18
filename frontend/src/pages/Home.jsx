import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';
import databaseIcon from '../assets/images/database.png';
import scrollIcon from '../assets/images/scroll.png';
import Modal from '../components/Modal';

const Home = () => {
  const [temperature, setTemperature] = useState(null);
  const [awaitingActions] = useState([
    { id:1, title: 'RTFV: Pending Tech Services', date:'6-9-2025' }
  ]);
  const [inProgress] = useState([
    { id:1, title:'Build the Home page.', note:"Create a homepage similar to the picture given by Adam.", link:'/database', label:'View' },
    { id:2, title:'Build a Sudo Login Page.', note:'Create a nice looking fake login page.', link:'/login', label:'View' },
    { id:3, title:'Finish the Details Page.', note:'Bill gave me new categories and we have finished the layout design.', link:'/database', label:'View' }
  ]);
  const [upcomingDates] = useState([
    { id:1, date:'6-9-2025', event:'Demo Crypta', note:'To Msgr. Winslow' }
  ]);
  const [recentActions] = useState([
    'Help Desk Tickets',
    'Expense Authorization',
    'Request a Crypta Feature',
    'Canon 1281 Request',
    'AI Chat Bot'
  ]);

  useEffect(() => {
    // TODO: fetch real weather data
    setTemperature(72);
  }, []);

  return (
    <div className="home-background">
      <div className="home-container container my-5">
        <div className="row">
          <div className="col-12 home-header mb-4">
            <div className="row">
              <h2 className="col mb-0">Welcome, Kyle Greenberg</h2>
              <div className="col text-end">
                <span className="me-1 align-bottom">Charlotte, NC {temperature}°F</span>
                <i className="fas fa-sun"></i>
              </div>
            </div>
          </div>

          <div className="col-lg-8">
            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body text-center">
                <h3>Welcome to Crypta</h3>
                <h4>The Diocese of Charlotte's data vault.</h4>
                <h6>Here you can find information on churches, priests, schools and many other things.</h6>
                <div className="pt-3 pb-2 align-items-middle">
                  <button 
                  type="button" 
                  className="btn btn-sm me-2 mb-2" 
                  data-bs-toggle="modal" 
                  data-bs-target="#welcomeModal" 
                  id="welcometogglebtn"
                  >
                    Learn More
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-4">
            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body">
                <h3 className="text-center">Getting Started</h3>
                <div className="d-flex align-items-start mt-2">
                  <Link to="/database" className="icon-links me-3 align-self-center">
                    <img src={databaseIcon} alt="database" className="database-icon mb-3" width="40" height="40" />
                  </Link>
                  <div>
                    <Link to="/database" className="icon-links"><p className="mb-0">Database</p></Link>
                    <small className="text-muted">Search and access all data in Crypta.</small>
                  </div>
                </div>
                <div className="d-flex align-items-start mt-2">
                  <Link to="/change-log" className="icon-links me-3 align-self-center">
                    <img src={scrollIcon} alt="change log" className="database-icon mb-3" width="40" height="40" />
                  </Link>
                  <div>
                    <Link to="/change-log" className="icon-links"><p className="mb-0">Change Log</p></Link>
                    <small className="text-muted">Keep track of all the enhancements.</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-6">
            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body">
                <small className="text-muted">Awaiting Your Action</small>
                {awaitingActions.map(a => (
                  <div key={a.id} className="d-flex align-items-start mt-2">
                    <i className="fas fa-inbox fa-2x me-3 align-self-center"></i>
                    <div>
                      <p className="mb-0">{a.title}</p>
                      <small className="text-muted">Requested for {a.date}</small>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body">
                <small className="text-muted">Things In Progress</small>
                {inProgress.map(item => (
                  <div key={item.id} className="d-flex align-items-start mt-2">
                    <i className="fas fa-tasks fa-2x me-3 align-self-center"></i>
                    <div className="flex-grow-1">
                      <p className="mb-0">{item.title}</p>
                      <small className="text-muted">{item.note}</small>
                    </div>
                    <Link to={item.link} className="align-self-center">{item.label}</Link>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-lg-6">
            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body">
                <small className="text-muted">Upcoming Dates</small>
                <ul className="list-unstyled mb-2 mt-2">
                  {upcomingDates.map(d => (
                    <li key={d.id} className="d-flex justify-content-between align-items-center py-2 border-bottom">
                      <span>{d.date}  {d.event}</span>
                      <small className="text-muted">{d.note}</small>
                    </li>
                  ))}
                </ul>
                {/* Placeholder for more upcoming dates */}
                <a href="#" className="d-block">View More</a>
              </div>
            </div>

            <div className="card mb-4 border-0 rounded-4 shadow">
              <div className="card-body">
                <small className="text-muted">Recent Actions</small>
                <ul className="list-unstyled mt-2">
                  {recentActions.map((act, idx) => <li key={idx}>{act}</li>)}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <Modal id="welcomeModal" title="Welcome">
            <h5>In Crypta you can do the following:</h5>
            <h6>Database Queries on:</h6>
            <ul>
              <li>Priests</li>
              <li>Deacons</li>
              <li>Lay People</li>
              <li>Churches</li>
              <li>Schools</li>
              <li>Other Entities</li>
              <li>Endowments</li>
              <li>Etc.</li>
            </ul>
            <h6>Send Emails based on filtered results.</h6>
            <h6>Export specific queried data with specified information.</h6>
            <h6>Use our Robust Search Engine.</h6>
            <h6>Submit and see current workflows.</h6>
            <h6>Perform actions on pending requests. And much more...</h6>
        </Modal>
      </div>
    </div>
  );
};

export default Home;
import React, { useState } from 'react';
import '../styles/AuthAdmin.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';

const menuItems = [
  { key: 'users', label: 'Users' },
  { key: 'roles', label: 'Roles' },
  { key: 'tokens', label: 'Tokens' },
  { key: 'organization', label: 'Organizations' },
  { key: 'login_attempts', label: 'Audit Logins' },
  { key: 'cryptaGroup', label: 'Crypta Groups' },
  { key: 'queryPermission', label: 'Query Controls' }
];

const dummyData = {
  users: [
    { id: 1, username: 'admin', email: 'admin@example.com' },
    { id: 2, username: 'jdoe', email: 'jdoe@example.com' }
  ],
  roles: [
    { id: 1, name: 'Administrator' },
    { id: 2, name: 'Viewer' }
  ],
  tokens: [
    { id: 1, user: 'admin', type: 'access', revoked: false },
    { id: 2, user: 'jdoe', type: 'refresh', revoked: true }
  ]
};

const columnsMap = {
  users: [
    { title: 'ID', field: 'id' },
    { title: 'Username', field: 'username' },
    { title: 'Email', field: 'email' }

  ],
  roles: [
    { title: 'ID', field: 'id' },
    { title: 'Name', field: 'name' }
  ],
  tokens: [
    { title: 'ID', field: 'id' },
    { title: 'User', field: 'user' },
    { title: 'Type', field: 'type' },
    { title: 'Revoked', field: 'revoked' }
  ],
  organization: [
    { title: 'ID', field: 'id' },
    { title: 'Name', field: 'name' },
    { title: 'Location Reference', field:'ref_location' }
  ],
  login_attempts: [
    { title: 'ID', field: 'id' },
    { title: 'Email', field: 'email' },
    { title: 'Time', field: 'time' },
    { title: 'Successful', field: 'successful' },
    { title: 'IP Address', field: 'ip_address' }
  ],
  cryptaGroup: [
    { title: 'ID', field: 'id' },
    { title: 'Name', field: 'name'}
  ],
  queryPermission: [
    { title: 'ID', field: 'id' },
    { title: 'Group Name', field: 'group__name' },
    { title: 'Resource Type', field: 'resource_type' },
    { title: 'Access Type', field: 'access_type' },
    { title: 'View Limit', field: 'view_limits' },
    { title: "Filter Conditions", field: 'filter_conditions' }
  ]
};

const AuthAdmin = () => {
  const [active, setActive] = useState('users');

  const columns = columnsMap[active];
  const rows = dummyData[active];

  return (
    <div className="container-fluid auth-admin-page">
      <div className="row">
        <AsidePanel header="Manage">
          <ul className="nav flex-column">
            {menuItems.map(item => (
              <li key={item.key} className="nav-item">
                <button
                  className={`nav-link btn btn-link text-start w-100${active === item.key ? ' active' : ''}`}
                  onClick={() => setActive(item.key)}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </AsidePanel>
        <main className="col-md-8 p-4 bg-light">
          <Card title={menuItems.find(m => m.key === active).label}>
            <DataGrid columns={columns} data={rows} />
          </Card>
        </main>
      </div>
    </div>
  );
};

export default AuthAdmin;
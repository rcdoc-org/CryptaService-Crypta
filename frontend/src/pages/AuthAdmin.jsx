import React, { useState, useEffect, useMemo } from 'react';
import * as bootstrap from 'bootstrap';
import '../styles/AuthAdmin.css';
import AsidePanel from '../components/AsidePanel';
import Button from '../components/Button';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import Modal from '../components/Modal';
import {
  fetchUsers,
  fetchRoles,
  fetchTokens,
  fetchOrganizations,
  fetchLoginAttempts,
  fetchCryptaGroups,
  fetchQueryPermissions,
  createUser,
  updateUser,
  deleteUser,
  createRole,
  deleteRole,
  createOrganization,
  deleteOrganization,
  createCryptaGroup,
  deleteCryptaGroup,
  createQueryPermission,
  deleteQueryPermission,
} from '../api/auth';

const menuItems = [
  { key: 'users', label: 'Users' },
  { key: 'roles', label: 'Roles' },
  { key: 'tokens', label: 'Tokens' },
  { key: 'organization', label: 'Organizations' },
  { key: 'login_attempts', label: 'Audit Logins' },
  { key: 'cryptaGroup', label: 'Crypta Groups' },
  { key: 'queryPermission', label: 'Query Controls' }
];

const columnsMap = {
  users: [
    { title: 'ID', field: 'id' },
    { title: 'Email', field: 'email' },
    { title: 'Active', field: 'is_active'},
    { title: 'Last Login', field: 'last_login'},
    { title: 'Date Joined', field: 'date_joined'},
    { title: 'Suspended', field: 'suspend'}

  ],
  roles: [
    { title: 'ID', field: 'id' },
    { title: 'Name', field: 'name' }
  ],
  tokens: [
    { title: 'User', field: 'user_email' },
    { title: 'Type', field: 'type' },
    { title: 'Revoked', field: 'revoked' },
    { title: 'Expiration', field: 'expiration' },
    { title: 'Created At', field: 'created_at' },
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
    { title: 'Name', field: 'name'},
    { title: 'Description', field: 'description' },
    { title: 'Enabled', field: 'is_enabled' },
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

const booleanFields = ['is_active', 'is_staff', 'suspend', 'revoked', 'successful', 'is_primary'];

const createFieldsMap = {
  users: ['email', 'password'],
};

const fetchMap = {
  users: fetchUsers,
  roles: fetchRoles,
  tokens: fetchTokens,
  organization: fetchOrganizations,
  login_attempts: fetchLoginAttempts,
  cryptaGroup: fetchCryptaGroups,
  queryPermission: fetchQueryPermissions,
};

const AuthAdmin = () => {
  const [active, setActive] = useState('users');
  const [rows, setRows] = useState([]);
  const [selectedRow, setSelectedRow] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [formData, setFormData] = useState({});

  const createMap = {
    users: createUser,
    roles: createRole,
    organization: createOrganization,
    cryptaGroup: createCryptaGroup,
    queryPermission: createQueryPermission,
  };

  const deleteMap = {
    users: deleteUser,
    roles: deleteRole,
    organization: deleteOrganization,
    cryptaGroup: deleteCryptaGroup,
    queryPermission: deleteQueryPermission,
  };

  const handleSuspendToggle = (row) => {
    updateUser(row.id, { suspend: !row.suspend })
      .then(loadRows);
  };

  // const columns = columnsMap[active];
  const columns = useMemo(() => {
    const base = columnsMap[active];
    if (active === 'users') {
      return base.map(col =>
        col.field === 'suspend'
          ? {
              ...col,
              cellRenderer: params => (
                <input
                  type="checkbox"
                  checked={params.value}
                  onChange={() => handleSuspendToggle(params.data)}
                />
              ),
            }
          : col
      );
    }
    return base;
  }, [active]);

  const loadRows = () => {
    const fetchFn = fetchMap[active];
    if (fetchFn) {
      fetchFn()
        .then(res => setRows(res.data))
        .catch(() => setRows([]));
    }
  };

  useEffect(() => {
    loadRows();
  }, [active]);

  const openCreate = () => {
    const init = {};
    const fields = createFieldsMap[active] ||
      columnsMap[active].filter(col => col.field !== 'id').map(col => col.field);
    fields.forEach(field => {
      init[field] = booleanFields.includes(field) ? false : '';
    });
    setFormData(init);
    setShowCreate(true);
  };

  const handleCreate = () => {
    const fn = createMap[active];
    if (fn) {
      const data = { ...formData };
      if (active === 'users') {
        data.username = formData.email;
      }
      fn(data).then(loadRows);
    }
    const modalEl = document.getElementById('createModal');
    if (modalEl) {
      const instance = bootstrap.Modal.getInstance(modalEl);
      if (instance) {
        instance.hide();
      } else {
        setShowCreate(false);
      }
    } else {
      setShowCreate(false);
    }
  };

  useEffect(() => {
    if (showCreate) {
      const modalEl = document.getElementById('createModal');
      if (modalEl) {
        const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
        const hideHandler = () => setShowCreate(false);
        modalEl.addEventListener('hidden.bs.modal', hideHandler, { once: true });
        instance.show();
      }
    }
  }, [showCreate])

  const handleDelete = () => {
    if (!selectedRow) return;
    const fn = deleteMap[active];
    if (fn) {
      fn(selectedRow.id).then(() => {
        setSelectedRow(null);
        loadRows();
      });
    }
  };

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
            <row className='button-row'>
                <Button
                  className="Create mb-2 action-btn rounded-4"
                  onClick={openCreate}
                >
                  Create
                </Button>
                <Button
                  className="Create mb-2 action-btn rounded-4"
                  disabled={!selectedRow}
                  onClick={handleDelete}
                >
                  Delete
                </Button>
            </row>
            <DataGrid columns={columns} data={rows} options={{onSelect: setSelectedRow}} />
            {showCreate && (
              <Modal id="createModal" title={`Create ${active}`}
                footer={<Button onClick={handleCreate}>Save</Button>}
              >
                {(createFieldsMap[active] ||
                    columnsMap[active].filter(c => c.field !== 'id').map(c => c.field))
                  .map(field => {
                    const col = columnsMap[active].find(c => c.field === field) || { title: field };
                    return (
                      <div className="mb-3" key={field}>
                        <label className="form-label">{col.title}</label>
                        {booleanFields.includes(field) ? (
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={formData[field]}
                            onChange={e => setFormData({ ...formData, [field]: e.target.checked })}
                          />
                        ) : (
                          <input
                            type={field === 'password' ? 'password' : 'text'}
                            className="form-control"
                            value={formData[field]}
                            onChange={e => setFormData({ ...formData, [field]: e.target.value })}
                          />
                        )}
                      </div>
                    );
                  })}
              </Modal>
            )}
          </Card>
        </main>
      </div>
    </div>
  );
};

export default AuthAdmin;
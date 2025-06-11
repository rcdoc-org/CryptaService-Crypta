import React, { useEffect, useState } from 'react';
import '../styles/Database.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import { fetchFilterTree } from '../api/crypta';

const Database = () => {
    const [filterTree, setFilterTree] = useState([]);
    const [appliedFilters, setAppliedFilters] = useState([]);
    const [rows, setRows] = useState([]);

    useEffect(() => {
        fetchFilterTree('person').then(res => setFilterTree(res.data));
        // initial fetch of rows
        fetch('api/data?base=person').then(r => r.json()).then(data => setRows(data));
    }, [])

    const handleBaseChange = (e) => {
        const base = e.target.value;
        // Toggle between person/location
        fetchFilterTree(base).then(res => setFilterTree(res.data));
        fetch(`api/data?base=${base}`).then(r => r.json()).then(data => setRows(data));
    };

    const columns = [
        { title: 'Name', field: 'name', sorter: 'string', headerFilter: 'input' },
        { title: 'Type', field: 'type', sorter: 'string' },
        { title: 'Email', field: 'primary_email' },
        { title: 'Phone', field: 'primary_phone' },
        // …any other fields you want to show
        ];


    const gridOptions = {
        rowClick: (e, row) => {
            const data = row.getData();
            window.location.href = `/details/${data.base}/${data.id}`;
    }
  };

    return (
        <div className="container-fluid filter-page">
            <div className="row">
                <AsidePanel header="Database Options">
                <select className="form-select" onChange={handleBaseChange}>
                    <option value="person">People</option>
                    <option value="location">Locations</option>
                </select>
                </AsidePanel>
                <main className="col-md-8 p-4 bg-light">
                    <Card title='Results'>
                        <DataGrid columns={columns} data={rows} options={gridOptions} />
                    </Card>
                </main>
            </div>
        </div>
    );
};

export default Database;
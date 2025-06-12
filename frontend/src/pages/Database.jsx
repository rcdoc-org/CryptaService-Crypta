import React, { useEffect, useState } from 'react';
import '../styles/Database.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import Button from '../components/Button';
import Dropdown from '../components/Dropdown';
import SearchBar from '../components/SearchBar'
import { fetchFilterTree } from '../api/crypta';

const Database = () => {
    const [filterTree, setFilterTree] = useState([]);
    const [appliedFilters, setAppliedFilters] = useState([]);
    const [rows, setRows] = useState([]);
    const baseToggles = [
        { value: 'person', label: 'People' },
        { value: 'location', label: 'Locations' }
    ];

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
        },
    paginationSize: 20,
};

return (
    <div className="container-fluid filter-page">
            <div className="row">
                <AsidePanel header="Database Options">
                    <div className='p-4'>
                        <span className="side-panel-header">Database Options</span>
                        <Dropdown
                        options={baseToggles}
                        onChange={handleBaseChange}
                        id='baseToggle'
                        name='baseToggle'
                        className='side-panel-form'
                        ></Dropdown>
                    </div>
                    <div className='p-4'>
                        <span className="side-panel-header">Filter Options</span>
                        <SearchBar
                            id='filterSearch'
                            className='filter-search'
                            placeholder='Search filter options...'
                            onSearch={(value) => {
                                // Implement search logic here
                                console.log('Searching filters for:', value);
                            }}/>
                    </div>
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
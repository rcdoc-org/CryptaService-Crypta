import React, { useEffect, useState } from 'react';
import '../styles/Database.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import Button from '../components/Button';
import Dropdown from '../components/Dropdown';
import SearchBar from '../components/SearchBar';
import FilterTree from '../components/FilterTree';
import { fetchFilterTree, fetchFilterResults } from '../api/crypta';

const Database = () => {
    const [filterTree, setFilterTree] = useState([]);
    const [appliedFilters, setAppliedFilters] = useState([]);
    const [rows, setRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const [base, setBase] = useState('person');
    const [searchQuery, setSearchQuery] = useState('');
    const baseToggles = [
        { value: 'person', label: 'People' },
        { value: 'location', label: 'Locations' }
    ];

    const handleFilterToggle = (value) => {
        setAppliedFilters(prev =>
            prev.includes(value)
                ? prev.filter(f => f !== value)
                : [...prev, value]
        );
    };

    useEffect(() => {
        console.log('UseEffect activated.')
        const timeout = setTimeout(() => {
            fetchFilterTree(base, { filters: appliedFilters })
                .then(res => setFilterTree(res.data.filter_tree));
            fetchFilterResults(base, appliedFilters)
                .then(res => setRows(res.data.results));
        }, 250);

        return () => clearTimeout(timeout);
    }, [base, appliedFilters]);

    const handleBaseChange = (e) => {
        console.log('HandleBaseChange activated.')
        const newBase = e.target.value;
        setBase(newBase);
        setAppliedFilters([]);
    };

    useEffect(() => {
        if (rows.length > 0) {
            const keys = Object.keys(rows[0]);
            setColumns(keys.map(k => ({ title: k, field: k })));
        } else {
            setColumns([]);
        }
    }, [rows]);

    const filteredFilterTree = filterTree
        .map(group => {
            const groupMatch = 
                group.field.toLowerCase().includes(searchQuery.toLowerCase()) ||
                group.display?.toLowerCase().includes(searchQuery.toLowerCase());

            const filteredOptions = group.options.filter(opt => {
                const label = typeof opt.label === 'string' ? opt.label : String(opt.label ?? '');
                return label.toLowerCase().includes(searchQuery.toLowerCase())
            });
                

            return {
                ...group,
                options: groupMatch ? group.options : filteredOptions,
                open: groupMatch || filteredOptions.length > 0
            };
    }).filter(group => group.options.length > 0); // remove empty groups

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
                                // console.log('Searching filters for:', value);
                                setSearchQuery(value);
                            }}/>
                        <FilterTree
                            // tree={filterTree}
                            // tree={filteredFilterTree}
                            tree={filteredFilterTree.map(group => ({
                                ...group,
                                searchQuery: searchQuery.toLowerCase()
                            }))}
                            selectedFilters={appliedFilters}
                            onToggle={handleFilterToggle}
                            />
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
import React, { useEffect, useState } from 'react';
import '../styles/Database.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Dropdown from '../components/Dropdown';
import SearchBar from '../components/SearchBar';
import FilterTree from '../components/FilterTree';
import { fetchFilterTree, fetchFilterResults } from '../api/crypta';

const Database = () => {
    const [filterTree, setFilterTree] = useState([]);
    const [appliedFilters, setAppliedFilters] = useState([]);
    const [rows, setRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const [allColumns, setAllColumns] = useState([]);
    const [selectedCols, setSelectedCols] = useState(new Set());
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
            fetchFilterResults(base, { filters: appliedFilters })
                .then(res => {
                    const grid = res.data.grid;
                    setRows(grid.data);
                    setAllColumns(grid.columns);
                    setSelectedCols(new Set(grid.columns.map(c => c.field)));
                });
        }, 250);

        return () => clearTimeout(timeout);
    }, [base, appliedFilters]);

    const handleBaseChange = (e) => {
        console.log('HandleBaseChange activated.')
        const newBase = e.target.value;
        setBase(newBase);
        setAppliedFilters([]);
    };

    const handleColumnToggle = (field) => {
        setSelectedCols(prev => {
            const next = new Set(prev);
            if (next.has(field)) {
                next.delete(field);
            } else {
                next.add(field);
            }
            return next
        });
    };

    const applyColumns = () => {
        const modelEl = document.getElementById('columnModal');
        if (modalEl) {
            const instance = bootstrap.Modal.getInstance(modalEl);
            instance && instance.hide();
        }
    };

    const exportCsv = () => {
        if (!rows.length) return;
        const headers = Array.from(selectedCols);
        const csv = [headers.join(',')];
        rows.forEach(r => {
            const row = headers.map(h => JSON.stringify(r[h] ?? '')).join(',');
            csv.push(row);
        });
        const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'results.csv';
        a.click();
        URL.revokeObjectURL(url);
    };

    const exportExcel = () => exportCsv();
    const exportPdf = () => exportCsv();

    useEffect(() => {
        const cols = allColumns.filter(c => selectedCols.has(c.field));
        setColumns(cols);
    }, [allColumns, selectedCols]);

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
                    <div id="activeFilters" className='mb-3 d-flex flex-wrap'>
                        {appliedFilters.length > 0 && (
                            <span className='side-panel-header mb-2'>Active Filters</span>
                        )}
                        {appliedFilters.map((filterStr, index) => {
                            const [field, value] = filterStr.split(':', 2);

                            // Find display & label from each tree
                            const group = filterTree.find(g => g.field === field)
                            const option = group?.options.find(opt => String(opt.value) === value);

                            if (!group || !option) return null;

                            let label = option.label?.replace('/\\u002D/g','-') ?? value;

                            return (
                                <span
                                    key={index}
                                    className='badge bg-secondary me-2 mb-2 d-flex align-items-center'
                                    style={{ cursor: 'pointer' }}
                                    onClick={() => {
                                        const updated = appliedFilters.filter(f => f !== filterStr);
                                        setAppliedFilters(updated);
                                    }}
                                >
                                    {group.display}: {label}
                                    <i className='fas fa-times ms-2' />   
                                </span>
                            );
                        })}
                    </div>
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
                    <div className="btn-toolbar mb-2">
                        <button type="button" className="btn result-btn btn-sm me-2" data-bs-toggle="modal" data-bs-target="#columnModal">Add Fields</button>
                        <button type="button" className="btn result-btn btn-sm me-2" data-bs-toggle="modal" data-bs-target="#actionModal">Actions</button>
                    </div>
                    <DataGrid columns={columns} data={rows} options={gridOptions} />
                </Card>
            </main>
        </div>
        <Modal id="columnModal" title="Choose Columns" size="modal-lg" footer={
            <button type="button" className="btn btn-primary" onClick={applyColumns}>Apply</button>
        }>
            <form className="row g-3">
                {allColumns.filter(c => c.field !== 'id').map(col => (
                    <div key={col.field} className="col-6 form-check">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            id={`col_${col.field}`}
                            checked={selectedCols.has(col.field)}
                            onChange={() => handleColumnToggle(col.field)}
                        />
                        <label className="form-check-label" htmlFor={`col_${col.field}`}>{col.title}</label>
                    </div>
                ))}
            </form>
        </Modal>

        <Modal id="actionModal" title="Actions">
            <div className="d-grid gap-2">
                <button className="btn result-btn btn-sm" onClick={exportExcel}>Export to Excel</button>
                <button className="btn result-btn btn-sm" onClick={exportCsv}>Export to CSV</button>
                <button className="btn result-btn btn-sm" onClick={exportPdf}>Export to PDF</button>
            </div>
        </Modal>
    </div>

        
    );
};

export default Database;
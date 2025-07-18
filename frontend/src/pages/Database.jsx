import React, { useEffect, useState, useMemo } from 'react';
const bootstrap = window.bootstrap
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import '../styles/Database.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import DataGrid from '../components/DataGrid';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Dropdown from '../components/Dropdown';
import SearchBar from '../components/SearchBar';
import FilterTree from '../components/FilterTree';
import { 
    fetchFilterTree,
    fetchFilterResults,
    fetchEmailCountPreview,
    uploadTempFile,
    sendEmailRequest,
} from '../api/crypta';

const Database = () => {
    const [filterTree, setFilterTree] = useState([]);
    const [appliedFilters, setAppliedFilters] = useState([]);
    const [rows, setRows] = useState([]);
    const [unfilteredRows, setUnfilteredRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const [allColumns, setAllColumns] = useState([]);
    const [selectedCols, setSelectedCols] = useState(new Set());
    const [base, setBase] = useState('person');
    const [prevBase, setPrevBase] = useState('person');
    const [searchQuery, setSearchQuery] = useState('');
    const [emailSubject, setEmailSubject] = useState('');
    const [emailBody, setEmailBody] = useState('');
    const [includePersonal, setIncludePersonal] = useState(false);
    const [includeParish, setIncludeParish] = useState(false);
    const [includeDiocesan, setIncludeDiocesan] = useState(false);
    const [attachmentFile, setAttachmentFile] = useState(null);
    const [statsInfo, setStatsInfo] = useState([]);
    const [statRanges, setStatRanges] = useState({});
    const [statBooleans, setStatBooleans] = useState({});
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
        const baseChanged = base !== prevBase;
        setPrevBase(base);
        const timeout = setTimeout(() => {
            fetchFilterTree(base, { filters: appliedFilters })
                .then(res => setFilterTree(res.data.filter_tree));
            fetchFilterResults(base, { filters: appliedFilters })
                .then(res => {
                    const grid = res.data.grid;
                    setUnfilteredRows(grid.data);
                    setRows(grid.data);
                    setAllColumns(grid.columns);
                    setStatsInfo(res.data.stats_info || [])
                    // setSelectedCols(new Set(grid.columns.map(c => c.field)));
                    const defaults = base === 'person'
                        ? ['First Name', 'Middle Name', 'Last Name']
                        : ['Name', 'Type'];

                    setSelectedCols(prev => {
                        const available = new Set(grid.columns.map(c => c.field));
                        if (prev.size === 0 || baseChanged) {
                            const initial = defaults.filter(f => available.has(f));
                            return new Set(initial);
                        }
                        const next = [...prev].filter(f => available.has(f));
                        return new Set(next);
                    });
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

    // Initialize stat filter defaults whenever stats info changes
    useEffect(() => {
        const ranges = {};
        const bools = {};
        statsInfo.forEach(info => {
            if (info.type === 'number') {
                ranges[info.field] = { min: info.min, max: info.max };
            } else if (info.type === 'boolean') {
                bools[info.field] = 'all';
            }
        });
        setStatRanges(ranges);
        setStatBooleans(bools);
    }, [statsInfo]);

    // Apply stat based filtering
    useEffect(() => {
        const filtered = unfilteredRows.filter(row => {
            for (const info of statsInfo) {
                if (info.type === 'number') {
                    const range = statRanges[info.field];
                    if (!range) continue;
                    const val = parseFloat(row[info.field]);
                    if (isNaN(val)) return false;
                    if (val < range.min || val > range.max) return false;
                } else if (info.type === 'boolean') {
                    const choice = statBooleans[info.field];
                    if (choice && choice !== 'all') {
                        const val = String(row[info.field]);
                        if (val !== choice) return false;
                    }
                }
            }
            return true;
        });
        setRows(filtered);
    }, [unfilteredRows, statRanges, statBooleans, statsInfo]);

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

    const handleRangeChange = (field, part, value) => {
        setStatRanges(prev => {
            const current = prev[field] || { min: 0, max: 0 };
            const updated = { ...current, [part]: value };
            if (updated.min > updated.max) {
                if (part === 'min') updated.max = value;
                else updated.min = value;
            }
            return { ...prev, [field]: updated };
        });
    };

    const handleBooleanChange = (field, value) => {
        setStatBooleans(prev => ({ ...prev, [field]: value }));
    };

    const applyColumns = () => {
        const modalEl = document.getElementById('columnModal');
        const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
        instance.hide();
    };

    const openEmailModal = () => {
        // hide the Actions modal before showing the Email modal
        const actionEl = document.getElementById('actionModal');
        if (actionEl) {
            const actionInstance = bootstrap.Modal.getOrCreateInstance(actionEl);
            actionInstance.hide();
        }
        const emailEl = document.getElementById('emailModal');
        const emailInstance = bootstrap.Modal.getOrCreateInstance(emailEl);
        emailInstance.show();
    };

    // Group all columns (excluding internal id) by category
    const groupedColumns = allColumns
        .filter(c => c.field !== 'id')
        .reduce((acc, col) => {
            const cat = col.category || 'Other';
            (acc[cat] = acc[cat] || []).push(col);
            return acc;
        }, {});

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

    const exportExcel = () => {
        if (!rows.length) return;
        const headers = Array.from(selectedCols);
        // Convert to array of objects, matching headers
        const data = rows.map(row => {
            const obj = {};
            headers.forEach(header => {
                obj[header] = row[header] ?? '';
            });
            return obj;
        });

        const worksheet = XLSX.utils.json_to_sheet(data, { header: headers });
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Results');

        XLSX.writeFile(workbook, 'results.xlsx');
    };
    
    const exportPdf = () => {
        if (!rows.length) return;

        const headers = Array.from(selectedCols);
        const data = rows.map(row =>
            headers.map(header => row[header] ?? '')
        );

        const doc = new jsPDF({
            orientation: 'landscape',
            unit: 'pt',
            format: 'A4',
        });

        doc.text('Crypta Exported Results', 40, 30);

        autoTable(doc, {
            startY: 50,
            head: [headers],
            body: data,
            margin: { top: 40, left: 40, right: 40 },
            styles: {
                fontSize: 8,
                overflow: 'linebreak',
                cellWidth: 'wrap',
            },
            headStyles: {
                fillColor: [0, 57, 107], // Optional: theme blue
                textColor: 255,
            },
        });

        doc.save('results.pdf');
    };

    const computeSummaries = () => {
        const visibleNumeric = statsInfo.filter(
            s => s.type === 'number' && selectedCols.has(s.field)
        );
        return visibleNumeric.map(info => {
            const nums = rows
                .map(r => parseFloat(r[info.field]))
                .filter(n => !isNaN(n));

            if (!nums.length) {
                return {
                    display: info.display,
                    min: 0,
                    median: 0,
                    avg: 0,
                    max: 0,
                    total: 0,
                };
            }

            nums.sort((a, b) => a - b);
            const total = nums.reduce((a, b) => a + b, 0);
            const avg = (total / nums.length).toFixed(2);
            const mid = Math.floor(nums.length / 2);
            const median = nums.length % 2
                ? nums[mid]
                : ((nums[mid - 1] + nums[mid]) / 2);

            return {
                display: info.display,
                min: Math.min(...nums),
                median: median.toFixed(2),
                avg,
                max: Math.max(...nums),
                total: total.toFixed(2),
            };
        });
    };

    const statsSummary = useMemo(
        () => computeSummaries(),
        [rows, statsInfo, selectedCols]
    );

    const handleSendEmail = async () => {
        const recipients = [];
        if (includePersonal) recipients.push('Personal');
        if (includeParish) recipients.push('Parish');
        if (includeDiocesan) recipients.push('Diocesan');

        if (!emailSubject.trim() || !emailBody.trim() || recipients.length === 0) {
            alert("Please provide subject, body, and at least one recipient type.");
            return;
        }

        const previewPayload = {
            base,
            filters: appliedFilters,
            personalEmail: includePersonal,
            parishEmail: includeParish,
            diocesanEmail: includeDiocesan,
        };

        let count = 0;
        try {
            const { data } = await fetchEmailCountPreview(previewPayload);
            count = data.count;
        } catch (err) {
            alert('Failed to get recipient count');
            return;
        }

        const summary = 
            `Please confirm before sending:\n\n` +
            `Subject: ${emailSubject}\n` +
            `Recipients: ${recipients.join(', ')}\n` +
            `Total recipients: ${count}\n\n` +
            `Body:\n${emailBody}`;

        if (!window.confirm(summary)) return;

        let attachmentPath = null;
        if (attachmentFile) {
            try {
                const { data } = await uploadTempFile(attachmentFile);
                attachmentPath = data.url;
            } catch (err) {
                alert('Failed to upload attachment');
                return;
            }
        }

        const formData = new FormData();
        formData.append('subject', emailSubject);
        formData.append('body', emailBody);
        if (includePersonal) formData.append('personalEmail', 'on');
        if (includeParish) formData.append('parishEmail', 'on');
        if (includeDiocesan) formData.append('diocesanEmail', 'on');
        if (attachmentPath) formData.append('temp_attachment_path', attachmentPath);
        formData.append('base', base);
        appliedFilters.forEach(f => formData.append('filters', f))

        try {
            await sendEmailRequest(formData);
            alert('Email Sent');
            const modalEl = document.getElementById('emailModal');
            const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
            instance.hide();
        } catch (err) {
            alert('Failed to send email')
        }
    };

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

                    {/* Statistics Filters */}
                    {statsInfo.length > 0 && (
                        <div id="statsFilters" className='mt-4'>
                            <h6>Statistics</h6>
                            {statsInfo
                                .filter(info => selectedCols.has(info.field))
                                .map(info => (
                                    info.type === 'number' ? (
                                        <div key={info.field} className='stats-range mb-3'>
                                            <label className='mb-2'>{info.display}:</label>
                                            <div className='range_container'>
                                                <div className='sliders_control mb-1'>
                                                    <input
                                                        type='range'
                                                        min={info.min}
                                                        max={info.max}
                                                        value={statRanges[info.field]?.min ?? info.min}
                                                        className='range-from'
                                                        onChange={e => handleRangeChange(info.field, 'min', Number(e.target.value))}
                                                    />
                                                    <input
                                                        type='range'
                                                        min={info.min}
                                                        max={info.max}
                                                        value={statRanges[info.field]?.max ?? info.max}
                                                        className='range-to'
                                                        onChange={e => handleRangeChange(info.field, 'max', Number(e.target.value))}
                                                        style={{ background: (() => {
                                                            const r = statRanges[info.field] || {min: info.min, max: info.max};
                                                            const rangeDistance = info.max - info.min;
                                                            const fromPos = r.min - info.min;
                                                            const toPos = r.max - info.min;
                                                            const lowPct = (fromPos / rangeDistance) * 100;
                                                            const highPct = (toPos / rangeDistance) * 100;
                                                            return `linear-gradient(to right,#C6C6C6 0%,#C6C6C6 ${lowPct}%,#4a5568 ${lowPct}%,#4a5568 ${highPct}%,#C6C6C6 ${highPct}%,#C6C6C6 100%)`;
                                                        })() }}
                                                    />
                                                </div>
                                                <div className='form_control'>
                                                    <input
                                                        type='number'
                                                        className='stats-val-box'
                                                        min={info.min}
                                                        max={info.max}
                                                        value={statRanges[info.field]?.min ?? info.min}
                                                        onChange={e => handleRangeChange(info.field, 'min', Number(e.target.value))}
                                                    />
                                                    <input
                                                        type='number'
                                                        className='stats-val-box'
                                                        min={info.min}
                                                        max={info.max}
                                                        value={statRanges[info.field]?.max ?? info.max}
                                                        onChange={e => handleRangeChange(info.field, 'max', Number(e.target.value))}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div key={info.field} className='mb-3'>
                                            <label>{info.display}:</label><br />
                                            {['true','false','all'].map(val => (
                                                <div className='form-check form-check-inline' key={val}>
                                                    <input
                                                        className='form-check-input'
                                                        type='radio'
                                                        name={`stat_${info.field}`}
                                                        value={val}
                                                        checked={(statBooleans[info.field] || 'all') === val}
                                                        onChange={() => handleBooleanChange(info.field, val)}
                                                    />
                                                    <label className='form-check-label'>
                                                        {val.charAt(0).toUpperCase() + val.slice(1)}
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    )
                                ))}
                        </div>
                    )}
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
                {statsSummary.length > 0 && (
                    <Card title='Statistics Summary' className='mt-4'>
                        <div className='table-responsive'>
                            <table className='table table-sm mb-0'>
                                <thead>
                                    <tr>
                                        <th>Metric</th>
                                        <th>Min</th>
                                        <th>Median</th>
                                        <th>Average</th>
                                        <th>Max</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {statsSummary.map(s => (
                                        <tr key={s.display}>
                                            <td>{s.display}</td>
                                            <td>{s.min}</td>
                                            <td>{s.median}</td>
                                            <td>{s.avg}</td>
                                            <td>{s.max}</td>
                                            <td>{s.total}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>
                )}
            </main>
        </div>
        <Modal id="columnModal" title="Choose Columns" size="modal-lg" footer={
            <button type="button" className="btn btn-primary" onClick={applyColumns}>Apply</button>
        }>
            <form>
                <div className="accordion" id="columnsAccordion">
                    {Object.entries(groupedColumns).map(([cat, cols], idx) => (
                        <div className="accordion-item" key={cat}>
                            <h2 className="accordion-header" id={`heading${idx}`}>
                                <button
                                    className={`accordion-button ${idx > 0 ? 'collapsed' : ''}`}
                                    type="button"
                                    data-bs-toggle="collapse"
                                    data-bs-target={`#collapse${idx}`}
                                    aria-expanded={idx === 0}
                                    aria-controls={`collapse${idx}`}
                                >
                                    {cat} ({cols.length})
                                </button>
                            </h2>
                            <div
                                id={`collapse${idx}`}
                                className={`accordion-collapse collapse ${idx === 0 ? 'show' : ''}`}
                                aria-labelledby={`heading${idx}`}
                                data-bs-parent="#columnsAccordion"
                            >
                                <div className="accordion-body row">
                                    {cols.map(col => (
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
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </form>
        </Modal>

        <Modal id="actionModal" title="Actions">
            <div className="d-grid gap-2">
                <button className='btn result-btn btn-sm' data-bs-toggle='modal' data-bs-target='#emailModal'>Send Email</button>
                {/* <button className='btn result-btn btn-sm' onClick={openEmailModal}>Send Email</button> */}
                <button className="btn result-btn btn-sm" onClick={exportExcel}>Export to Excel</button>
                <button className="btn result-btn btn-sm" onClick={exportCsv}>Export to CSV</button>
                <button className="btn result-btn btn-sm" onClick={exportPdf}>Export to PDF</button>
            </div>
        </Modal>

        <Modal id="emailModal" title="Send Email" size="modal-lg" footer={
            <button type="button" className="btn btn-primary" onClick={handleSendEmail}>Send</button>
        }>
            <div className="mb-3 form-check form-check-inline">
                <input type="checkbox" className="form-check-input" id="personalEmail" checked={includePersonal} onChange={e => setIncludePersonal(e.target.checked)} />
                <label className="form-check-label" htmlFor="personalEmail">Include Personal Emails?</label>
            </div>
            <div className="mb-3 form-check form-check-inline">
                <input type="checkbox" className="form-check-input" id="parishEmail" checked={includeParish} onChange={e => setIncludeParish(e.target.checked)} />
                <label className="form-check-label" htmlFor="parishEmail">Include Parish Emails?</label>
            </div>
            <div className="mb-3 form-check form-check-inline">
                <input type="checkbox" className="form-check-input" id="diocesanEmail" checked={includeDiocesan} onChange={e => setIncludeDiocesan(e.target.checked)} />
                <label className="form-check-label" htmlFor="diocesanEmail">Include Diocesan Emails?</label>
            </div>
            <div className="mb-3">
                <label htmlFor="subjectInput" className="form-label">Subject</label>
                <input type="text" className="form-control" id="subjectInput" value={emailSubject} onChange={e => setEmailSubject(e.target.value)} />
            </div>
            <div className="mb-3">
                <label htmlFor="attachmentInput" className="form-label">Attachment</label>
                <input type="file" className="form-control" id="attachmentInput" onChange={e => setAttachmentFile(e.target.files[0])} />
            </div>
            <div className="mb-3">
                <label htmlFor="bodyInput" className="form-label">Body</label>
                <textarea className="form-control" id="bodyInput" rows="4" value={emailBody} onChange={e => setEmailBody(e.target.value)} />
            </div>
        </Modal>
    </div>

        
    );
};

export default Database;
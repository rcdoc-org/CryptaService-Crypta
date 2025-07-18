import React, { useState, useEffect } from 'react';

const FilterTree = ({ tree, selectedFilters, onToggle }) => {
    const [openGroups, setOpenGroups] = useState({});

    useEffect(() => {
        const newOpenGroups = {};
        tree.forEach(group => {
            const groupMatch =
                group.display?.toLowerCase().includes(group.searchQuery) ||
                group.field.toLowerCase().includes(group.searchQuery);

            const optionMatch = group.options.some(opt =>
                String(opt.label ?? '').toLowerCase().includes(group.searchQuery)
            );

            newOpenGroups[group.field] = group.searchQuery === ''
                ? false
                : groupMatch || optionMatch;
        });
        setOpenGroups(newOpenGroups);
    }, [tree]);

    const toggleGroup = (field) => {
        setOpenGroups(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    return (
        <ul className="list-unstyled" id="filterSidebar">
            {tree.map(group => (
                <li key={group.field} className="mb-3">
                    <div className="filter-group">
                        <div
                            className="filter-label d-flex justify-content-between align-items-center mt-3"
                            role="button"
                            onClick={() => toggleGroup(group.field)}
                        >
                            <span>{group.display}</span>
                            <i
                                className={`fas fa-chevron-down transition-transform ${
                                        openGroups[group.field] ? 'rotate-180': ''
                                    }`}
                            />
                        </div>
                        {openGroups[group.field] && (
                            <ul className="ps-3 mb-0">
                                {group.options.map(opt => {
                                    const value = `${group.field}:${opt.value}`;
                                    return (
                                        <li key={value}>
                                            <div className="form-check">
                                                <input
                                                    className="form-check-input filter-checkbox"
                                                    type="checkbox"
                                                    id={`filter_${group.field}_${opt.value}`}
                                                    value={value}
                                                    checked={selectedFilters.includes(value)}
                                                    onChange={() => onToggle(value)}
                                                />
                                                <label
                                                    className="form-check-label"
                                                    htmlFor={`filter_${group.field}_${opt.value}`}
                                                >
                                                    {opt.label} <span className="text-muted">({opt.count})</span>
                                                </label>
                                            </div>
                                        </li>
                                    );
                                })}
                            </ul>
                        )}
                    </div>
                </li>
            ))}
        </ul>
    );
};

export default FilterTree;

import React from 'react';

const FilterTree = ({ tree, selectedFilters, onToggle }) => {
    return (
        <ul className="list-unstyled" id="filterSidebar">
        {tree.map(group => (
            <li key={group.field} className="mb-3">
            <details open>
                <summary className="filter-label">{group.display}</summary>
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
                        <label className="form-check-label" htmlFor={`filter_${group.field}_${opt.value}`}> 
                            {opt.label} <span className="text-muted">({opt.count})</span>
                        </label>
                        </div>
                    </li>
                    );
                })}
                </ul>
            </details>
            </li>
        ))}
        </ul>
    );
};

export default FilterTree;

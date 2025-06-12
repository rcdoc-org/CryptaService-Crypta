import React from 'react';

const SearchBar = ({ onSearch, id, placeholder = 'Search...', className = '' }) => {
    return (
        <div className='mb-2'>
            <div className={`d-flex align-items-center ${className}`}>
                <i className='fas fa-search search-icon me-2'/>
                <input
                    type='text'
                    id={id}
                    className='form-control form-control-sm'
                    placeholder={placeholder}
                    aria-label='Search'
                    onChange={(e) => onSearch(e.target.value)}
                    />
            </div>
        </div>
    );
};

export default SearchBar;
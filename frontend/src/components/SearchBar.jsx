import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SearchBar = ({ 
    onSearch,   // optional: live callback
    onSubmit,   // optional: enter-key or submit callback
    id, 
    placeholder = 'Search...', 
    className = '' 
}) => {
    const [q, setQ] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        const val = e.target.value; 
        setQ(val);
        onSearch && onSearch(val);
    };

    const handleSubmit = e => {
        e.preventDefault();
        onSubmit 
            ? onSubmit(q)
            : !onSearch && navigate(`/search?q=${encodeURIComponent(q)}`);
    };
    
    return (
    <form onSubmit={handleSubmit} className={`d-flex align-items-center ${className}`}>
      <i className="fas fa-search search-icon me-2" />
      <input
        type="text"
        id={id}
        className="form-control form-control-sm"
        placeholder={placeholder}
        value={q}
        onChange={handleChange}
        aria-label="Search"
      />
    </form>
  );
};

export default SearchBar;
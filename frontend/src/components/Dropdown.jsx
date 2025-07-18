import React from 'react';

const Dropdown = ({ options, onChange, id, className ='', name = ''}) => {
    return (
        <select 
            className={`form-select ${className}`}
            id={id}
            aria-label={`${name}Toggle`}
            name= {name}
            onChange={(e) => onChange(e)}
            >
                {options.map((option, index) => (
                    <option
                        key={index}
                        value={option.value}
                        >
                            {option.label || option.value}
                        </option>
                )
            )}
            </select>

    );
};

export default Dropdown;
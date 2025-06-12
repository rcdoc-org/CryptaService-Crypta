import React from 'react';

const Dropdown = ({ options, onChange, id, className ='', name = ''}) => {
    return (
        <select 
            className={`form-select ${className}`}
            id={id}
            aria-label={`${name}Toggle`}
            name= {name}
            >
                {options.map((option, index) => (
                    <option
                        key={index}
                        value={option.value}
                        onClick={ () => onChange(option.value) }
                        >
                            {option.label || option.value}
                        </option>
                )
            )}
            </select>

    );
};

export default Dropdown;
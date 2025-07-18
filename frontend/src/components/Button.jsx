import React from 'react';

const Button = ({ onClick, children, className= '', type= 'button', disabled = false }) => {
    return (
        <button
            type={type}
            className={`btn btn-primary ${className}`}
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
};

export default Button;

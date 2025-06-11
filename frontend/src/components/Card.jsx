import React from 'react';

const Card = ({ title, children, className = '' }) => {
    <div className={`card mb-4 border-0 rounded-4 shadow-sm ${className}`}>
        <div className="card-body">
            {title && <small className="text-muted">{title}</small>}
            <div className="mt-2">
                {children}
            </div>
        </div>
    </div>
};

export default Card;
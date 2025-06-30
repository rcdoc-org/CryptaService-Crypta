import React from 'react';
import '../styles/Card.css'

const Card = ({ 
    title, 
    children, 
    className = '', 
    headerTag = 'small' 
}) => {
    const HeaderTag = headerTag

    return (
        <div className={`card mb-4 border-0 rounded-4 shadow-sm ${className}`}>
        <div className="card-body">
            {title &&(
                <HeaderTag className={headerTag === 'small' ?
                    'text-muted'
                    : 'text-center'}>
                        {title}
                    </HeaderTag>
                )}
            <div className="mt-2">
                {children}
            </div>
        </div>
    </div>
    )
    
};

export default Card;
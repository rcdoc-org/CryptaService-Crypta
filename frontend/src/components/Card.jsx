import React from 'react';

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
            {title && headerTag === 'small' && (
                <HeaderTag className="text-muted">
                    {title}
                </HeaderTag>
            )}
            {title && (
                <HeaderTag className="text-center">
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
import React from 'react';

const AsidePanel = ({ children, header, className}) => {
    <aside className={` col-md-4 p-0 aside-panel shadow ${className}`}>
        <div className="p-4">
            <h5 className="side-panel-header">{header}</h5>
            {children}
        </div>
    </aside>
}

export default AsidePanel;
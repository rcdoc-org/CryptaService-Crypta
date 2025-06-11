import React from 'react';

const Modal = ({ id, title, children, footer, size = 'modal-lg' }) => {
    <div className="modal fade" id={id} tabIndex="-1" area-hidden="true">
        <div className={`modal-dialog ${size}`}>
            <div className="modal-content">
                <div className="modal-header">
                    <h5 className="modal-title">{title}</h5>
                    <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div className="modal-body">{children}</div>
                {footer && <div className="modal-footer">{footer}</div>}
            </div>
        </div>
    </div>
};

export default Modal;
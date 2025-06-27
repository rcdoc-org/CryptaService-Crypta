import React from 'react';
import '../styles/Modal.css'

const Modal = ({ id, title, children, footer, size = 'modal-lg' }) => {
    return (
    <div 
        className="modal fade" 
        id={id} 
        tabIndex="-1" 
        aria-hidden='true'
        >
            <div className={`modal-dialog ${size}`}>
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title" id={`${id}Label`}>{title}</h5>
                        <button 
                            type="button" 
                            className="btn-close custom-close align-self-start" 
                            data-bs-dismiss="modal" 
                            aria-label="Close">
                            </button>
                    </div>
                    <div className="modal-body">{children}</div>
                    {footer && <div className="modal-footer">{footer}</div>}
                </div>
            </div>
    </div>
    );
};

export default Modal;
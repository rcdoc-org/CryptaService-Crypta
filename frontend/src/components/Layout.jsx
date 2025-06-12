import React from 'react';
import Header from './Header';

const Layout = ({ children }) => {
    return (
    <>
        <Header />
        <main className="app-main home-background">
            {children}
        </main>
    </>
    );
};

export default Layout;
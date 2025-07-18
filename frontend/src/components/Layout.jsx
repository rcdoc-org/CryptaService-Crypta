import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';

const Layout = () => {
    return (
    <>
        <Header />
        <main className="app-main home-background">
            <Outlet />
        </main>
    </>
    );
};

export default Layout;
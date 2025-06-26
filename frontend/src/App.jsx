import React from 'react';
import { Routes, Route, BrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import SearchResults from './pages/SearchResults';
import Details from './pages/Details';
import Database from './pages/Database';
import ChangeLog from './pages/ChangeLog';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Register from './pages/Register';
import AuthAdmin from './pages/AuthAdmin';
import './styles/App.css';

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

// Define Routes and wrap in Layout component
const App = () => {
    return (
    <BrowserRouter>
        <Routes>
            
            <Route path='/login' element={<Login />} />
            <Route path='/register' element={<Register />} />

            <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                    <Route path='/' element={<Home />} />
                    <Route path='/database' element={<Database />} />
                    <Route path='/search' element={<SearchResults />} />
                    <Route path='/details/:base/:id' element={<Details />} />
                    <Route path='/change-log' element={<ChangeLog />} />
                    <Route path='/auth-admin' element={<AuthAdmin />} />
                    <Route path='*' element={<NotFound />} />
                </Route>
            </Route>
            
        </Routes>
    </BrowserRouter>
    )
}

export default App;
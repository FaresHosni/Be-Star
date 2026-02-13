import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Tickets from './pages/Tickets'
import Distributors from './pages/Distributors'
import Admins from './pages/Admins'
import AddAdmin from './pages/AddAdmin'
import EditAdmin from './pages/EditAdmin'
import Login from './pages/Login'
import LiveEngagement from './pages/LiveEngagement'
import ChatWidget from './components/ChatWidget'

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [admin, setAdmin] = useState(null)

    useEffect(() => {
        const token = localStorage.getItem('token')
        const adminData = localStorage.getItem('admin')
        if (token && adminData) {
            setIsAuthenticated(true)
            setAdmin(JSON.parse(adminData))
        }
    }, [])

    const handleLogin = (token, adminData) => {
        localStorage.setItem('token', token)
        localStorage.setItem('admin', JSON.stringify(adminData))
        setIsAuthenticated(true)
        setAdmin(adminData)
    }

    const handleLogout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('admin')
        setIsAuthenticated(false)
        setAdmin(null)
    }

    if (!isAuthenticated) {
        return <Login onLogin={handleLogin} />
    }

    return (
        <Router>
            <div className="flex min-h-screen">
                <Sidebar admin={admin} onLogout={handleLogout} />
                <main className="flex-1 p-8 mr-64">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/tickets" element={<Tickets />} />
                        <Route path="/distributors" element={<Distributors />} />
                        <Route path="/admins" element={<Admins />} />
                        <Route path="/admins/add" element={<AddAdmin />} />
                        <Route path="/admins/edit/:id" element={<EditAdmin />} />
                        <Route path="/engagement" element={<LiveEngagement />} />
                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </main>
                <ChatWidget />
            </div>
        </Router>
    )
}

export default App

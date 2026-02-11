import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    Ticket,
    Users,
    LogOut,
    Star,
    Shield
} from 'lucide-react'

function Sidebar({ admin, onLogout }) {
    const location = useLocation()

    const menuItems = [
        { path: '/', icon: LayoutDashboard, label: 'لوحة التحكم' },
        { path: '/tickets', icon: Ticket, label: 'التذاكر' },
        { path: '/distributors', icon: Users, label: 'الموزعين' },
        { path: '/admins', icon: Shield, label: 'المسؤولين' },
    ]

    return (
        <aside className="sidebar fixed right-0 top-0 h-screen w-64 flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-gold-500/20">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center">
                        <Star className="w-7 h-7 text-dark-500" fill="currentColor" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold gold-text">كن نجماً</h1>
                        <p className="text-xs text-white/50">Be Star</p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 overflow-y-auto">
                {menuItems.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.path
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`sidebar-item ${isActive ? 'active' : ''}`}
                        >
                            <Icon className="w-5 h-5" />
                            <span>{item.label}</span>
                        </Link>
                    )
                })}
            </nav>

            {/* Admin Info */}
            <div className="p-4 border-t border-gold-500/20">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-semibold text-white">{admin?.name || 'مدير'}</p>
                        <p className="text-xs text-white/50">{admin?.email}</p>
                    </div>
                    <button
                        onClick={onLogout}
                        className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                        title="تسجيل الخروج"
                    >
                        <LogOut className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar

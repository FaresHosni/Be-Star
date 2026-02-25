import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../utils/api'
import {
    Ticket,
    Users,
    DollarSign,
    Clock,
    TrendingUp,
    Star,
    LogOut
} from 'lucide-react'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts'

function Dashboard() {
    const navigate = useNavigate()
    const [stats, setStats] = useState({
        total_tickets: 0,
        by_status: { pending: 0, payment_submitted: 0, approved: 0, rejected: 0, activated: 0 },
        by_type: { vip: 0, student: 0 },
        total_revenue: 0,
        total_customers: 0
    })
    const [recentTickets, setRecentTickets] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStats()
        fetchRecentTickets()
    }, [])

    const fetchStats = async () => {
        try {
            const res = await apiFetch('/api/stats/dashboard')
            if (!res.ok) return  // Don't crash on 401/403/500
            const data = await res.json()
            if (data && data.by_type) setStats(data)
        } catch (error) {
            console.error('Error fetching stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchRecentTickets = async () => {
        try {
            const res = await apiFetch('/api/stats/recent-tickets?limit=5')
            const data = await res.json()
            setRecentTickets(data)
        } catch (error) {
            console.error('Error fetching recent tickets:', error)
        }
    }

    const statCards = [
        {
            title: 'إجمالي التذاكر',
            value: stats.total_tickets,
            icon: Ticket,
            color: 'from-gold-500 to-gold-400'
        },
        {
            title: 'تذاكر VIP',
            value: stats.by_type?.vip || 0,
            icon: Star,
            color: 'from-purple-500 to-purple-400'
        },
        {
            title: 'تذاكر Student',
            value: stats.by_type?.student || 0,
            icon: Users,
            color: 'from-blue-500 to-blue-400'
        },
        {
            title: 'الإيرادات',
            value: `${stats.total_revenue.toLocaleString()} جنيه`,
            icon: DollarSign,
            color: 'from-green-500 to-green-400'
        },
    ]

    const pieData = [
        { name: 'معتمدة', value: stats.by_status.approved, color: '#22C55E' },
        { name: 'في المراجعة', value: stats.by_status.payment_submitted, color: '#FBBF24' },
        { name: 'مرفوضة', value: stats.by_status.rejected, color: '#EF4444' },
        { name: 'مفعلة', value: stats.by_status.activated, color: '#3B82F6' },
    ]

    const getStatusBadge = (status) => {
        const badges = {
            payment_submitted: 'badge-pending',
            approved: 'badge-approved',
            rejected: 'badge-rejected'
        }
        const labels = {
            payment_submitted: 'في المراجعة',
            approved: 'معتمد',
            rejected: 'مرفوض'
        }
        return <span className={`badge ${badges[status] || 'badge-pending'}`}>{labels[status] || status}</span>
    }

    return (
        <div className="space-y-8 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold gold-text">لوحة التحكم</h1>
                    <p className="text-white/60 mt-2">مرحباً بك في نظام إدارة تذاكر كن نجماً</p>
                </div>
                <button
                    onClick={() => {
                        localStorage.removeItem('token')
                        localStorage.removeItem('admin')
                        window.location.href = '/login'
                    }}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                    title="تسجيل الخروج"
                >
                    <LogOut className="w-5 h-5" />
                    <span>خروج</span>
                </button>
            </div>

            {/* Event Info Card */}
            <div className="card bg-gradient-to-l from-gold-500/20 to-transparent border-gold-500/40">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-gold-500">🌟 إيفنت كن نجماً</h2>
                        <p className="text-white/70 mt-1">2026-02-11 | سوهاج - الكوامل - قاعة قناة السويس</p>
                    </div>
                    <div className="flex items-center gap-2 text-gold-400">
                        <Clock className="w-5 h-5" />
                        <span>متبقي 3 أيام</span>
                    </div>
                </div>
            </div>

            {/* Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((card, index) => {
                    const Icon = card.icon
                    return (
                        <div key={index} className="stat-card">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-white/60 text-sm">{card.title}</p>
                                    <p className="text-3xl font-bold text-white mt-2">{card.value}</p>
                                </div>
                                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center`}>
                                    <Icon className="w-7 h-7 text-dark-500" />
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gold-500 mb-4">حالة التذاكر</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: '#1a1a1a',
                                        border: '1px solid rgba(212, 175, 55, 0.3)',
                                        borderRadius: '8px',
                                        direction: 'rtl'
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex flex-wrap justify-center gap-4 mt-4">
                        {pieData.map((item, index) => (
                            <div key={index} className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: item.color }}
                                />
                                <span className="text-sm text-white/70">{item.name}: {item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Tickets */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gold-500 mb-4">أحدث التذاكر</h3>
                    <div className="space-y-4">
                        {recentTickets.length === 0 ? (
                            <p className="text-white/50 text-center py-8">لا توجد تذاكر بعد</p>
                        ) : (
                            recentTickets.map((ticket) => (
                                <div
                                    key={ticket.id}
                                    className="flex items-center justify-between p-4 bg-dark-200 rounded-xl border border-gold-500/10"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold-500 to-gold-400 flex items-center justify-center">
                                            <Ticket className="w-5 h-5 text-dark-500" />
                                        </div>
                                        <div>
                                            <p className="font-semibold text-white">{ticket.customer_name}</p>
                                            <p className="text-sm text-white/50">{ticket.code}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className={`badge ${ticket.ticket_type === 'VIP' ? 'badge-vip' : 'badge-student'}`}>
                                            {ticket.ticket_type}
                                        </span>
                                        {getStatusBadge(ticket.status)}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard

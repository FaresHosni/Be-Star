import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Search,
    Filter,
    Check,
    X,
    Download,
    Eye,
    Loader2,
    RefreshCw,
    ArrowRight
} from 'lucide-react'

function Tickets() {
    const navigate = useNavigate()
    const [tickets, setTickets] = useState([])
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')
    const [statusFilter, setStatusFilter] = useState('all')

    useEffect(() => {
        fetchTickets()
    }, [statusFilter])

    const fetchTickets = async () => {
        setLoading(true)
        try {
            const url = statusFilter === 'all'
                ? '/api/tickets/'
                : `/api/tickets/?status=${statusFilter}`
            const res = await fetch(url)
            const data = await res.json()
            setTickets(data)
        } catch (error) {
            console.error('Error fetching tickets:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleApprove = async (ticketId) => {
        if (!confirm('هل أنت متأكد من الموافقة على هذه التذكرة؟')) return
        try {
            const res = await fetch(`/api/tickets/${ticketId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: true })
            })
            if (!res.ok) {
                 const data = await res.json()
                 throw new Error(data.detail || 'فشل الموافقة على التذكرة')
            }
            fetchTickets()
        } catch (error) {
            console.error('Error approving ticket:', error)
            alert(error.message)
        }
    }

    const handleReject = async (ticketId, reason = 'تم الرفض') => {
        if (!confirm('هل أنت متأكد من رفض هذه التذكرة؟')) return
        try {
            const res = await fetch(`/api/tickets/${ticketId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: false, rejection_reason: reason })
            })
            if (!res.ok) {
                 const data = await res.json()
                 throw new Error(data.detail || 'فشل رفض التذكرة')
            }
            fetchTickets()
        } catch (error) {
            console.error('Error rejecting ticket:', error)
            alert(error.message)
        }
    }

    const getStatusBadge = (status) => {
        const badges = {
            payment_submitted: { class: 'badge-pending', label: 'في المراجعة' },
            approved: { class: 'badge-approved', label: 'معتمد' },
            rejected: { class: 'badge-rejected', label: 'مرفوض' }
        }
        const badge = badges[status] || badges.payment_submitted
        return <span className={`badge ${badge.class}`}>{badge.label}</span>
    }

    const filteredTickets = tickets.filter(ticket =>
        ticket.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.code.includes(searchTerm) ||
        ticket.customer_phone.includes(searchTerm)
    )

    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate(-1)}
                        className="p-3 rounded-xl bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                        title="رجوع"
                    >
                        <ArrowRight className="w-6 h-6" />
                    </button>
                    <div>
                        <h1 className="text-3xl font-bold gold-text">إدارة التذاكر</h1>
                        <p className="text-white/60 mt-2">عرض ومراجعة جميع حجوزات التذاكر</p>
                    </div>
                </div>
                <button onClick={fetchTickets} className="btn-gold flex items-center gap-2">
                    <RefreshCw className="w-5 h-5" />
                    تحديث
                </button>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="flex flex-wrap gap-4">
                    {/* Search */}
                    <div className="flex-1 min-w-[280px]">
                        <div className="relative">
                            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                            <input
                                type="text"
                                placeholder="بحث بالاسم، الكود، أو رقم الهاتف..."
                                className="input-gold pr-12"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* Status Filter */}
                    <div className="flex items-center gap-2">
                        <Filter className="w-5 h-5 text-gold-500" />
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="input-gold w-auto"
                        >
                            <option value="all">جميع الحالات</option>
                            <option value="payment_submitted">في المراجعة</option>
                            <option value="approved">معتمد</option>
                            <option value="rejected">مرفوض</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Tickets Table */}
            <div className="card overflow-hidden p-0">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="w-10 h-10 text-gold-500 animate-spin" />
                    </div>
                ) : filteredTickets.length === 0 ? (
                    <div className="text-center py-20 text-white/50">
                        لا توجد تذاكر
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="table-gold">
                            <thead>
                                <tr>
                                    <th>الكود</th>
                                    <th>الاسم</th>
                                    <th>الهاتف</th>
                                    <th>النوع</th>
                                    <th>السعر</th>
                                    <th>طريقة الدفع</th>
                                    <th>الحالة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredTickets.map((ticket) => (
                                    <tr key={ticket.id}>
                                        <td>
                                            <span className="font-mono text-gold-400">{ticket.code}</span>
                                        </td>
                                        <td>{ticket.customer_name}</td>
                                        <td className="font-mono">{ticket.customer_phone}</td>
                                        <td>
                                            <span className={`badge ${ticket.ticket_type === 'VIP' ? 'badge-vip' : 'badge-student'}`}>
                                                {ticket.ticket_type}
                                            </span>
                                        </td>
                                        <td>{ticket.price} جنيه</td>
                                        <td>{ticket.payment_method || '-'}</td>
                                        <td>{getStatusBadge(ticket.status)}</td>
                                        <td>
                                            <div className="flex items-center gap-2">
                                                {ticket.payment_proof && (
                                                    <button
                                                        onClick={() => navigate(`/tickets/${ticket.id}/proof`)}
                                                        className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors"
                                                        title="عرض إثبات الدفع"
                                                    >
                                                        <Eye className="w-4 h-4" />
                                                    </button>
                                                )}

                                                {(ticket.status === 'pending' || ticket.status === 'payment_submitted') && (
                                                    <>
                                                        <button
                                                            onClick={() => handleApprove(ticket.id)}
                                                            className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                                                            title="موافقة"
                                                        >
                                                            <Check className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleReject(ticket.id)}
                                                            className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                                            title="رفض"
                                                        >
                                                            <X className="w-4 h-4" />
                                                        </button>
                                                    </>
                                                )}

                                                {(ticket.status === 'approved' || ticket.status === 'activated') && (
                                                    <button
                                                        onClick={() => {
                                                            const link = document.createElement('a')
                                                            link.href = `/api/tickets/${ticket.id}/pdf`
                                                            link.download = `ticket_${ticket.code}.pdf`
                                                            document.body.appendChild(link)
                                                            link.click()
                                                            document.body.removeChild(link)
                                                        }}
                                                        className="p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                                                        title="تحميل التذكرة"
                                                    >
                                                        <Download className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>


        </div>
    )
}

export default Tickets

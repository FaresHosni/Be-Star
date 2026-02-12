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
    const [selectedTicket, setSelectedTicket] = useState(null)
    const [showProofModal, setShowProofModal] = useState(false)

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
        try {
            await fetch(`/api/tickets/${ticketId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: true })
            })
            fetchTickets()
        } catch (error) {
            console.error('Error approving ticket:', error)
        }
    }

    const handleReject = async (ticketId, reason = 'تم الرفض') => {
        try {
            await fetch(`/api/tickets/${ticketId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: false, rejection_reason: reason })
            })
            fetchTickets()
        } catch (error) {
            console.error('Error rejecting ticket:', error)
        }
    }

    const getStatusBadge = (status) => {
        const badges = {
            pending: { class: 'badge-pending', label: 'معلق' },
            payment_submitted: { class: 'badge-pending', label: 'في المراجعة' },
            approved: { class: 'badge-approved', label: 'معتمد' },
            rejected: { class: 'badge-rejected', label: 'مرفوض' },
            activated: { class: 'badge-approved', label: 'مفعّل' }
        }
        const badge = badges[status] || badges.pending
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
                            <option value="pending">معلق</option>
                            <option value="payment_submitted">في المراجعة</option>
                            <option value="approved">معتمد</option>
                            <option value="rejected">مرفوض</option>
                            <option value="activated">مفعّل</option>
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
                                                        onClick={() => {
                                                            setSelectedTicket(ticket)
                                                            setShowProofModal(true)
                                                        }}
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

            {/* Payment Proof Modal */}
            {showProofModal && selectedTicket && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => setShowProofModal(false)}
                                    className="p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                                    title="رجوع"
                                >
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                                <h3 className="text-xl font-bold text-gold-500">إثبات الدفع - {selectedTicket.code}</h3>
                            </div>
                            <button
                                onClick={() => setShowProofModal(false)}
                                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-white/50">الاسم:</span>
                                    <span className="mr-2">{selectedTicket.customer_name}</span>
                                </div>
                                <div>
                                    <span className="text-white/50">الهاتف:</span>
                                    <span className="mr-2">{selectedTicket.customer_phone}</span>
                                </div>
                                <div>
                                    <span className="text-white/50">البريد الإلكتروني:</span>
                                    <span className="mr-2">{selectedTicket.customer_email || '-'}</span>
                                </div>
                                <div>
                                    <span className="text-white/50">النوع:</span>
                                    <span className="mr-2">{selectedTicket.ticket_type}</span>
                                </div>
                                <div>
                                    <span className="text-white/50">السعر:</span>
                                    <span className="mr-2">{selectedTicket.price} جنيه</span>
                                </div>
                            </div>

                            {selectedTicket.payment_proof && (
                                <div className="mt-4">
                                    <p className="text-white/50 mb-2">صورة إثبات الدفع:</p>
                                    <img
                                        src={selectedTicket.payment_proof}
                                        alt="إثبات الدفع"
                                        className="w-full rounded-lg border border-gold-500/30"
                                    />
                                </div>
                            )}

                            {(selectedTicket.status === 'pending' || selectedTicket.status === 'payment_submitted') && (
                                <div className="flex gap-4 mt-6">
                                    <button
                                        onClick={() => {
                                            handleApprove(selectedTicket.id)
                                            setShowProofModal(false)
                                        }}
                                        className="btn-gold flex-1 flex items-center justify-center gap-2"
                                    >
                                        <Check className="w-5 h-5" />
                                        موافقة
                                    </button>
                                    <button
                                        onClick={() => {
                                            handleReject(selectedTicket.id)
                                            setShowProofModal(false)
                                        }}
                                        className="flex-1 py-3 px-6 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <X className="w-5 h-5" />
                                        رفض
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Tickets

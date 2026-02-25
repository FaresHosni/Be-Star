import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ArrowRight, Check, X, Loader2, User, Phone, Mail,
    CreditCard, Hash, Tag, Image, AlertCircle
} from 'lucide-react'

function PaymentProof() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [ticket, setTicket] = useState(null)
    const [loading, setLoading] = useState(true)
    const [actionLoading, setActionLoading] = useState(false)
    const [error, setError] = useState(null)
    const [actionDone, setActionDone] = useState(null) // 'approved' | 'rejected'

    useEffect(() => {
        fetchTicket()
    }, [id])

    const fetchTicket = async () => {
        setLoading(true)
        try {
            const res = await fetch('/api/tickets/')
            const data = await res.json()
            const found = data.find(t => t.id === parseInt(id))
            if (found) {
                setTicket(found)
            } else {
                setError('التذكرة غير موجودة')
            }
        } catch (e) {
            setError('حدث خطأ في تحميل البيانات')
        } finally {
            setLoading(false)
        }
    }

    const handleApprove = async () => {
        setActionLoading(true)
        try {
            await fetch(`/api/tickets/${id}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: true })
            })
            setActionDone('approved')
            setTimeout(() => navigate('/tickets'), 1500)
        } catch (e) {
            setError('حدث خطأ أثناء الموافقة')
        } finally {
            setActionLoading(false)
        }
    }

    const handleReject = async () => {
        setActionLoading(true)
        try {
            await fetch(`/api/tickets/${id}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved: false, rejection_reason: 'تم الرفض' })
            })
            setActionDone('rejected')
            setTimeout(() => navigate('/tickets'), 1500)
        } catch (e) {
            setError('حدث خطأ أثناء الرفض')
        } finally {
            setActionLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-10 h-10 text-gold-500 animate-spin" />
            </div>
        )
    }

    if (error && !ticket) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                <AlertCircle className="w-16 h-16 text-red-400/50" />
                <p className="text-white/50 text-lg">{error}</p>
                <button onClick={() => navigate('/tickets')} className="btn-gold flex items-center gap-2">
                    <ArrowRight className="w-5 h-5" />
                    رجوع للتذاكر
                </button>
            </div>
        )
    }

    // Success overlay after approve/reject
    if (actionDone) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 animate-fade-in">
                <div className={`w-24 h-24 rounded-full flex items-center justify-center ${actionDone === 'approved'
                        ? 'bg-green-500/20 ring-4 ring-green-500/30'
                        : 'bg-red-500/20 ring-4 ring-red-500/30'
                    }`}>
                    {actionDone === 'approved'
                        ? <Check className="w-12 h-12 text-green-400" />
                        : <X className="w-12 h-12 text-red-400" />
                    }
                </div>
                <h2 className="text-2xl font-bold text-white">
                    {actionDone === 'approved' ? 'تمت الموافقة ✅' : 'تم الرفض ❌'}
                </h2>
                <p className="text-white/40">جاري العودة لصفحة التذاكر...</p>
            </div>
        )
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/tickets')}
                    className="p-3 rounded-xl bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors"
                    title="رجوع للتذاكر"
                >
                    <ArrowRight className="w-6 h-6" />
                </button>
                <div>
                    <h1 className="text-2xl font-bold gold-text">
                        إثبات الدفع — {ticket.code}
                    </h1>
                    <p className="text-white/40 mt-1 text-sm">مراجعة بيانات التذكرة وإثبات الدفع</p>
                </div>
            </div>

            {/* Ticket Info Card */}
            <div className="card-dark rounded-2xl border border-gold-500/10 overflow-hidden">
                <div className="p-5 border-b border-white/5">
                    <h3 className="text-white/60 text-sm font-medium mb-4">بيانات التذكرة</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-y-5 gap-x-8">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-gold-500/10 flex items-center justify-center">
                                <User className="w-4 h-4 text-gold-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">الاسم</p>
                                <p className="text-white font-medium">{ticket.customer_name}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                <Phone className="w-4 h-4 text-blue-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">الهاتف</p>
                                <p className="text-white font-mono text-sm">{ticket.customer_phone}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-purple-500/10 flex items-center justify-center">
                                <Mail className="w-4 h-4 text-purple-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">البريد الإلكتروني</p>
                                <p className="text-white text-sm">{ticket.customer_email || '—'}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                <Tag className="w-4 h-4 text-amber-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">النوع</p>
                                <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${ticket.ticket_type === 'VIP' ? 'bg-gold-500/20 text-gold-400' : 'bg-blue-500/20 text-blue-400'
                                    }`}>{ticket.ticket_type}</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-green-500/10 flex items-center justify-center">
                                <CreditCard className="w-4 h-4 text-green-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">السعر</p>
                                <p className="text-white font-bold">{ticket.price} جنيه</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-lg bg-pink-500/10 flex items-center justify-center">
                                <Hash className="w-4 h-4 text-pink-400" />
                            </div>
                            <div>
                                <p className="text-white/30 text-xs">طريقة الدفع</p>
                                <p className="text-white text-sm">{ticket.payment_method || '—'}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Payment Proof Image */}
                {ticket.payment_proof && (
                    <div className="p-5">
                        <div className="flex items-center gap-2 mb-3">
                            <Image className="w-4 h-4 text-gold-400" />
                            <h3 className="text-white/60 text-sm font-medium">صورة إثبات الدفع</h3>
                        </div>
                        {ticket.payment_proof.startsWith('data:image') || ticket.payment_proof.startsWith('http') ? (
                            <div className="rounded-xl overflow-hidden border border-gold-500/20 bg-black/30">
                                <img
                                    src={ticket.payment_proof}
                                    alt="إثبات الدفع"
                                    className="w-full max-h-[60vh] object-contain"
                                />
                            </div>
                        ) : (
                            <div className="p-4 rounded-xl bg-white/5 border border-gold-500/20 text-white/70">
                                📎 {ticket.payment_proof}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            {(ticket.status === 'pending' || ticket.status === 'payment_submitted') && (
                <div className="flex gap-4">
                    <button
                        onClick={handleApprove}
                        disabled={actionLoading}
                        className="flex-1 py-4 px-6 rounded-xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 text-green-400 border border-green-500/30 hover:from-green-500/30 hover:to-emerald-500/30 transition-all font-bold text-lg flex items-center justify-center gap-3 disabled:opacity-50"
                    >
                        {actionLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Check className="w-6 h-6" />}
                        موافقة ✅
                    </button>
                    <button
                        onClick={handleReject}
                        disabled={actionLoading}
                        className="flex-1 py-4 px-6 rounded-xl bg-gradient-to-r from-red-500/20 to-rose-500/20 text-red-400 border border-red-500/30 hover:from-red-500/30 hover:to-rose-500/30 transition-all font-bold text-lg flex items-center justify-center gap-3 disabled:opacity-50"
                    >
                        {actionLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <X className="w-6 h-6" />}
                        رفض ❌
                    </button>
                </div>
            )}

            {/* Already processed indicator */}
            {ticket.status !== 'pending' && ticket.status !== 'payment_submitted' && (
                <div className={`p-4 rounded-xl border flex items-center gap-3 ${ticket.status === 'approved' || ticket.status === 'activated'
                        ? 'bg-green-500/10 border-green-500/20 text-green-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-400'
                    }`}>
                    {ticket.status === 'approved' || ticket.status === 'activated'
                        ? <Check className="w-5 h-5" />
                        : <X className="w-5 h-5" />
                    }
                    <span className="font-medium">
                        {ticket.status === 'approved' || ticket.status === 'activated' ? 'هذه التذكرة معتمدة بالفعل' : 'هذه التذكرة مرفوضة'}
                    </span>
                </div>
            )}
        </div>
    )
}

export default PaymentProof

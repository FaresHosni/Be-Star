import React, { useState, useEffect, useCallback } from 'react'
import {
    AlertTriangle, Filter, Eye, X, CheckCircle,
    Clock, MessageSquare, ChevronDown
} from 'lucide-react'
import { apiFetch } from '../utils/api'

const API = '/api/complaints'

function ComplaintsPage() {
    const [complaints, setComplaints] = useState([])
    const [loading, setLoading] = useState(true)
    const [statusFilter, setStatusFilter] = useState('')
    const [selectedComplaint, setSelectedComplaint] = useState(null)
    const [resolutionNote, setResolutionNote] = useState('')
    const [stats, setStats] = useState({ total: 0, open: 0, escalated: 0, resolved: 0 })

    const fetchComplaints = useCallback(async () => {
        setLoading(true)
        try {
            const url = statusFilter ? `${API}/?status=${statusFilter}` : `${API}/`
            const res = await apiFetch(url)
            const data = await res.json()
            setComplaints(data)
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [statusFilter])

    const fetchStats = async () => {
        try {
            const res = await apiFetch(`${API}/stats`)
            const data = await res.json()
            setStats(data)
        } catch (e) { console.error(e) }
    }

    useEffect(() => { fetchComplaints() }, [fetchComplaints])
    useEffect(() => { fetchStats() }, [])

    const resolveComplaint = async (id) => {
        try {
            await apiFetch(`${API}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status: 'resolved',
                    resolution_note: resolutionNote || null,
                })
            })
            setSelectedComplaint(null)
            setResolutionNote('')
            fetchComplaints()
            fetchStats()
        } catch (e) { console.error(e) }
    }

    const getStatusBadge = (status) => {
        const styles = {
            open: 'bg-red-500/20 text-red-400 border-red-500/30',
            escalated: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
            resolved: 'bg-green-500/20 text-green-400 border-green-500/30',
        }
        const labels = {
            open: '🔴 مفتوحة',
            escalated: '🟠 مصعّدة',
            resolved: '✅ تم الحل',
        }
        return (
            <span className={`badge border ${styles[status] || styles.open}`}>
                {labels[status] || status}
            </span>
        )
    }

    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold gold-text">🔺 الشكاوى المباشرة</h1>
                <p className="text-white/60 mt-1">متابعة وإدارة الشكاوى الواردة من جروب واتساب</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="stat-card cursor-pointer hover:border-white/30" onClick={() => setStatusFilter('')}>
                    <p className="text-white/50 text-sm">الإجمالي</p>
                    <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-red-500/50" onClick={() => setStatusFilter('open')}>
                    <p className="text-red-400/70 text-sm">مفتوحة</p>
                    <p className="text-3xl font-bold text-red-400 mt-1">{stats.open}</p>
                    {stats.open > 0 && <div className="mt-2 flex gap-1">
                        {Array.from({ length: Math.min(stats.open, 5) }).map((_, i) => (
                            <AlertTriangle key={i} className="w-3 h-3 text-red-400 animate-pulse" />
                        ))}
                    </div>}
                </div>
                <div className="stat-card cursor-pointer hover:border-orange-500/50" onClick={() => setStatusFilter('escalated')}>
                    <p className="text-orange-400/70 text-sm">مُصعّدة للمدير</p>
                    <p className="text-3xl font-bold text-orange-400 mt-1">{stats.escalated}</p>
                </div>
                <div className="stat-card cursor-pointer hover:border-green-500/50" onClick={() => setStatusFilter('resolved')}>
                    <p className="text-green-400/70 text-sm">تم حلها</p>
                    <p className="text-3xl font-bold text-green-400 mt-1">{stats.resolved}</p>
                </div>
            </div>

            {/* Filter Bar */}
            <div className="flex items-center gap-3">
                <Filter className="w-5 h-5 text-white/40" />
                <div className="flex gap-2">
                    {[
                        { value: '', label: 'الكل' },
                        { value: 'open', label: '🔴 مفتوحة' },
                        { value: 'escalated', label: '🟠 مصعّدة' },
                        { value: 'resolved', label: '✅ محلولة' },
                    ].map(f => (
                        <button
                            key={f.value}
                            onClick={() => setStatusFilter(f.value)}
                            className={`px-4 py-2 rounded-lg text-sm transition-all ${statusFilter === f.value
                                    ? 'bg-gold-500/20 text-gold-400 border border-gold-500/40'
                                    : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10'
                                }`}
                        >
                            {f.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Complaints List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="text-center py-12 text-white/40">جاري التحميل...</div>
                ) : complaints.length === 0 ? (
                    <div className="text-center py-12">
                        <CheckCircle className="w-16 h-16 mx-auto text-green-500/20 mb-4" />
                        <p className="text-white/40">
                            {statusFilter ? 'لا توجد شكاوى بهذا الفلتر' : 'لا توجد شكاوى حالياً 🎉'}
                        </p>
                    </div>
                ) : (
                    complaints.map(complaint => (
                        <div
                            key={complaint.id}
                            className={`card border transition-all hover:border-gold-500/30 ${complaint.status === 'open' ? 'border-red-500/30 bg-red-500/5' :
                                    complaint.status === 'escalated' ? 'border-orange-500/30 bg-orange-500/5' :
                                        'border-white/10'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4">
                                    {/* Red Triangle Indicator */}
                                    {complaint.status === 'open' && (
                                        <div className="flex-shrink-0 mt-1">
                                            <AlertTriangle className="w-6 h-6 text-red-500 animate-pulse" />
                                        </div>
                                    )}
                                    {complaint.status === 'escalated' && (
                                        <div className="flex-shrink-0 mt-1">
                                            <AlertTriangle className="w-6 h-6 text-orange-500" />
                                        </div>
                                    )}
                                    {complaint.status === 'resolved' && (
                                        <div className="flex-shrink-0 mt-1">
                                            <CheckCircle className="w-6 h-6 text-green-500" />
                                        </div>
                                    )}

                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            {getStatusBadge(complaint.status)}
                                            <span className="text-xs text-white/30">
                                                #{complaint.id}
                                            </span>
                                        </div>

                                        <p className="text-white font-medium mb-2">{complaint.complaint_text}</p>

                                        <div className="flex flex-wrap gap-4 text-sm text-white/40">
                                            {complaint.reporter_name && (
                                                <span>👤 {complaint.reporter_name}</span>
                                            )}
                                            {complaint.reporter_phone && (
                                                <span>📱 {complaint.reporter_phone}</span>
                                            )}
                                            {complaint.created_at && (
                                                <span className="flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {new Date(complaint.created_at).toLocaleString('ar-EG', {
                                                        day: '2-digit', month: '2-digit',
                                                        hour: '2-digit', minute: '2-digit'
                                                    })}
                                                </span>
                                            )}
                                            {complaint.escalated_to_manager && (
                                                <span className="text-orange-400">📤 تم الإرسال للمدير</span>
                                            )}
                                        </div>

                                        {complaint.resolution_note && (
                                            <div className="mt-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                                                <p className="text-sm text-green-300">
                                                    <MessageSquare className="w-3 h-3 inline ml-1" />
                                                    ملاحظة الحل: {complaint.resolution_note}
                                                </p>
                                                {complaint.resolved_at && (
                                                    <p className="text-xs text-green-400/50 mt-1">
                                                        تم الحل: {new Date(complaint.resolved_at).toLocaleString('ar-EG')}
                                                    </p>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Actions */}
                                {complaint.status !== 'resolved' && (
                                    <div className="flex gap-2 flex-shrink-0">
                                        <button
                                            onClick={() => setSelectedComplaint(complaint)}
                                            className="flex items-center gap-1 px-3 py-2 rounded-lg bg-green-500/10 text-green-400 hover:bg-green-500/20 text-sm transition-colors"
                                        >
                                            <CheckCircle className="w-4 h-4" />
                                            حل
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Resolve Modal */}
            {selectedComplaint && (
                <div className="modal-2026" onClick={() => setSelectedComplaint(null)}>
                    <div className="glass-card-2026 w-full max-w-lg p-8" onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold gold-text">حل الشكوى #{selectedComplaint.id}</h3>
                            <button onClick={() => setSelectedComplaint(null)} className="text-white/40 hover:text-white">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="p-4 rounded-xl bg-white/5 border border-white/10 mb-4">
                            <p className="text-white/80">{selectedComplaint.complaint_text}</p>
                            {selectedComplaint.reporter_name && (
                                <p className="text-sm text-white/40 mt-2">من: {selectedComplaint.reporter_name}</p>
                            )}
                        </div>

                        <div className="mb-6">
                            <label className="label-2026">ملاحظة الحل (اختياري)</label>
                            <textarea
                                className="input-2026 min-h-[100px] resize-none"
                                placeholder="اكتب ملاحظة عن كيفية حل الشكوى..."
                                value={resolutionNote}
                                onChange={e => setResolutionNote(e.target.value)}
                                style={{ paddingRight: '14px' }}
                            />
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button onClick={() => setSelectedComplaint(null)} className="btn-cancel-2026">
                                إلغاء
                            </button>
                            <button onClick={() => resolveComplaint(selectedComplaint.id)} className="btn-2026">
                                <CheckCircle className="w-4 h-4 inline ml-2" />
                                تأكيد الحل
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ComplaintsPage

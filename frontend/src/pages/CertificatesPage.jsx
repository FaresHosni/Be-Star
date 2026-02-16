import { useState, useEffect } from 'react'
import {
    Award, Send, Search, ChevronUp, ChevronDown, CheckCircle, XCircle,
    Users, Trophy, Clock, MessageCircle, FileText, Star, Sparkles,
    Hash, AlertCircle
} from 'lucide-react'

const API = '/api/certificates'

function CertificatesPage() {
    const [tab, setTab] = useState('participants')
    const [participants, setParticipants] = useState([])
    const [certLogs, setCertLogs] = useState([])
    const [thankLogs, setThankLogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [sending, setSending] = useState(false)
    const [selectedIds, setSelectedIds] = useState([])
    const [sortBy, setSortBy] = useState('points')
    const [topN, setTopN] = useState('')
    const [searchQ, setSearchQ] = useState('')
    const [showThanksModal, setShowThanksModal] = useState(false)
    const [thanksMessage, setThanksMessage] = useState(
        '🌟 شكراً لك يا {name} على مشاركتك في إيفنت كن نجماً!\n\nحصلت على {points} نقطة 🏆\n\nفخورين بيك وبتميزك! ⭐'
    )
    const [sendResult, setSendResult] = useState(null)

    useEffect(() => {
        fetchData()
    }, [])

    useEffect(() => {
        if (tab === 'participants') fetchParticipants()
        else if (tab === 'cert-logs') fetchCertLogs()
        else if (tab === 'thanks-logs') fetchThankLogs()
    }, [tab, sortBy])

    const fetchData = async () => {
        setLoading(true)
        await fetchParticipants()
        setLoading(false)
    }

    const fetchParticipants = async () => {
        try {
            const res = await fetch(`${API}/participants/?sort_by=${sortBy}`)
            console.log('Certificates API status:', res.status)
            const data = await res.json()
            console.log('Certificates API data:', data)
            if (data.participants && data.participants.length > 0) {
                setParticipants(data.participants)
            } else if (data.success && data.participants) {
                setParticipants(data.participants)
            }
        } catch (e) {
            console.error('Certificates fetch error:', e)
        }
        setLoading(false)
    }

    const fetchCertLogs = async () => {
        try {
            const res = await fetch(`${API}/logs/certificates/`)
            const data = await res.json()
            setCertLogs(Array.isArray(data) ? data : [])
        } catch (e) { console.error(e) }
    }

    const fetchThankLogs = async () => {
        try {
            const res = await fetch(`${API}/logs/thanks/`)
            const data = await res.json()
            setThankLogs(Array.isArray(data) ? data : [])
        } catch (e) { console.error(e) }
    }

    const toggleSelect = (ticketId) => {
        setSelectedIds(prev =>
            prev.includes(ticketId)
                ? prev.filter(id => id !== ticketId)
                : [...prev, ticketId]
        )
    }

    const selectAll = () => {
        const filtered = getFilteredParticipants()
        if (selectedIds.length === filtered.length) {
            setSelectedIds([])
        } else {
            setSelectedIds(filtered.map(p => p.ticket_id))
        }
    }

    const selectTopN = () => {
        const n = parseInt(topN)
        if (!n || n <= 0) return
        const sorted = [...participants].sort((a, b) => b.total_points - a.total_points)
        setSelectedIds(sorted.slice(0, n).map(p => p.ticket_id))
    }

    const getFilteredParticipants = () => {
        if (!searchQ) return participants
        return participants.filter(p =>
            (p.guest_name || '').includes(searchQ) ||
            (p.phone || '').includes(searchQ)
        )
    }

    const sendCertificates = async () => {
        if (selectedIds.length === 0) return
        setSending(true)
        setSendResult(null)
        try {
            const res = await fetch(`${API}/send-certificates/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_ids: selectedIds })
            })
            const data = await res.json()
            setSendResult(data)
            if (data.success) {
                setSelectedIds([])
                fetchCertLogs()
            }
        } catch (e) {
            console.error(e)
            setSendResult({ success: false, message: 'خطأ في الاتصال بالسيرفر' })
        }
        setSending(false)
    }

    const sendThanks = async () => {
        if (selectedIds.length === 0 || !thanksMessage.trim()) return
        setSending(true)
        setSendResult(null)
        try {
            const res = await fetch(`${API}/send-thanks/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_ids: selectedIds, message: thanksMessage })
            })
            const data = await res.json()
            setSendResult(data)
            if (data.success) {
                setShowThanksModal(false)
                setSelectedIds([])
                fetchThankLogs()
            }
        } catch (e) {
            console.error(e)
            setSendResult({ success: false, message: 'خطأ في الاتصال بالسيرفر' })
        }
        setSending(false)
    }

    const getRankBadge = (rank) => {
        if (rank === 1) return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-yellow-400 to-amber-500 text-dark-500 font-bold text-sm shadow-lg shadow-yellow-500/30"><Trophy className="w-4 h-4" /> 🥇</span>
        if (rank === 2) return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-gray-300 to-gray-400 text-dark-500 font-bold text-sm shadow-lg shadow-gray-400/20">🥈</span>
        if (rank === 3) return <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-amber-600 to-amber-700 text-white font-bold text-sm shadow-lg shadow-amber-700/20">🥉</span>
        return <span className="text-white/50 text-sm font-mono">#{rank}</span>
    }

    const getStatusBadge = (status) => {
        if (status === 'sent') return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-medium border border-emerald-500/20"><CheckCircle className="w-3.5 h-3.5" /> تم الإرسال</span>
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/15 text-red-400 text-xs font-medium border border-red-500/20"><XCircle className="w-3.5 h-3.5" /> فشل</span>
    }

    const formatDate = (iso) => {
        if (!iso) return '-'
        const d = new Date(iso)
        return d.toLocaleDateString('ar-EG', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    }

    const filtered = getFilteredParticipants()

    const tabs = [
        { key: 'participants', icon: Users, label: 'تحليل المشاركين', emoji: '📊' },
        { key: 'cert-logs', icon: FileText, label: 'سجل الشهادات', emoji: '📜' },
        { key: 'thanks-logs', icon: MessageCircle, label: 'سجل الشكر', emoji: '💌' },
    ]

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Hero Header */}
            <div className="relative overflow-hidden rounded-2xl border border-gold-500/20" style={{
                background: 'linear-gradient(135deg, rgba(212,175,55,0.12) 0%, rgba(10,10,10,0.95) 50%, rgba(212,175,55,0.08) 100%)'
            }}>
                <div className="absolute inset-0 opacity-5">
                    <div className="absolute top-4 left-10 text-6xl">⭐</div>
                    <div className="absolute top-8 right-20 text-4xl">🏆</div>
                    <div className="absolute bottom-4 left-1/3 text-5xl">📜</div>
                    <div className="absolute bottom-6 right-10 text-3xl">✨</div>
                </div>

                <div className="relative p-8 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gold-500 to-amber-600 flex items-center justify-center shadow-xl shadow-gold-500/25 ring-2 ring-gold-500/30">
                            <Award className="w-9 h-9 text-dark-500" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold gold-text tracking-tight">الشهادات ورسائل الشكر</h1>
                            <p className="text-white/50 mt-1 text-sm">إرسال شهادات تقدير ورسائل شكر للمشاركين عبر واتساب</p>
                        </div>
                    </div>

                    {/* Stats Pills */}
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-dark-400/80 border border-gold-500/10">
                            <Users className="w-4 h-4 text-gold-400" />
                            <span className="text-gold-400 font-bold text-lg">{participants.length}</span>
                            <span className="text-white/40 text-xs">مشارك</span>
                        </div>
                        <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-dark-400/80 border border-gold-500/10">
                            <CheckCircle className="w-4 h-4 text-emerald-400" />
                            <span className="text-emerald-400 font-bold text-lg">{selectedIds.length}</span>
                            <span className="text-white/40 text-xs">محدد</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2">
                {tabs.map(t => (
                    <button key={t.key} onClick={() => setTab(t.key)}
                        className={`flex items-center gap-2.5 px-5 py-3 rounded-xl font-medium text-sm transition-all duration-300 ${tab === t.key
                            ? 'bg-gradient-to-r from-gold-500/20 to-gold-500/5 text-gold-400 border border-gold-500/30 shadow-lg shadow-gold-500/10'
                            : 'text-white/40 hover:text-white/60 border border-transparent hover:border-white/10 hover:bg-white/5'
                            }`}>
                        <span className="text-base">{t.emoji}</span>
                        <t.icon className="w-4 h-4" />
                        {t.label}
                    </button>
                ))}
            </div>

            {/* Send Result Alert */}
            {sendResult && (
                <div className={`flex items-center gap-3 p-4 rounded-xl border animate-fade-in ${sendResult.success
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/10 border-red-500/20 text-red-400'
                    }`}>
                    {sendResult.success ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    <span className="font-medium">{sendResult.message}</span>
                    <button onClick={() => setSendResult(null)} className="mr-auto text-white/30 hover:text-white/60">✕</button>
                </div>
            )}

            {/* ═══════ TAB 1: Participants ═══════ */}
            {tab === 'participants' && (
                <div className="space-y-4">
                    {/* Toolbar */}
                    <div className="flex items-center gap-3 flex-wrap">
                        {/* Search */}
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                            <input
                                value={searchQ} onChange={e => setSearchQ(e.target.value)}
                                placeholder="بحث بالاسم أو الرقم..."
                                className="input-gold w-full pr-10"
                            />
                        </div>

                        {/* Top N selector */}
                        <div className="flex items-center gap-2">
                            <label className="text-white/40 text-sm whitespace-nowrap">أعلى</label>
                            <input
                                type="number" min="1" value={topN}
                                onChange={e => setTopN(e.target.value)}
                                placeholder="5"
                                className="input-gold w-16 text-center"
                            />
                            <button onClick={selectTopN}
                                className="px-3 py-2 rounded-lg bg-gold-500/10 text-gold-400 hover:bg-gold-500/20 border border-gold-500/20 text-sm font-medium transition-colors">
                                تحديد
                            </button>
                        </div>

                        {/* Sort buttons */}
                        <div className="flex items-center gap-1 bg-dark-400 rounded-xl p-1 border border-white/5">
                            {[
                                { key: 'points', label: 'النقاط', icon: Trophy },
                                { key: 'name', label: 'الاسم', icon: Users },
                                { key: 'answers', label: 'الإجابات', icon: Hash },
                            ].map(s => (
                                <button key={s.key} onClick={() => setSortBy(s.key)}
                                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${sortBy === s.key
                                        ? 'bg-gold-500/20 text-gold-400'
                                        : 'text-white/30 hover:text-white/50'
                                        }`}>
                                    <s.icon className="w-3.5 h-3.5" />
                                    {s.label}
                                </button>
                            ))}
                        </div>

                        {/* Select all */}
                        <button onClick={selectAll}
                            className="px-3 py-2 rounded-lg bg-white/5 text-white/40 hover:text-white/60 text-sm border border-white/5 hover:border-white/10 transition-colors">
                            {selectedIds.length === filtered.length && filtered.length > 0 ? 'إلغاء الكل' : 'تحديد الكل'}
                        </button>
                    </div>

                    {/* Action buttons */}
                    {selectedIds.length > 0 && (
                        <div className="flex items-center gap-3 p-4 rounded-xl bg-gold-500/5 border border-gold-500/15 animate-fade-in">
                            <Sparkles className="w-5 h-5 text-gold-400" />
                            <span className="text-gold-300 text-sm font-medium">تم تحديد {selectedIds.length} مشارك</span>
                            <div className="mr-auto flex gap-2">
                                <button onClick={sendCertificates} disabled={sending}
                                    className="btn-gold flex items-center gap-2 text-sm px-5 py-2.5 shadow-lg shadow-gold-500/20">
                                    {sending ? <Clock className="w-4 h-4 animate-spin" /> : <Award className="w-4 h-4" />}
                                    إرسال شهادة 📜
                                </button>
                                <button onClick={() => setShowThanksModal(true)} disabled={sending}
                                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-pink-500/20 to-purple-500/20 text-pink-300 hover:from-pink-500/30 hover:to-purple-500/30 border border-pink-500/20 text-sm font-medium transition-all">
                                    {sending ? <Clock className="w-4 h-4 animate-spin" /> : <MessageCircle className="w-4 h-4" />}
                                    إرسال شكر 💌
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Participants Table */}
                    <div className="card-dark overflow-hidden">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/5">
                                    <th className="text-right p-4 text-white/30 text-xs font-medium w-10"></th>
                                    <th className="text-right p-4 text-white/30 text-xs font-medium w-16">المركز</th>
                                    <th className="text-right p-4 text-white/30 text-xs font-medium">الاسم</th>
                                    <th className="text-right p-4 text-white/30 text-xs font-medium">الهاتف</th>
                                    <th className="text-center p-4 text-white/30 text-xs font-medium">النقاط</th>
                                    <th className="text-center p-4 text-white/30 text-xs font-medium">الإجابات</th>
                                    <th className="text-center p-4 text-white/30 text-xs font-medium">الصحيحة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="7" className="text-center py-12 text-white/30">
                                        <Clock className="w-6 h-6 animate-spin mx-auto mb-2" /> جاري التحميل...
                                    </td></tr>
                                ) : filtered.length === 0 ? (
                                    <tr><td colSpan="7" className="text-center py-12 text-white/30">
                                        <Users className="w-8 h-8 mx-auto mb-3 opacity-30" />
                                        لا يوجد مشاركين
                                    </td></tr>
                                ) : filtered.map((p, i) => (
                                    <tr key={p.ticket_id}
                                        onClick={() => toggleSelect(p.ticket_id)}
                                        className={`border-b border-white/5 cursor-pointer transition-all duration-200 ${selectedIds.includes(p.ticket_id)
                                            ? 'bg-gold-500/10 hover:bg-gold-500/15'
                                            : 'hover:bg-white/5'
                                            } ${p.rank <= 3 ? 'relative' : ''}`}
                                    >
                                        <td className="p-4">
                                            <div className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${selectedIds.includes(p.ticket_id)
                                                ? 'border-gold-400 bg-gold-500'
                                                : 'border-white/20 hover:border-white/40'
                                                }`}>
                                                {selectedIds.includes(p.ticket_id) && (
                                                    <CheckCircle className="w-3.5 h-3.5 text-dark-500" />
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4">{getRankBadge(p.rank)}</td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold ${p.rank === 1 ? 'bg-gradient-to-br from-yellow-400 to-amber-500 text-dark-500' :
                                                    p.rank === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-dark-500' :
                                                        p.rank === 3 ? 'bg-gradient-to-br from-amber-600 to-amber-700 text-white' :
                                                            'bg-dark-300 text-white/50'
                                                    }`}>
                                                    {(p.guest_name || '?')[0]}
                                                </div>
                                                <span className="text-white font-medium">{p.guest_name}</span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-white/40 text-sm font-mono">{p.phone}</td>
                                        <td className="p-4 text-center">
                                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-sm font-bold ${p.rank === 1 ? 'bg-yellow-500/15 text-yellow-400' :
                                                p.rank <= 3 ? 'bg-gold-500/15 text-gold-400' :
                                                    'bg-white/5 text-white/70'
                                                }`}>
                                                <Star className="w-3.5 h-3.5" />
                                                {p.total_points}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center text-white/40 text-sm">{p.total_answers}</td>
                                        <td className="p-4 text-center">
                                            <span className="text-emerald-400 text-sm font-medium">{p.correct_answers}</span>
                                            <span className="text-white/20 text-xs mx-1">/</span>
                                            <span className="text-white/30 text-xs">{p.total_answers}</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* ═══════ TAB 2: Certificate Logs ═══════ */}
            {tab === 'cert-logs' && (
                <div className="card-dark overflow-hidden">
                    <div className="p-4 border-b border-white/5 flex items-center gap-3">
                        <FileText className="w-5 h-5 text-gold-400" />
                        <h3 className="text-white font-medium">سجل الشهادات المُرسلة</h3>
                        <span className="text-white/30 text-xs mr-auto">{certLogs.length} سجل</span>
                    </div>
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/5">
                                <th className="text-right p-4 text-white/30 text-xs font-medium">الاسم</th>
                                <th className="text-right p-4 text-white/30 text-xs font-medium">الهاتف</th>
                                <th className="text-center p-4 text-white/30 text-xs font-medium">النقاط</th>
                                <th className="text-center p-4 text-white/30 text-xs font-medium">المركز</th>
                                <th className="text-center p-4 text-white/30 text-xs font-medium">الحالة</th>
                                <th className="text-right p-4 text-white/30 text-xs font-medium">التاريخ</th>
                            </tr>
                        </thead>
                        <tbody>
                            {certLogs.length === 0 ? (
                                <tr><td colSpan="6" className="text-center py-12 text-white/30">
                                    <FileText className="w-8 h-8 mx-auto mb-3 opacity-30" />
                                    لم يتم إرسال شهادات بعد
                                </td></tr>
                            ) : certLogs.map(log => (
                                <tr key={log.id} className="border-b border-white/5 hover:bg-white/5">
                                    <td className="p-4 text-white font-medium">{log.guest_name}</td>
                                    <td className="p-4 text-white/40 text-sm font-mono">{log.phone}</td>
                                    <td className="p-4 text-center">
                                        <span className="text-gold-400 font-bold">{log.total_points}</span>
                                    </td>
                                    <td className="p-4 text-center">{getRankBadge(log.rank)}</td>
                                    <td className="p-4 text-center">{getStatusBadge(log.status)}</td>
                                    <td className="p-4 text-white/30 text-xs">{formatDate(log.sent_at)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* ═══════ TAB 3: Thanks Logs ═══════ */}
            {tab === 'thanks-logs' && (
                <div className="card-dark overflow-hidden">
                    <div className="p-4 border-b border-white/5 flex items-center gap-3">
                        <MessageCircle className="w-5 h-5 text-pink-400" />
                        <h3 className="text-white font-medium">سجل رسائل الشكر</h3>
                        <span className="text-white/30 text-xs mr-auto">{thankLogs.length} سجل</span>
                    </div>
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/5">
                                <th className="text-right p-4 text-white/30 text-xs font-medium">الاسم</th>
                                <th className="text-right p-4 text-white/30 text-xs font-medium">الهاتف</th>
                                <th className="text-right p-4 text-white/30 text-xs font-medium">الرسالة</th>
                                <th className="text-center p-4 text-white/30 text-xs font-medium">الحالة</th>
                                <th className="text-right p-4 text-white/30 text-xs font-medium">التاريخ</th>
                            </tr>
                        </thead>
                        <tbody>
                            {thankLogs.length === 0 ? (
                                <tr><td colSpan="5" className="text-center py-12 text-white/30">
                                    <MessageCircle className="w-8 h-8 mx-auto mb-3 opacity-30" />
                                    لم يتم إرسال رسائل شكر بعد
                                </td></tr>
                            ) : thankLogs.map(log => (
                                <tr key={log.id} className="border-b border-white/5 hover:bg-white/5">
                                    <td className="p-4 text-white font-medium">{log.guest_name}</td>
                                    <td className="p-4 text-white/40 text-sm font-mono">{log.phone}</td>
                                    <td className="p-4 text-white/50 text-sm max-w-xs truncate">{log.message_text}</td>
                                    <td className="p-4 text-center">{getStatusBadge(log.status)}</td>
                                    <td className="p-4 text-white/30 text-xs">{formatDate(log.sent_at)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* ═══════ Thanks Modal ═══════ */}
            {showThanksModal && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
                    <div className="bg-dark-400 rounded-2xl p-6 w-full max-w-lg border border-gold-500/20 shadow-2xl shadow-gold-500/10 animate-fade-in">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-pink-500/20 to-purple-500/20 flex items-center justify-center">
                                    <MessageCircle className="w-5 h-5 text-pink-400" />
                                </div>
                                <h3 className="text-xl font-bold text-pink-300">رسالة شكر 💌</h3>
                            </div>
                            <button onClick={() => setShowThanksModal(false)}
                                className="text-white/40 hover:text-white text-xl">✕</button>
                        </div>

                        <div className="mb-4 p-3 rounded-xl bg-dark-300/50 border border-white/5">
                            <p className="text-white/40 text-xs mb-2">المتغيرات المتاحة:</p>
                            <div className="flex flex-wrap gap-2">
                                {['{name}', '{points}', '{rank}'].map(v => (
                                    <code key={v} className="px-2 py-1 rounded-md bg-gold-500/10 text-gold-400 text-xs border border-gold-500/20">{v}</code>
                                ))}
                            </div>
                        </div>

                        <textarea
                            value={thanksMessage}
                            onChange={e => setThanksMessage(e.target.value)}
                            rows={6}
                            className="input-gold w-full mb-4 resize-none"
                            dir="rtl"
                            placeholder="اكتب رسالة الشكر هنا..."
                        />

                        <div className="flex items-center gap-3">
                            <span className="text-white/30 text-xs">سيتم إرسالها لـ {selectedIds.length} مشارك</span>
                            <button onClick={sendThanks} disabled={sending || !thanksMessage.trim()}
                                className="btn-gold mr-auto flex items-center gap-2 px-6">
                                {sending ? <Clock className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                إرسال
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default CertificatesPage

import { useState, useEffect } from 'react'
import { apiFetch } from '../utils/api'
import {
    HelpCircle, Users, Trophy, ClipboardList, Plus, Send, Trash2, Clock,
    CheckCircle, XCircle, ChevronDown, ChevronUp, Search, Timer, Award, X,
    BarChart3, Target, UserPlus, Edit2
} from 'lucide-react'

const API = '/api/quiz'

export default function QuizEngine() {
    const [activeTab, setActiveTab] = useState('questions')
    const [questions, setQuestions] = useState([])
    const [groups, setGroups] = useState([])
    const [leaderboard, setLeaderboard] = useState([])
    const [attendees, setAttendees] = useState([])
    const [loading, setLoading] = useState(false)

    // Modals
    const [showCreateQ, setShowCreateQ] = useState(false)
    const [showCreateGroup, setShowCreateGroup] = useState(false)
    const [editingGroup, setEditingGroup] = useState(null)
    const [showAnswers, setShowAnswers] = useState(null) // question_id
    const [answersData, setAnswersData] = useState(null)

    // Leaderboard filter
    const [lbFilter, setLbFilter] = useState('all')

    // Question form
    const [qForm, setQForm] = useState({
        text: '', question_type: 'mcq', correct_answer: '', points: '',
        time_limit_seconds: '', time_unit: 'seconds', target_groups: ['all'], accept_late: false,
        correct_answers: [''],
        options: [
            { label: 'A', text: '', is_correct: true },
            { label: 'B', text: '', is_correct: false },
            { label: 'C', text: '', is_correct: false },
            { label: 'D', text: '', is_correct: false },
        ]
    })

    // Group form
    const [gForm, setGForm] = useState({ name: '', description: '', ticket_ids: [] })
    const [gSearch, setGSearch] = useState('')

    useEffect(() => {
        fetchQuestions()
        fetchGroups()
        fetchAttendees()
    }, [])

    useEffect(() => {
        if (activeTab === 'leaderboard') fetchLeaderboard()
    }, [activeTab, lbFilter])

    // ═══════ Data Fetching ═══════

    const fetchQuestions = async () => {
        try {
            const res = await apiFetch(`${API}/questions`)
            const data = await res.json()
            setQuestions(data.questions || [])
        } catch (e) { console.error(e) }
    }

    const fetchGroups = async () => {
        try {
            const res = await apiFetch(`${API}/groups`)
            const data = await res.json()
            setGroups(data.groups || [])
        } catch (e) { console.error(e) }
    }

    const fetchLeaderboard = async () => {
        try {
            const url = lbFilter === 'all' ? `${API}/leaderboard` : `${API}/leaderboard?group=${lbFilter}`
            const res = await apiFetch(url)
            const data = await res.json()
            setLeaderboard(data.leaderboard || [])
        } catch (e) { console.error(e) }
    }

    const fetchAttendees = async () => {
        try {
            const res = await apiFetch('/api/engagement/attendees')
            const data = await res.json()
            setAttendees(data.attendees || [])
        } catch (e) { console.error(e) }
    }

    const fetchAnswers = async (qid) => {
        try {
            const res = await apiFetch(`${API}/answers/${qid}`)
            const data = await res.json()
            setAnswersData(data)
            setShowAnswers(qid)
        } catch (e) { console.error(e) }
    }

    // ═══════ Actions ═══════

    const createQuestion = async () => {
        setLoading(true)
        try {
            // Validate MCQ has a correct answer selected
            if (qForm.question_type === 'mcq' && !qForm.correct_answer) {
                alert('يجب اختيار الإجابة الصحيحة (اضغط على الحرف A/B/C/D)')
                setLoading(false)
                return
            }
            const payload = { ...qForm }
            if (qForm.question_type === 'completion') {
                delete payload.options
                // Join multiple correct answers with ||
                payload.correct_answer = qForm.correct_answers.filter(a => a.trim()).join('||')
            }
            delete payload.correct_answers
            delete payload.time_unit
            // Convert time based on unit
            const timeVal = parseInt(qForm.time_limit_seconds) || 60
            if (qForm.time_unit === 'minutes') payload.time_limit_seconds = timeVal * 60
            else if (qForm.time_unit === 'hours') payload.time_limit_seconds = timeVal * 3600
            else payload.time_limit_seconds = timeVal
            // Default points if empty
            if (!payload.points) payload.points = 1
            const res = await apiFetch(`${API}/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            const data = await res.json()
            if (data.success) {
                setShowCreateQ(false)
                resetQForm()
                fetchQuestions()
            }
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    const sendQuestion = async (qid) => {
        if (!confirm('هل أنت متأكد من إرسال السؤال؟')) return
        try {
            const res = await apiFetch(`${API}/questions/${qid}/send`, { method: 'POST' })
            const data = await res.json()
            if (!res.ok) {
                alert(data.detail || 'حدث خطأ أثناء الإرسال')
            } else {
                alert(data.message)
                fetchQuestions()
            }
        } catch (e) {
            console.error(e)
            alert('خطأ في الاتصال بالسيرفر')
        }
    }

    const expireQuestion = async (qid) => {
        try {
            await apiFetch(`${API}/questions/${qid}/expire`, { method: 'POST' })
            fetchQuestions()
        } catch (e) { console.error(e) }
    }

    const deleteQuestion = async (qid) => {
        if (!confirm('حذف السؤال نهائياً؟')) return
        try {
            await apiFetch(`${API}/questions/${qid}`, { method: 'DELETE' })
            fetchQuestions()
        } catch (e) { console.error(e) }
    }

    const createGroup = async () => {
        setLoading(true)
        try {
            const isEdit = !!editingGroup
            const url = isEdit ? `${API}/groups/${editingGroup.id}` : `${API}/groups`
            const method = isEdit ? 'PUT' : 'POST'
            const res = await apiFetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(gForm)
            })
            const data = await res.json()
            if (data.success) {
                setShowCreateGroup(false)
                setEditingGroup(null)
                setGForm({ name: '', description: '', ticket_ids: [] })
                fetchGroups()
            }
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    const deleteGroup = async (gid) => {
        if (!confirm('حذف المجموعة؟')) return
        try {
            await apiFetch(`${API}/groups/${gid}`, { method: 'DELETE' })
            fetchGroups()
        } catch (e) { console.error(e) }
    }

    const resetQForm = () => {
        setQForm({
            text: '', question_type: 'mcq', correct_answer: '', points: '',
            time_limit_seconds: '', time_unit: 'seconds', target_groups: ['all'], accept_late: false,
            correct_answers: [''],
            options: [
                { label: 'A', text: '', is_correct: true },
                { label: 'B', text: '', is_correct: false },
                { label: 'C', text: '', is_correct: false },
                { label: 'D', text: '', is_correct: false },
            ]
        })
    }

    // ═══════ Helpers ═══════

    const statusBadge = (status) => {
        const styles = {
            draft: 'bg-white/10 text-white/50',
            active: 'bg-green-500/20 text-green-400 animate-pulse',
            expired: 'bg-red-500/20 text-red-400',
        }
        const labels = { draft: 'مسودة', active: '🔴 نشط', expired: 'منتهي' }
        return <span className={`px-3 py-1 rounded-full text-xs font-bold ${styles[status] || ''}`}>{labels[status] || status}</span>
    }

    const typeBadge = (type) => {
        if (type === 'mcq') return <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs">اختيار متعدد</span>
        return <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 text-xs">إكمال</span>
    }

    const rankBadge = (rank) => {
        if (rank === 1) return <span className="text-2xl">🥇</span>
        if (rank === 2) return <span className="text-2xl">🥈</span>
        if (rank === 3) return <span className="text-2xl">🥉</span>
        return <span className="text-white/40 font-mono">#{rank}</span>
    }

    const tabs = [
        { id: 'questions', label: 'الأسئلة', icon: HelpCircle },
        { id: 'groups', label: 'المجموعات', icon: Users },
        { id: 'leaderboard', label: 'الترتيب', icon: Trophy },
        { id: 'answers_log', label: 'سجل الإجابات', icon: ClipboardList },
    ]

    // ═══════════════════════════════════════════
    //  RENDER
    // ═══════════════════════════════════════════

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gold-400 flex items-center gap-3">
                        <Target className="w-8 h-8" /> المسابقات والتفاعل
                    </h1>
                    <p className="text-white/50 mt-1">إدارة الأسئلة وتقييم الإجابات والنتائج</p>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mb-6 border-b border-white/10 pb-2">
                {tabs.map(t => (
                    <button key={t.id} onClick={() => setActiveTab(t.id)}
                        className={`flex items-center gap-2 px-5 py-3 rounded-t-xl text-sm font-medium transition-all ${activeTab === t.id
                            ? 'bg-gold-500/15 text-gold-400 border-b-2 border-gold-500'
                            : 'text-white/50 hover:text-white/70 hover:bg-white/5'
                            }`}>
                        <t.icon className="w-4 h-4" /> {t.label}
                    </button>
                ))}
            </div>

            {/* ═══════ TAB: Questions ═══════ */}
            {activeTab === 'questions' && (
                <div>
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-white/80">قائمة الأسئلة ({questions.length})</h2>
                        <button onClick={() => setShowCreateQ(true)}
                            className="btn-gold flex items-center gap-2">
                            <Plus className="w-4 h-4" /> سؤال جديد
                        </button>
                    </div>

                    {questions.length === 0 ? (
                        <div className="card text-center py-16">
                            <HelpCircle className="w-16 h-16 text-white/20 mx-auto mb-4" />
                            <p className="text-white/50">لا يوجد أسئلة بعد</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {questions.map(q => (
                                <div key={q.id} className="card">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                {statusBadge(q.status)}
                                                {typeBadge(q.question_type)}
                                                <span className="text-white/30 text-xs">#{q.id}</span>
                                            </div>
                                            <p className="text-white font-medium text-base mb-2">{q.text}</p>
                                            <div className="flex items-center gap-4 text-xs text-white/40">
                                                <span className="flex items-center gap-1"><Award className="w-3 h-3" /> {q.points} نقطة</span>
                                                <span className="flex items-center gap-1"><Timer className="w-3 h-3" /> {q.time_limit_seconds} ثانية</span>
                                                <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3" /> {q.correct_count}/{q.answer_count} صح</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {q.status === 'draft' && (
                                                <>
                                                    <button onClick={() => sendQuestion(q.id)}
                                                        className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                                                        title="إرسال">
                                                        <Send className="w-4 h-4" />
                                                    </button>
                                                    <button onClick={() => deleteQuestion(q.id)}
                                                        className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                                        title="حذف">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </>
                                            )}
                                            {q.status === 'active' && (
                                                <button onClick={() => expireQuestion(q.id)}
                                                    className="p-2 rounded-lg bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 transition-colors"
                                                    title="إنهاء">
                                                    <Clock className="w-4 h-4" />
                                                </button>
                                            )}
                                            <button onClick={() => fetchAnswers(q.id)}
                                                className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors"
                                                title="عرض الإجابات">
                                                <BarChart3 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>

                                    {/* MCQ Options Preview */}
                                    {q.question_type === 'mcq' && q.options?.length > 0 && (
                                        <div className="mt-3 grid grid-cols-2 gap-2">
                                            {q.options.map(opt => (
                                                <div key={opt.label}
                                                    className={`px-3 py-2 rounded-lg text-sm ${opt.is_correct
                                                        ? 'bg-green-500/15 text-green-400 border border-green-500/30'
                                                        : 'bg-white/5 text-white/60 border border-white/10'
                                                        }`}>
                                                    <span className="font-bold ml-2">{opt.label})</span> {opt.text}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Completion answer */}
                                    {q.question_type === 'completion' && (
                                        <div className="mt-3 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400/80 text-sm">
                                            ✅ الإجابة الصحيحة: {q.correct_answer}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* ═══════ TAB: Groups ═══════ */}
            {activeTab === 'groups' && (
                <div>
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-white/80">المجموعات المخصصة ({groups.length})</h2>
                        <button onClick={() => setShowCreateGroup(true)}
                            className="btn-gold flex items-center gap-2">
                            <Plus className="w-4 h-4" /> مجموعة جديدة
                        </button>
                    </div>

                    {/* Built-in groups */}
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="card border border-yellow-500/20">
                            <div className="flex items-center justify-between">
                                <span className="text-yellow-400 font-bold">⭐ VIP</span>
                                <span className="text-white/40 text-sm">
                                    {attendees.filter(a => a.ticket_type === 'VIP').length} عضو
                                </span>
                            </div>
                            <p className="text-white/40 text-xs mt-1">مجموعة تلقائية</p>
                        </div>
                        <div className="card border border-blue-500/20">
                            <div className="flex items-center justify-between">
                                <span className="text-blue-400 font-bold">🎓 طلبة</span>
                                <span className="text-white/40 text-sm">
                                    {attendees.filter(a => a.ticket_type === 'Student').length} عضو
                                </span>
                            </div>
                            <p className="text-white/40 text-xs mt-1">مجموعة تلقائية</p>
                        </div>
                    </div>

                    {/* Custom groups */}
                    {groups.length === 0 ? (
                        <div className="card text-center py-12 mt-4">
                            <Users className="w-12 h-12 text-white/20 mx-auto mb-3" />
                            <p className="text-white/50">لا يوجد مجموعات مخصصة</p>
                        </div>
                    ) : (
                        <div className="space-y-3 mt-4">
                            {groups.map(g => (
                                <div key={g.id} className="card">
                                    <div className="flex items-center justify-between mb-2">
                                        <div>
                                            <h3 className="text-white font-semibold">{g.name}</h3>
                                            {g.description && <p className="text-white/40 text-xs">{g.description}</p>}
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-white/40 text-sm">{g.member_count} عضو</span>
                                            <button onClick={() => {
                                                setEditingGroup(g)
                                                setGForm({
                                                    name: g.name,
                                                    description: g.description || '',
                                                    ticket_ids: g.members?.map(m => m.ticket_id) || []
                                                })
                                                setShowCreateGroup(true)
                                            }}
                                                className="p-2 rounded-lg bg-gold-500/20 text-gold-400 hover:bg-gold-500/30 transition-colors">
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                            <button onClick={() => deleteGroup(g.id)}
                                                className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors">
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                    {g.members?.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {g.members.map(m => (
                                                <span key={m.ticket_id}
                                                    className="px-2 py-1 rounded-lg bg-white/5 text-white/60 text-xs">
                                                    {m.guest_name}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* ═══════ TAB: Leaderboard ═══════ */}
            {activeTab === 'leaderboard' && (
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-white/80">ترتيب المشاركين</h2>
                        <div className="flex items-center gap-2">
                            <span className="text-white/40 text-sm">تصفية:</span>
                            {['all', 'VIP', 'Student', ...groups.map(g => `group:${g.id}`)].map(f => (
                                <button key={f} onClick={() => setLbFilter(f)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${lbFilter === f
                                        ? 'bg-gold-500/20 text-gold-400 border border-gold-500/30'
                                        : 'bg-white/5 text-white/50 hover:text-white/70'
                                        }`}>
                                    {f === 'all' ? 'الكل' : f.startsWith('group:') ? groups.find(g => `group:${g.id}` === f)?.name : f}
                                </button>
                            ))}
                        </div>
                    </div>

                    {leaderboard.length === 0 ? (
                        <div className="card text-center py-16">
                            <Trophy className="w-16 h-16 text-white/20 mx-auto mb-4" />
                            <p className="text-white/50">لا توجد نتائج بعد</p>
                        </div>
                    ) : (
                        <table className="table-gold">
                            <thead>
                                <tr>
                                    <th>المركز</th>
                                    <th>الاسم</th>
                                    <th>رقم الواتساب</th>
                                    <th>النوع</th>
                                    <th>الإجابات</th>
                                    <th>الصحيحة</th>
                                    <th>النقاط</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaderboard.map(p => (
                                    <tr key={p.ticket_id} className={p.rank <= 3 ? 'bg-gold-500/5' : ''}>
                                        <td className="text-center">{rankBadge(p.rank)}</td>
                                        <td className="font-semibold">{p.guest_name}</td>
                                        <td className="text-white/50 text-sm" dir="ltr">{p.phone}</td>
                                        <td>
                                            {p.ticket_type === 'VIP'
                                                ? <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs">VIP</span>
                                                : <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs">Student</span>
                                            }
                                        </td>
                                        <td className="text-white/60">{p.total_answers}</td>
                                        <td className="text-green-400">{p.correct_answers}</td>
                                        <td>
                                            <span className="text-gold-400 font-bold text-lg">{p.total_points}</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {/* ═══════ TAB: Answers Log ═══════ */}
            {activeTab === 'answers_log' && (
                <div>
                    <h2 className="text-lg font-semibold text-white/80 mb-4">سجل الإجابات لكل سؤال</h2>
                    {questions.length === 0 ? (
                        <div className="card text-center py-16">
                            <ClipboardList className="w-16 h-16 text-white/20 mx-auto mb-4" />
                            <p className="text-white/50">لا يوجد أسئلة</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {questions.filter(q => q.answer_count > 0).map(q => (
                                <div key={q.id} className="card cursor-pointer hover:border-gold-500/30 transition-all"
                                    onClick={() => fetchAnswers(q.id)}>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-white font-medium">{q.text}</p>
                                            <div className="flex items-center gap-3 mt-1 text-xs text-white/40">
                                                {typeBadge(q.question_type)}
                                                <span>{q.answer_count} إجابة</span>
                                                <span className="text-green-400">{q.correct_count} صح</span>
                                                <span className="text-red-400">{q.answer_count - q.correct_count} خطأ</span>
                                            </div>
                                        </div>
                                        <BarChart3 className="w-5 h-5 text-white/30" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* ═══════ MODAL: Create Question ═══════ */}
            {showCreateQ && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-400 rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto border border-gold-500/20">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-gold-400">سؤال جديد</h3>
                            <button onClick={() => { setShowCreateQ(false); resetQForm() }}
                                className="text-white/40 hover:text-white"><X className="w-5 h-5" /></button>
                        </div>

                        {/* Question Type */}
                        <div className="flex gap-2 mb-4">
                            {['mcq', 'completion'].map(t => (
                                <button key={t}
                                    onClick={() => setQForm({ ...qForm, question_type: t })}
                                    className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all ${qForm.question_type === t
                                        ? 'bg-gold-500/20 text-gold-400 border border-gold-500/30'
                                        : 'bg-white/5 text-white/50 border border-white/10'
                                        }`}>
                                    {t === 'mcq' ? '📋 اختيار من متعدد' : '✍️ إكمال'}
                                </button>
                            ))}
                        </div>

                        {/* Question Text */}
                        <label className="block text-white/60 text-sm mb-1">نص السؤال</label>
                        <textarea value={qForm.text}
                            onChange={e => setQForm({ ...qForm, text: e.target.value })}
                            className="input-gold w-full mb-4 h-20 resize-none"
                            placeholder="اكتب السؤال هنا..."
                        />

                        {/* MCQ Options */}
                        {qForm.question_type === 'mcq' && (
                            <div className="mb-4">
                                <label className="block text-white/60 text-sm mb-2">الخيارات</label>
                                {qForm.options.map((opt, i) => (
                                    <div key={opt.label} className="flex items-center gap-2 mb-2">
                                        <button onClick={() => {
                                            const newOpts = qForm.options.map((o, j) => ({
                                                ...o, is_correct: j === i
                                            }))
                                            setQForm({ ...qForm, options: newOpts, correct_answer: opt.label })
                                        }}
                                            className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${opt.is_correct
                                                ? 'bg-green-500/30 text-green-400 border border-green-500'
                                                : 'bg-white/10 text-white/50 border border-white/20'
                                                }`}>
                                            {opt.label}
                                        </button>
                                        <input value={opt.text}
                                            onChange={e => {
                                                const newOpts = [...qForm.options]
                                                newOpts[i] = { ...newOpts[i], text: e.target.value }
                                                setQForm({ ...qForm, options: newOpts })
                                            }}
                                            className="input-gold flex-1"
                                            placeholder={`خيار ${opt.label}`}
                                        />
                                    </div>
                                ))}
                                <p className="text-white/30 text-xs mt-1">اضغط على الحرف لتحديد الإجابة الصحيحة</p>
                            </div>
                        )}

                        {/* Completion Answers (multiple) */}
                        {qForm.question_type === 'completion' && (
                            <div className="mb-4">
                                <label className="block text-white/60 text-sm mb-2">الإجابات الصحيحة</label>
                                {qForm.correct_answers.map((ans, i) => (
                                    <div key={i} className="flex items-center gap-2 mb-2">
                                        <span className="text-gold-400 text-sm font-bold w-6">{i + 1}.</span>
                                        <input value={ans}
                                            onChange={e => {
                                                const newAnswers = [...qForm.correct_answers]
                                                newAnswers[i] = e.target.value
                                                setQForm({ ...qForm, correct_answers: newAnswers })
                                            }}
                                            className="input-gold flex-1"
                                            placeholder={`الإجابة الصحيحة ${i + 1}...`}
                                        />
                                        {qForm.correct_answers.length > 1 && (
                                            <button onClick={() => {
                                                const newAnswers = qForm.correct_answers.filter((_, j) => j !== i)
                                                setQForm({ ...qForm, correct_answers: newAnswers })
                                            }}
                                                className="text-red-400 hover:text-red-300 text-lg px-1">×</button>
                                        )}
                                    </div>
                                ))}
                                <button onClick={() => setQForm({ ...qForm, correct_answers: [...qForm.correct_answers, ''] })}
                                    className="text-gold-400 hover:text-gold-300 text-sm flex items-center gap-1 mt-1">
                                    + إضافة إجابة صحيحة أخرى
                                </button>
                                <p className="text-white/30 text-xs mt-2">الإجابات المقاربة (90%+ تشابه) مع أي إجابة صحيحة تُحتسب صحيحة</p>
                            </div>
                        )}

                        {/* Points & Time */}
                        <div className="grid grid-cols-2 gap-3 mb-4">
                            <div>
                                <label className="block text-white/60 text-sm mb-1">النقاط</label>
                                <input type="number" value={qForm.points} min={1}
                                    onChange={e => setQForm({ ...qForm, points: e.target.value })}
                                    className="input-gold w-full"
                                    placeholder="1"
                                />
                            </div>
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <label className="text-white/60 text-sm">المدة</label>
                                    <div className="flex gap-1">
                                        {[{ v: 'seconds', l: 'ثانية' }, { v: 'minutes', l: 'دقيقة' }, { v: 'hours', l: 'ساعة' }].map(u => (
                                            <button key={u.v}
                                                onClick={() => setQForm({ ...qForm, time_unit: u.v })}
                                                className={`px-2 py-0.5 rounded text-[10px] transition-all ${qForm.time_unit === u.v
                                                    ? 'bg-gold-500/20 text-gold-400 border border-gold-500/30'
                                                    : 'bg-white/5 text-white/40 border border-white/10 hover:text-white/60'
                                                    }`}>{u.l}</button>
                                        ))}
                                    </div>
                                </div>
                                <input type="number" value={qForm.time_limit_seconds} min={1}
                                    onChange={e => setQForm({ ...qForm, time_limit_seconds: e.target.value })}
                                    className="input-gold w-full"
                                    placeholder={qForm.time_unit === 'seconds' ? '60' : qForm.time_unit === 'minutes' ? '1' : '1'}
                                />
                            </div>
                        </div>

                        {/* Target Groups */}
                        <div className="mb-4">
                            <label className="block text-white/60 text-sm mb-2">المجموعات المستهدفة</label>
                            <div className="flex flex-wrap gap-2">
                                {['all', 'VIP', 'Student', ...groups.map(g => `group:${g.id}`)].map(t => (
                                    <button key={t}
                                        onClick={() => {
                                            let tg = [...qForm.target_groups]
                                            if (t === 'all') {
                                                tg = ['all']
                                            } else {
                                                tg = tg.filter(x => x !== 'all')
                                                if (tg.includes(t)) tg = tg.filter(x => x !== t)
                                                else tg.push(t)
                                                if (tg.length === 0) tg = ['all']
                                            }
                                            setQForm({ ...qForm, target_groups: tg })
                                        }}
                                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${qForm.target_groups.includes(t)
                                            ? 'bg-gold-500/20 text-gold-400 border border-gold-500/30'
                                            : 'bg-white/5 text-white/50 border border-white/10'
                                            }`}>
                                        {t === 'all' ? '🌐 الكل' : t === 'VIP' ? '⭐ VIP' : t === 'Student' ? '🎓 طلبة' : groups.find(g => `group:${g.id}` === t)?.name}
                                    </button>
                                ))}
                            </div>
                        </div>



                        {/* Submit */}
                        <button onClick={createQuestion} disabled={loading || !qForm.text || (qForm.question_type === 'mcq' && !qForm.correct_answer) || (qForm.question_type === 'completion' && !qForm.correct_answers.some(a => a.trim()))}
                            className="btn-gold w-full flex items-center justify-center gap-2">
                            {loading ? <Clock className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                            إنشاء السؤال
                        </button>
                    </div>
                </div>
            )}

            {/* ═══════ MODAL: Create Group ═══════ */}
            {showCreateGroup && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-400 rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto border border-gold-500/20">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-gold-400">{editingGroup ? 'تعديل المجموعة' : 'مجموعة جديدة'}</h3>
                            <button onClick={() => { setShowCreateGroup(false); setEditingGroup(null); setGForm({ name: '', description: '', ticket_ids: [] }) }}
                                className="text-white/40 hover:text-white"><X className="w-5 h-5" /></button>
                        </div>

                        <label className="block text-white/60 text-sm mb-1">اسم المجموعة</label>
                        <input value={gForm.name}
                            onChange={e => setGForm({ ...gForm, name: e.target.value })}
                            className="input-gold w-full mb-3"
                            placeholder="مثال: فريق البطولة"
                        />

                        <label className="block text-white/60 text-sm mb-1">الوصف (اختياري)</label>
                        <input value={gForm.description}
                            onChange={e => setGForm({ ...gForm, description: e.target.value })}
                            className="input-gold w-full mb-4"
                            placeholder="وصف قصير..."
                        />

                        {/* Member Selection */}
                        <label className="block text-white/60 text-sm mb-2">اختيار الأعضاء</label>
                        <div className="relative mb-3">
                            <Search className="w-4 h-4 absolute right-3 top-3 text-white/30" />
                            <input value={gSearch}
                                onChange={e => setGSearch(e.target.value)}
                                className="input-gold w-full pr-10"
                                placeholder="بحث بالاسم..."
                            />
                        </div>
                        <div className="max-h-48 overflow-y-auto space-y-1 mb-4 border border-white/10 rounded-xl p-2">
                            {attendees
                                .filter(a => a.guest_name?.includes(gSearch) || !gSearch)
                                .map(a => (
                                    <button key={a.id}
                                        onClick={() => {
                                            const ids = new Set(gForm.ticket_ids)
                                            if (ids.has(a.id)) ids.delete(a.id)
                                            else ids.add(a.id)
                                            setGForm({ ...gForm, ticket_ids: [...ids] })
                                        }}
                                        className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${gForm.ticket_ids.includes(a.id)
                                            ? 'bg-gold-500/15 text-gold-400'
                                            : 'text-white/60 hover:bg-white/5'
                                            }`}>
                                        <span>{a.guest_name}</span>
                                        <span className="text-xs text-white/30">{a.ticket_type}</span>
                                    </button>
                                ))}
                        </div>
                        <p className="text-white/30 text-xs mb-4">تم اختيار {gForm.ticket_ids.length} عضو</p>

                        <button onClick={createGroup} disabled={loading || !gForm.name || gForm.ticket_ids.length === 0}
                            className="btn-gold w-full flex items-center justify-center gap-2">
                            {loading ? <Clock className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
                            {editingGroup ? 'حفظ التعديلات' : 'إنشاء المجموعة'}
                        </button>
                    </div>
                </div>
            )}

            {/* ═══════ MODAL: Question Answers Detail ═══════ */}
            {showAnswers && answersData && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div className="bg-dark-400 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gold-500/20">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gold-400">إجابات السؤال</h3>
                            <button onClick={() => { setShowAnswers(null); setAnswersData(null) }}
                                className="text-white/40 hover:text-white"><X className="w-5 h-5" /></button>
                        </div>

                        <div className="card mb-4 border border-white/10">
                            <p className="text-white font-medium">{answersData.question?.text}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-white/40">
                                <span className="text-green-400">{answersData.correct} صح</span>
                                <span className="text-red-400">{answersData.total - answersData.correct} خطأ</span>
                                <span>من {answersData.total} إجابة</span>
                            </div>
                        </div>

                        {answersData.answers?.length === 0 ? (
                            <p className="text-white/50 text-center py-8">لا توجد إجابات</p>
                        ) : (
                            <table className="table-gold">
                                <thead>
                                    <tr>
                                        <th>الاسم</th>
                                        <th>الإجابة</th>
                                        <th>النتيجة</th>
                                        <th>التشابه</th>
                                        <th>النقاط</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {answersData.answers.map(a => (
                                        <tr key={a.id}>
                                            <td className="font-semibold">{a.guest_name}</td>
                                            <td className="text-white/70 text-sm">{a.answer_text}</td>
                                            <td>
                                                {a.is_correct
                                                    ? <CheckCircle className="w-5 h-5 text-green-400" />
                                                    : <XCircle className="w-5 h-5 text-red-400" />
                                                }
                                            </td>
                                            <td className="text-white/50 text-sm">
                                                {a.similarity_score > 0 ? `${a.similarity_score}%` : '—'}
                                            </td>
                                            <td className="text-gold-400 font-bold">{a.points_earned}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

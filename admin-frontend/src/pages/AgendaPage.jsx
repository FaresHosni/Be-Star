import React, { useState, useEffect, useCallback } from 'react'
import {
    Calendar, Plus, Trash2, Edit3, Save, X, MapPin, Clock,
    ChevronRight, ChevronLeft, Bell, BellOff
} from 'lucide-react'
import { apiFetch } from '../utils/api'

const API = '/api/agenda'

function getWeekStart(dateObj) {
    const d = new Date(dateObj)
    const day = d.getDay()
    const diff = (day === 6) ? 0 : (day + 1)
    d.setDate(d.getDate() - diff)
    return d
}

function formatDate(d) {
    return d.toISOString().split('T')[0]
}

const DAY_NAMES = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']

function AgendaPage() {
    const [selectedDate, setSelectedDate] = useState(formatDate(new Date()))
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)
    const [showForm, setShowForm] = useState(false)
    const [editingId, setEditingId] = useState(null)

    // Form state
    const [formTitle, setFormTitle] = useState('')
    const [formDesc, setFormDesc] = useState('')
    const [formTime, setFormTime] = useState('')
    const [formLocation, setFormLocation] = useState('')

    // Week events
    const [weekEvents, setWeekEvents] = useState([])

    const fetchEvents = useCallback(async () => {
        setLoading(true)
        try {
            const res = await apiFetch(`${API}/?date_filter=${selectedDate}`)
            const data = await res.json()
            setEvents(data)
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [selectedDate])

    const fetchWeekEvents = useCallback(async () => {
        try {
            const weekStart = getWeekStart(new Date(selectedDate))
            const res = await apiFetch(`${API}/week?start_date=${formatDate(weekStart)}`)
            const data = await res.json()
            setWeekEvents(data.events || [])
        } catch (e) { console.error(e) }
    }, [selectedDate])

    useEffect(() => { fetchEvents(); fetchWeekEvents() }, [fetchEvents, fetchWeekEvents])

    // ─── Actions ───
    const resetForm = () => {
        setFormTitle(''); setFormDesc(''); setFormTime(''); setFormLocation('')
        setShowForm(false); setEditingId(null)
    }

    const saveEvent = async () => {
        if (!formTitle.trim() || !formTime) return
        const eventTime = `${selectedDate}T${formTime}:00`

        try {
            if (editingId) {
                await apiFetch(`${API}/${editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: formTitle,
                        description: formDesc || null,
                        event_time: eventTime,
                        location: formLocation || null,
                    })
                })
            } else {
                await apiFetch(`${API}/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: formTitle,
                        description: formDesc || null,
                        event_time: eventTime,
                        location: formLocation || null,
                        date: selectedDate,
                    })
                })
            }
            resetForm()
            fetchEvents()
            fetchWeekEvents()
        } catch (e) { console.error(e) }
    }

    const deleteEvent = async (id) => {
        if (!confirm('هل أنت متأكد من حذف هذا الحدث؟')) return
        try {
            await apiFetch(`${API}/${id}`, { method: 'DELETE' })
            fetchEvents()
            fetchWeekEvents()
        } catch (e) { console.error(e) }
    }

    const startEdit = (event) => {
        setEditingId(event.id)
        setFormTitle(event.title)
        setFormDesc(event.description || '')
        setFormTime(event.event_time ? event.event_time.split('T')[1]?.substring(0, 5) : '')
        setFormLocation(event.location || '')
        setShowForm(true)
    }

    // ─── Date Navigation ───
    const changeDate = (offset) => {
        const d = new Date(selectedDate)
        d.setDate(d.getDate() + offset)
        setSelectedDate(formatDate(d))
    }

    const todayDate = formatDate(new Date())
    const currentDayName = DAY_NAMES[new Date(selectedDate).getDay()]

    // Group week events by day for the week dots
    const weekDayCounts = {}
    weekEvents.forEach(e => {
        weekDayCounts[e.date] = (weekDayCounts[e.date] || 0) + 1
    })

    return (
        <div className="space-y-6 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold gold-text">📅 الأجندة</h1>
                    <p className="text-white/60 mt-1">إدارة الأحداث والمواعيد مع تذكيرات تلقائية</p>
                </div>
                <button
                    onClick={() => { setShowForm(!showForm); if (showForm) resetForm() }}
                    className="btn-2026 flex items-center gap-2"
                >
                    {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                    {showForm ? 'إلغاء' : 'حدث جديد'}
                </button>
            </div>

            {/* Week Navigation */}
            <div className="card">
                <div className="grid grid-cols-7 gap-2">
                    {(() => {
                        const weekStart = getWeekStart(new Date(selectedDate))
                        const days = []
                        for (let i = 0; i < 7; i++) {
                            const d = new Date(weekStart)
                            d.setDate(d.getDate() + i)
                            const dStr = formatDate(d)
                            const isSelected = dStr === selectedDate
                            const isToday = dStr === todayDate
                            const count = weekDayCounts[dStr] || 0
                            days.push(
                                <button
                                    key={dStr}
                                    onClick={() => setSelectedDate(dStr)}
                                    className={`rounded-xl p-3 text-center transition-all border ${isSelected
                                            ? 'border-gold-500 bg-gold-500/20'
                                            : isToday
                                                ? 'border-blue-500/50 bg-blue-500/10'
                                                : 'border-white/10 bg-white/5 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="text-xs text-white/50 mb-1">{DAY_NAMES[d.getDay()]}</div>
                                    <div className="text-lg font-bold text-white">{dStr.split('-')[2]}</div>
                                    {count > 0 && (
                                        <div className="flex justify-center gap-1 mt-2">
                                            {Array.from({ length: Math.min(count, 4) }).map((_, idx) => (
                                                <div key={idx} className="w-1.5 h-1.5 rounded-full bg-gold-400" />
                                            ))}
                                        </div>
                                    )}
                                </button>
                            )
                        }
                        return days
                    })()}
                </div>
            </div>

            {/* Date Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <button onClick={() => changeDate(-1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <ChevronRight className="w-5 h-5 text-white/60" />
                    </button>
                    <div className="flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-gold-500" />
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={e => setSelectedDate(e.target.value)}
                            className="bg-transparent text-white text-lg font-semibold border-none outline-none cursor-pointer"
                        />
                        <span className="text-white/40 text-sm">({currentDayName})</span>
                    </div>
                    <button onClick={() => changeDate(1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <ChevronLeft className="w-5 h-5 text-white/60" />
                    </button>
                    {selectedDate !== todayDate && (
                        <button onClick={() => setSelectedDate(todayDate)} className="text-xs text-gold-400 hover:text-gold-300">
                            اليوم
                        </button>
                    )}
                </div>
                <span className="text-sm text-white/40">{events.length} أحداث</span>
            </div>

            {/* Add/Edit Form */}
            {showForm && (
                <div className="card border-gold-500/30">
                    <h3 className="text-lg font-semibold text-gold-500 mb-4">
                        {editingId ? '✏️ تعديل الحدث' : '➕ حدث جديد'}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="label-2026">اسم الحدث</label>
                            <input
                                className="input-2026"
                                placeholder="مثال: اجتماع الفريق"
                                value={formTitle}
                                onChange={e => setFormTitle(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="label-2026"><Clock className="w-4 h-4" /> الوقت</label>
                            <input
                                type="time"
                                className="input-2026"
                                value={formTime}
                                onChange={e => setFormTime(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="label-2026"><MapPin className="w-4 h-4" /> المكان</label>
                            <input
                                className="input-2026"
                                placeholder="مثال: قاعة السويس"
                                value={formLocation}
                                onChange={e => setFormLocation(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="label-2026">وصف إضافي</label>
                            <input
                                className="input-2026"
                                placeholder="تفاصيل إضافية (اختياري)"
                                value={formDesc}
                                onChange={e => setFormDesc(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="mt-4 flex gap-3 justify-end">
                        <button onClick={resetForm} className="btn-cancel-2026">إلغاء</button>
                        <button
                            onClick={saveEvent}
                            className="btn-2026"
                            disabled={!formTitle.trim() || !formTime}
                        >
                            <Save className="w-4 h-4 inline ml-2" />
                            {editingId ? 'حفظ التعديل' : 'إضافة الحدث'}
                        </button>
                    </div>
                </div>
            )}

            {/* Events Timeline */}
            <div className="space-y-4">
                {loading ? (
                    <div className="text-center py-12 text-white/40">جاري التحميل...</div>
                ) : events.length === 0 ? (
                    <div className="text-center py-12">
                        <Calendar className="w-16 h-16 mx-auto text-white/10 mb-4" />
                        <p className="text-white/40">لا توجد أحداث لهذا اليوم</p>
                        <p className="text-white/30 text-sm mt-1">أضف حدث جديد من الزر أعلاه</p>
                    </div>
                ) : (
                    events.map((event, index) => {
                        const eventTime = event.event_time ? new Date(event.event_time) : null
                        const timeStr = eventTime
                            ? eventTime.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
                            : '—'
                        const isPast = eventTime && eventTime < new Date()

                        return (
                            <div key={event.id} className="flex gap-4">
                                {/* Timeline Line */}
                                <div className="flex flex-col items-center">
                                    <div className={`w-4 h-4 rounded-full border-2 ${isPast ? 'border-white/20 bg-white/10' : 'border-gold-500 bg-gold-500/30'
                                        }`} />
                                    {index < events.length - 1 && (
                                        <div className="w-0.5 flex-1 bg-white/10 my-1" />
                                    )}
                                </div>

                                {/* Event Card */}
                                <div className={`card flex-1 mb-2 ${isPast ? 'opacity-60' : ''} ${event.reminder_sent ? 'border-green-500/30' : 'border-white/10'
                                    }`}>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="text-2xl font-bold text-gold-400">{timeStr}</span>
                                                {event.reminder_sent && (
                                                    <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded-full">
                                                        <Bell className="w-3 h-3" /> تم التذكير
                                                    </span>
                                                )}
                                                {!event.reminder_sent && !isPast && (
                                                    <span className="flex items-center gap-1 text-xs text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded-full">
                                                        <BellOff className="w-3 h-3" /> لم يُذكّر بعد
                                                    </span>
                                                )}
                                            </div>
                                            <h4 className={`text-lg font-semibold ${isPast ? 'text-white/50' : 'text-white'}`}>
                                                {event.title}
                                            </h4>
                                            {event.location && (
                                                <p className="text-sm text-white/50 mt-1 flex items-center gap-1">
                                                    <MapPin className="w-3 h-3" /> {event.location}
                                                </p>
                                            )}
                                            {event.description && (
                                                <p className="text-sm text-white/40 mt-1">{event.description}</p>
                                            )}
                                        </div>

                                        <div className="flex gap-1">
                                            <button
                                                onClick={() => startEdit(event)}
                                                className="p-2 text-white/30 hover:text-gold-400 hover:bg-gold-500/10 rounded-lg transition-colors"
                                            >
                                                <Edit3 className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => deleteEvent(event.id)}
                                                className="p-2 text-white/30 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )
                    })
                )}
            </div>
        </div>
    )
}

export default AgendaPage

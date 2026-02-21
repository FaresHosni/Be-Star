import { useState } from 'react';
import { GraduationCap, Wrench, MessageSquare, Trophy, Pin, Mic, BookOpen } from 'lucide-react';
import eventData from '../config/eventData.json';

export default function Sessions() {
    const { sessions } = eventData;
    const [filter, setFilter] = useState('الكل');

    const types = ['الكل', ...new Set(sessions.map((s) => s.type))];
    const filtered = filter === 'الكل' ? sessions : sessions.filter((s) => s.type === filter);

    const typeIcons = {
        'محاضرة': <GraduationCap size={24} />,
        'ورشة عمل': <Wrench size={24} />,
        'جلسة حوارية': <MessageSquare size={24} />,
        'مسابقة': <Trophy size={24} />,
    };

    return (
        <>
            <div className="page-header">
                <h1>الجلسات والفقرات</h1>
                <p>اكتشف جميع الجلسات وورش العمل والمسابقات المقررة في الحدث</p>
            </div>

            <section className="section">
                <div className="container">
                    <div className="sessions-filters">
                        {types.map((type) => (
                            <button
                                key={type}
                                className={`filter-btn${filter === type ? ' active' : ''}`}
                                onClick={() => setFilter(type)}
                            >
                                {type}
                            </button>
                        ))}
                    </div>

                    {filtered.map((session) => (
                        <div className="session-card" key={session.id}>
                            <div className="session-icon">
                                {typeIcons[session.type] || <Pin size={24} />}
                            </div>
                            <div className="session-info">
                                <h3>{session.title}</h3>
                                <p style={{ color: 'var(--gray-500)', fontSize: '0.95rem', margin: '8px 0' }}>
                                    {session.description}
                                </p>
                                <div className="session-meta">
                                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Mic size={14} /> {session.speaker}</span>
                                    <span className="badge badge-blue">{session.type}</span>
                                    <span className="badge badge-gold">{session.level}</span>
                                </div>
                                <p style={{ fontSize: '0.85rem', color: 'var(--gray-400)', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <BookOpen size={14} /> ما ستتعلمه: {session.learnings}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </>
    );
}

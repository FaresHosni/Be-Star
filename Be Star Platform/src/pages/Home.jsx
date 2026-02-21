import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Star, Ticket, Mic, MessageCircle, Target, FileText, ClipboardList } from 'lucide-react';

const aiIcons = {
    MessageCircle: <MessageCircle size={32} />,
    Ticket: <Ticket size={32} />,
    Target: <Target size={32} />,
    FileText: <FileText size={32} />,
    ClipboardList: <ClipboardList size={32} />
};
import eventData from '../config/eventData.json';

function CountdownTimer({ targetDate }) {
    const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date().getTime();
            const target = new Date(targetDate).getTime();
            const diff = target - now;

            if (diff > 0) {
                setTimeLeft({
                    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
                    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
                    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
                    seconds: Math.floor((diff % (1000 * 60)) / 1000),
                });
            }
        }, 1000);
        return () => clearInterval(timer);
    }, [targetDate]);

    return (
        <div className="countdown">
            {[
                { value: timeLeft.days, label: 'يوم' },
                { value: timeLeft.hours, label: 'ساعة' },
                { value: timeLeft.minutes, label: 'دقيقة' },
                { value: timeLeft.seconds, label: 'ثانية' },
            ].map((item, i) => (
                <div className="countdown-item" key={i}>
                    <div className="countdown-number">{String(item.value).padStart(2, '0')}</div>
                    <div className="countdown-label">{item.label}</div>
                </div>
            ))}
        </div>
    );
}

function FAQSection() {
    const [openIndex, setOpenIndex] = useState(null);

    return (
        <div className="faq-list">
            {eventData.faq.map((item, i) => (
                <div className={`faq-item${openIndex === i ? ' open' : ''}`} key={i}>
                    <div className="faq-question" onClick={() => setOpenIndex(openIndex === i ? null : i)}>
                        <span>{item.q}</span>
                        <span className="faq-arrow">▼</span>
                    </div>
                    {openIndex === i && <div className="faq-answer">{item.a}</div>}
                </div>
            ))}
        </div>
    );
}

export default function Home() {
    const { event, speakers, sponsors } = eventData;

    // Generate random stars
    const stars = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        top: `${Math.random() * 100}%`,
        left: `${Math.random() * 100}%`,
        delay: `${Math.random() * 3}s`,
        size: `${2 + Math.random() * 3}px`,
    }));

    return (
        <>
            {/* ═══════ Hero Section ═══════ */}
            <section className="hero">
                <div className="stars">
                    {stars.map((s) => (
                        <div
                            key={s.id}
                            className="star"
                            style={{
                                top: s.top,
                                left: s.left,
                                animationDelay: s.delay,
                                width: s.size,
                                height: s.size,
                            }}
                        />
                    ))}
                </div>
                <div className="hero-content">
                    <div className="hero-badge">
                        <Star fill="currentColor" size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px' }} /> {event.tagline}
                    </div>
                    <h1>
                        نحو النجومية
                        <span className="gold">كن نجماً</span>
                    </h1>
                    <p className="hero-desc">{event.description}</p>

                    <div className="hero-buttons">
                        <Link to="/tickets" className="btn btn-primary btn-lg">
                            <Ticket size={20} /> احجز مكانك الآن
                        </Link>
                        <Link to="/about" className="btn btn-secondary btn-lg">
                            اكتشف المزيد
                        </Link>
                    </div>

                    <CountdownTimer targetDate={event.date} />

                    <div className="hero-stats">
                        <div className="hero-stat">
                            <div className="hero-stat-number">+{event.participantsCount.toLocaleString()}</div>
                            <div className="hero-stat-label">مشارك</div>
                        </div>
                        <div className="hero-stat">
                            <div className="hero-stat-number">+{event.speakersCount}</div>
                            <div className="hero-stat-label">متحدث</div>
                        </div>
                        <div className="hero-stat">
                            <div className="hero-stat-number">+{event.workshopsCount}</div>
                            <div className="hero-stat-label">ورشة عمل</div>
                        </div>
                        <div className="hero-stat">
                            <div className="hero-stat-number">+{event.companiesCount}</div>
                            <div className="hero-stat-label">شركة ناشئة</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════ Speakers Preview ═══════ */}
            <section className="section" style={{ background: 'var(--gray-50)' }}>
                <div className="container">
                    <h2 className="section-title">المتحدثون والضيوف</h2>
                    <p className="section-subtitle">تعرّف على نخبة من أفضل الخبراء في صناعة المحتوى والإعلام</p>
                    <div className="speakers-grid">
                        {speakers.slice(0, 3).map((speaker) => (
                            <div className="speaker-card" key={speaker.id}>
                                <div className="speaker-avatar">
                                    {speaker.name.charAt(0)}
                                </div>
                                <h3>{speaker.name}</h3>
                                <div className="field">{speaker.field}</div>
                                <p className="bio">{speaker.bio}</p>
                                <div className="session-badge"><Mic size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px' }} /> {speaker.session}</div>
                            </div>
                        ))}
                    </div>
                    <div style={{ textAlign: 'center', marginTop: '32px' }}>
                        <Link to="/speakers" className="btn btn-outline">
                            عرض جميع المتحدثين ←
                        </Link>
                    </div>
                </div>
            </section>

            {/* ═══════ AI Features Preview ═══════ */}
            <section className="section">
                <div className="container">
                    <h2 className="section-title">مدعوم بالذكاء الاصطناعي</h2>
                    <p className="section-subtitle">
                        هذا الحدث مدعوم بتقنيات الذكاء الاصطناعي من شركة Mr. AI لتجربة ذكية ومتكاملة
                    </p>
                    <div className="ai-features-grid">
                        {eventData.aiFeatures.slice(0, 3).map((feature, i) => (
                            <div className="ai-feature-card" key={i}>
                                <div className="ai-feature-icon">{aiIcons[feature.icon]}</div>
                                <h3>{feature.titleAr}</h3>
                                <div className="title-en">{feature.title}</div>
                                <p>{feature.description}</p>
                            </div>
                        ))}
                    </div>
                    <div style={{ textAlign: 'center', marginTop: '32px' }}>
                        <Link to="/ai-features" className="btn btn-outline">
                            اكتشف جميع المميزات ←
                        </Link>
                    </div>
                </div>
            </section>

            {/* ═══════ Sponsors Preview ═══════ */}
            <section className="section" style={{ background: 'var(--gray-50)' }}>
                <div className="container">
                    <h2 className="section-title">رعاة وشركاء الحدث</h2>
                    <p className="section-subtitle">شكراً لشركائنا الذين يدعمون رحلة صناع المحتوى</p>
                    <div className="sponsors-grid">
                        {sponsors.slice(0, 5).map((sponsor) => (
                            <div className="sponsor-card" key={sponsor.id}>
                                {sponsor.name}
                            </div>
                        ))}
                    </div>
                    <div style={{ textAlign: 'center', marginTop: '32px' }}>
                        <Link to="/sponsors" className="btn btn-outline">
                            عرض جميع الرعاة ←
                        </Link>
                    </div>
                </div>
            </section>

            {/* ═══════ FAQ ═══════ */}
            <section className="section">
                <div className="container">
                    <h2 className="section-title">الأسئلة الشائعة</h2>
                    <p className="section-subtitle">إجابات على أكثر الأسئلة تكراراً عن الحدث</p>
                    <FAQSection />
                </div>
            </section>

            {/* ═══════ CTA Section ═══════ */}
            <section style={{
                background: 'var(--gradient-hero)',
                padding: '80px 24px',
                textAlign: 'center',
                color: '#fff',
            }}>
                <div className="container">
                    <h2 style={{ fontSize: '2.2rem', fontWeight: 900, marginBottom: '16px' }}>
                        مستعد تكون نجم؟ <Star fill="currentColor" size={28} style={{ display: 'inline', verticalAlign: 'text-bottom', marginStart: '8px' }} />
                    </h2>
                    <p style={{ fontSize: '1.1rem', opacity: 0.7, marginBottom: '32px', maxWidth: '500px', margin: '0 auto 32px' }}>
                        لا تفوّت فرصة بناء مستقبلك في صناعة المحتوى. احجز مكانك الآن!
                    </p>
                    <Link to="/tickets" className="btn btn-primary btn-lg">
                        <Ticket size={20} /> احجز مكانك الآن
                    </Link>
                </div>
            </section>
        </>
    );
}

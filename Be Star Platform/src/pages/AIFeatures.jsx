import eventData from '../config/eventData.json';
import { Bot, Zap, User, Settings, MessageCircle, Ticket, Target, ClipboardList, FileText } from 'lucide-react';

const aiIcons = {
    MessageCircle: <MessageCircle size={32} />,
    Ticket: <Ticket size={32} />,
    Target: <Target size={32} />,
    FileText: <FileText size={32} />,
    ClipboardList: <ClipboardList size={32} />
};

export default function AIFeatures() {
    const { aiFeatures } = eventData;

    return (
        <>
            <div className="page-header">
                <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}><Bot size={36} /> مميزات الذكاء الاصطناعي</h1>
                <p>هذا الحدث مدعوم بتقنيات الذكاء الاصطناعي من شركة Mr. AI</p>
            </div>

            {/* Intro */}
            <section className="section">
                <div className="container" style={{ maxWidth: '700px', textAlign: 'center' }}>
                    <div className="card" style={{
                        padding: '40px',
                        background: 'linear-gradient(135deg, rgba(10,22,40,0.03), rgba(255,193,7,0.05))',
                        border: '1px solid rgba(255,193,7,0.15)',
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--primary-gold-dark)' }}><Zap size={48} /></div>
                        <h2 style={{ color: 'var(--primary-dark)', marginBottom: '12px', fontSize: '1.5rem' }}>
                            ليس مجرد موقع إيفنت عادي
                        </h2>
                        <p style={{ color: 'var(--gray-500)', lineHeight: 1.8, fontSize: '1.05rem' }}>
                            إيفنت كن نجماً يعتمد على <strong style={{ color: 'var(--primary-gold-dark)' }}>نظام تشغيل ذكي</strong> مبني
                            بالكامل على الذكاء الاصطناعي من شركة <strong style={{ color: 'var(--primary-blue)' }}>Mr. AI</strong>.
                            <br />
                            موظفين ذكاء اصطناعي متخصصين يديرون كل مرحلة من مراحل الحدث — من التسجيل إلى المتابعة.
                        </p>
                    </div>
                </div>
            </section>

            {/* AI Officers Grid */}
            <section className="section" style={{ background: 'var(--gray-50)', paddingTop: 0 }}>
                <div className="container">
                    <h2 className="section-title">موظفو الذكاء الاصطناعي</h2>
                    <p className="section-subtitle">كل مرحلة في الحدث يديرها موظف ذكاء اصطناعي متخصص</p>

                    <div className="ai-features-grid">
                        {aiFeatures.map((feature, i) => (
                            <div className="ai-feature-card" key={i}>
                                <div className="ai-feature-icon">{aiIcons[feature.icon]}</div>
                                <h3>{feature.titleAr}</h3>
                                <div className="title-en">{feature.title}</div>
                                <p>{feature.description}</p>
                                <div style={{ marginTop: '16px' }}>
                                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }} className={`badge ${feature.userFacing ? 'badge-gold' : 'badge-blue'}`}>
                                        {feature.userFacing ? <><User size={14} /> متاح للمستخدم</> : <><Settings size={14} /> خلف الكواليس</>}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="section">
                <div className="container" style={{ maxWidth: '700px' }}>
                    <h2 className="section-title">كيف يعمل النظام؟</h2>
                    <p className="section-subtitle">رحلة المشارك مدعومة بالذكاء الاصطناعي في كل خطوة</p>

                    {[
                        { step: '1', title: 'قبل الحدث', desc: 'مساعد التوعية يجيب على جميع الأسئلة ويساعد في الحجز', icon: <MessageCircle size={24} color="#fff" /> },
                        { step: '2', title: 'التسجيل', desc: 'موظف التذاكر يسجل المشاركين ويدير عمليات الدفع تلقائياً', icon: <Ticket size={24} color="#fff" /> },
                        { step: '3', title: 'أثناء الحدث', desc: 'موظف التفاعل يدير المسابقات والأسئلة التفاعلية', icon: <Target size={24} color="#fff" /> },
                        { step: '4', title: 'التنظيم', desc: 'منسق اللوجستيات يتابع الجدول الزمني ويدير الموارد', icon: <ClipboardList size={24} color="#fff" /> },
                        { step: '5', title: 'بعد الحدث', desc: 'موظف الشهادات يرسل الشهادات ويتابع المشاركين', icon: <FileText size={24} color="#fff" /> },
                    ].map((item, i) => (
                        <div key={i} style={{
                            display: 'flex',
                            gap: '20px',
                            alignItems: 'flex-start',
                            marginBottom: '20px',
                            padding: '20px',
                            background: 'var(--white)',
                            borderRadius: 'var(--radius-md)',
                            border: '1px solid var(--gray-100)',
                            transition: 'all 0.3s ease',
                        }}>
                            <div style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '50%',
                                background: 'var(--gradient-gold)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.5rem',
                                flexShrink: 0,
                            }}>{item.icon}</div>
                            <div>
                                <h4 style={{ color: 'var(--primary-dark)', marginBottom: '4px' }}>
                                    <span style={{ color: 'var(--primary-gold-dark)' }}>المرحلة {item.step} — </span>{item.title}
                                </h4>
                                <p style={{ color: 'var(--gray-500)', fontSize: '0.95rem' }}>{item.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Mr. AI Footer */}
            <section style={{
                background: 'var(--gradient-hero)',
                padding: '60px 24px',
                textAlign: 'center',
                color: '#fff',
            }}>
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--primary-gold)' }}><Zap size={48} /></div>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '12px' }}>
                    مدعوم بالذكاء الاصطناعي من Mr. AI
                </h2>
                <p style={{ opacity: 0.7, maxWidth: '500px', margin: '0 auto' }}>
                    نبني أنظمة ذكية تُحسّن تجربة الأحداث وتُقلل من العبء على الفريق البشري
                </p>
            </section>
        </>
    );
}

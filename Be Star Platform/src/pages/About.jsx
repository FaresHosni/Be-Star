export default function About() {
    const features = [
        { icon: '🎯', title: 'الرؤية', desc: 'أن نكون المنصة الأولى لتمكين صناع المحتوى في صعيد مصر وربطهم بفرص حقيقية.' },
        { icon: '💡', title: 'الرسالة', desc: 'تقديم بيئة متكاملة تجمع بين التعلم والتطبيق والتشبيك لبناء جيل جديد من صناع المحتوى المحترفين.' },
        { icon: '🚀', title: 'القيمة المضافة', desc: 'ليس مجرد مؤتمر... بل منظومة تمكين متكاملة تجمع بين التعلم والتطبيق والتشبيك والفرص الحقيقية بعد الحدث.' },
        { icon: '🤖', title: 'مدعوم بالذكاء الاصطناعي', desc: 'الحدث مدعوم بتقنيات الذكاء الاصطناعي من شركة Mr. AI لإدارة رحلة الحضور بالكامل.' },
        { icon: '⭐', title: 'لماذا مختلف؟', desc: 'كل خطوة لها نظام واضح: من التسجيل الذكي، للتفاعل أثناء الحدث، للشهادات والمتابعة بعده.' },
        { icon: '🎓', title: 'الأهداف', desc: 'تطوير مهارات صناعة المحتوى، التشبيك مع الخبراء، توفير فرص عمل حقيقية للمشاركين المتميزين.' },
    ];

    return (
        <>
            <div className="page-header">
                <h1>عن الحدث</h1>
                <p>تعرّف على إيفنت كن نجماً ورؤيتنا لتمكين صناع المحتوى في صعيد مصر</p>
            </div>

            <section className="section">
                <div className="container">
                    <div className="about-grid">
                        {features.map((f, i) => (
                            <div className="about-card" key={i}>
                                <div className="about-card-icon">{f.icon}</div>
                                <h3>{f.title}</h3>
                                <p>{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* الجهة المنظمة */}
            <section className="section" style={{ background: 'var(--gray-50)' }}>
                <div className="container" style={{ maxWidth: '700px', textAlign: 'center' }}>
                    <h2 className="section-title">الجهة المنظمة</h2>
                    <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🏢</div>
                        <h3 style={{ fontSize: '1.3rem', marginBottom: '8px', color: 'var(--primary-dark)' }}>Be Star Organization</h3>
                        <p style={{ color: 'var(--gray-500)', lineHeight: 1.7 }}>
                            مؤسسة كن نجماً هي المسؤولة عن تنظيم أكبر منحة لصناع المحتوى في صعيد مصر.
                            تهدف لتمكين 1000 صانع محتوى من خلال التعليم والتدريب والتشبيك.
                        </p>
                    </div>

                    <div className="card" style={{ textAlign: 'center', padding: '40px', marginTop: '20px' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>⚡</div>
                        <h3 style={{ fontSize: '1.3rem', marginBottom: '8px', color: 'var(--primary-gold-dark)' }}>الشريك التقني — Mr. AI</h3>
                        <p style={{ color: 'var(--gray-500)', lineHeight: 1.7 }}>
                            شركة Mr. AI هي الشريك التقني المسؤول عن تطوير المنصة الذكية وموظفي الذكاء الاصطناعي
                            الذين يديرون رحلة الحضور بالكامل من التسجيل إلى المتابعة.
                        </p>
                    </div>
                </div>
            </section>

            {/* الفئة المستهدفة */}
            <section className="section">
                <div className="container" style={{ maxWidth: '900px' }}>
                    <h2 className="section-title">الفئة المستهدفة</h2>
                    <p className="section-subtitle">هذا الحدث مصمم خصيصاً لكل طموح يسعى للنجاح في عالم الإعلام والمحتوى</p>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                        gap: '20px'
                    }}>
                        {[
                            { title: 'صُناع المحتوى', icon: '📱', desc: 'على منصات TikTok, YouTube, Facebook, Instagram' },
                            { title: 'المؤثرون والبلوجرز', icon: '🌟', desc: 'كل من لديه رسالة ويريد توسيع تأثيره' },
                            { title: 'طلاب الإعلام', icon: '🎓', desc: 'والمهتمون بمجال الصحافة والتقديم التلفزيوني' },
                            { title: 'أصحاب الأعمال', icon: '💼', desc: 'الراغبون في تعلم تسويق المحتوى لتنمية مشاريعهم' },
                        ].map((target, i) => (
                            <div key={i} className="card" style={{ textAlign: 'center', padding: '24px' }}>
                                <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>{target.icon}</div>
                                <h4 style={{ color: 'var(--primary-dark)', marginBottom: '8px' }}>{target.title}</h4>
                                <p style={{ color: 'var(--gray-500)', fontSize: '0.9rem' }}>{target.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* User Journey */}
            <section className="section">
                <div className="container" style={{ maxWidth: '700px' }}>
                    <h2 className="section-title">رحلة المشارك</h2>
                    <p className="section-subtitle">من أول ما تسمع عن الحدث لحد ما تحصل على شهادتك</p>

                    {[
                        { step: '1', title: 'الاكتشاف', desc: 'تشوف الإعلان → تدخل الموقع → تتعرف على التفاصيل من المساعد الذكي', icon: '🔍' },
                        { step: '2', title: 'التسجيل', desc: 'تحجز عبر الفورم أو الشات الذكي → تستلم تذكرتك الرقمية', icon: '🎫' },
                        { step: '3', title: 'قبل الحدث', desc: 'تتلقى تذكيرات ومحتوى تحضيري عبر واتساب', icon: '📱' },
                        { step: '4', title: 'أثناء الحدث', desc: 'تتفاعل عبر QR → مسابقات → تسجيل النتائج', icon: '🎯' },
                        { step: '5', title: 'بعد الحدث', desc: 'شهادة حضور تلقائية للناجحين', icon: '📜' },
                    ].map((item, i) => (
                        <div key={i} style={{
                            display: 'flex',
                            gap: '20px',
                            alignItems: 'flex-start',
                            marginBottom: '24px',
                            padding: '20px',
                            background: 'var(--white)',
                            borderRadius: 'var(--radius-md)',
                            border: '1px solid var(--gray-100)',
                        }}>
                            <div style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: 'var(--radius-full)',
                                background: 'var(--gradient-hero)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.5rem',
                                flexShrink: 0,
                            }}>{item.icon}</div>
                            <div>
                                <h4 style={{ color: 'var(--primary-dark)', marginBottom: '4px' }}>
                                    <span style={{ color: 'var(--primary-gold)' }}>الخطوة {item.step} — </span>{item.title}
                                </h4>
                                <p style={{ color: 'var(--gray-500)', fontSize: '0.95rem' }}>{item.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </>
    );
}

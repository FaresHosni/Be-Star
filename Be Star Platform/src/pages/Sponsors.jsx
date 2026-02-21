import eventData from '../config/eventData.json';
import { Trophy, Medal, Radio, Laptop, Tv, Palette, Rocket, Mail } from 'lucide-react';

export default function Sponsors() {
    const { sponsors } = eventData;

    const tiers = {
        platinum: { label: <><Trophy size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px', color: '#ffc107' }} /> الرعاة البلاتينيون</>, items: sponsors.filter((s) => s.tier === 'platinum') },
        gold: { label: <><Medal size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px', color: '#ffd700' }} /> الرعاة الذهبيون</>, items: sponsors.filter((s) => s.tier === 'gold') },
        media: { label: <><Radio size={20} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px', color: 'var(--primary-blue)' }} /> الشركاء الإعلاميون</>, items: sponsors.filter((s) => s.tier === 'media') },
    };

    return (
        <>
            <div className="page-header">
                <h1>الرعاة والشركاء</h1>
                <p>شكراً لشركائنا الذين يدعمون رحلة صناع المحتوى في صعيد مصر</p>
            </div>

            <section className="section">
                <div className="container">
                    {Object.entries(tiers).map(([key, tier]) => (
                        tier.items.length > 0 && (
                            <div className="sponsors-tier" key={key}>
                                <h3>{tier.label}</h3>
                                <div className="sponsors-grid">
                                    {tier.items.map((sponsor) => (
                                        <div className="sponsor-card" key={sponsor.id}>
                                            {sponsor.logo ? (
                                                <img src={sponsor.logo} alt={sponsor.name} />
                                            ) : (
                                                sponsor.name
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}
                </div>
            </section>

            {/* Sponsor Booths */}
            <section className="section" style={{ background: 'var(--gray-50)' }}>
                <div className="container" style={{ textAlign: 'center' }}>
                    <h2 className="section-title">مناطق العرض</h2>
                    <p className="section-subtitle">
                        زُر أجنحة الشركات الراعية واكتشف منتجاتها وخدماتها
                    </p>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                        gap: '20px',
                        maxWidth: '800px',
                        margin: '0 auto',
                    }}>
                        {['منطقة التقنية', 'منطقة الإعلام', 'منطقة التصميم', 'منطقة ريادة الأعمال'].map((zone, i) => (
                            <div key={i} className="card" style={{ textAlign: 'center', padding: '24px' }}>
                                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px', color: 'var(--primary-dark)' }}>
                                    {[<Laptop size={32} />, <Tv size={32} />, <Palette size={32} />, <Rocket size={32} />][i]}
                                </div>
                                <h4 style={{ color: 'var(--primary-dark)' }}>{zone}</h4>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Partnership CTA */}
            <section style={{
                background: 'var(--gradient-hero)',
                padding: '60px 24px',
                textAlign: 'center',
                color: '#fff',
            }}>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '12px' }}>
                    هل تريد أن تكون شريكاً؟
                </h2>
                <p style={{ opacity: 0.7, marginBottom: '24px' }}>
                    انضم لشركائنا وادعم مستقبل صناع المحتوى
                </p>
                <a href="mailto:info@bestar.com" className="btn btn-primary btn-lg">
                    <Mail size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginEnd: '6px' }} /> تواصل معنا للرعاية
                </a>
            </section>
        </>
    );
}

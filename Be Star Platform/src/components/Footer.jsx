import { Link } from 'react-router-dom';

export default function Footer() {
    return (
        <footer className="footer">
            <div className="footer-grid">
                <div className="footer-brand">
                    <h3>⭐ كن نجماً — Be Star</h3>
                    <p>
                        منحة 1000 صانع محتوى بسوهاج. مؤتمر يجمع بين التعلم والتطبيق
                        والتشبيك مع أفضل الخبراء في صناعة المحتوى والإعلام.
                    </p>
                    <p style={{ marginTop: '12px', fontSize: '0.85rem' }}>
                        📍 سوهاج &nbsp;|&nbsp; 📅 قريباً
                    </p>
                </div>

                <div className="footer-links">
                    <h4>روابط سريعة</h4>
                    <Link to="/">الرئيسية</Link>
                    <Link to="/about">عن الحدث</Link>
                    <Link to="/speakers">المتحدثين</Link>
                    <Link to="/sessions">الجلسات</Link>
                    <Link to="/tickets">حجز التذاكر</Link>
                </div>

                <div className="footer-links">
                    <h4>الحدث</h4>
                    <Link to="/sponsors">الرعاة والشركاء</Link>
                    <Link to="/ai-features">مميزات AI</Link>
                    <a href="#">الشروط والأحكام</a>
                    <a href="#">سياسة الخصوصية</a>
                </div>
            </div>

            <div className="footer-bottom">
                <span>© 2026 Be Star — كن نجماً. جميع الحقوق محفوظة.</span>
                <span className="footer-powered">
                    مدعوم بالذكاء الاصطناعي من Mr. AI ⚡
                </span>
            </div>
        </footer>
    );
}

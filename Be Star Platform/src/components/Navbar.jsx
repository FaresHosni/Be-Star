import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        setMobileOpen(false);
    }, [location]);

    const links = [
        { path: '/', label: 'الرئيسية' },
        { path: '/about', label: 'عن الحدث' },
        { path: '/speakers', label: 'المتحدثين' },
        { path: '/sessions', label: 'الجلسات' },
        { path: '/sponsors', label: 'الرعاة' },
        { path: '/ai-features', label: 'مميزات AI' },
    ];

    return (
        <nav className={`navbar${scrolled ? ' scrolled' : ''}`}>
            <div className="navbar-inner">
                <Link to="/" className="navbar-logo">
                    <img src="/logo.jpeg" alt="Be Star Logo" />
                    <span>كن نجماً</span>
                </Link>

                <div className={`navbar-links${mobileOpen ? ' open' : ''}`}>
                    {links.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={location.pathname === link.path ? 'active' : ''}
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>

                <div className="navbar-cta">
                    <Link to="/tickets" className="btn btn-primary">
                        🎫 احجز الآن
                    </Link>
                </div>

                <button
                    className="navbar-mobile-toggle"
                    onClick={() => setMobileOpen(!mobileOpen)}
                >
                    {mobileOpen ? '✕' : '☰'}
                </button>
            </div>
        </nav>
    );
}

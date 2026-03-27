import { Link } from 'react-router-dom';
import { FaHome, FaCreditCard, FaPiggyBank, FaBookOpen, FaTrophy, FaUserCircle } from 'react-icons/fa';
import styles from './menu.module.css';

interface MenuProps {
  user: {
    fullname: string;
    age: number;
    parentName?: string;
  };
}

const Menu = ({ user }: MenuProps) => {
  return (
    <aside className={styles.sidebar}>
      {/* Λογότυπο / Όνομα Εφαρμογής */}
      <div className={styles.logoBox}>
        <h2 className={styles.logoTitle}>PocketWise</h2>
        <p className={styles.logoSubtitle}>Μαθαίνω & Κερδίζω</p>
      </div>

      {/* Σύνδεσμοι Πλοήγησης */}
      <nav className={styles.navLinks}>
        <Link to="/dashboard" className={styles.link}><FaHome className={styles.icon} /> Αρχική</Link>
        <Link to="/card" className={styles.link}><FaCreditCard className={styles.icon} /> Κάρτα</Link>
        <Link to="/savings" className={styles.link}><FaPiggyBank className={styles.icon} /> Αποταμίευση</Link>
        <Link to="/learning" className={styles.link}><FaBookOpen className={styles.icon} /> Μάθηση</Link>
        <Link to="/rewards" className={styles.link}><FaTrophy className={styles.icon} /> Βραβεία</Link>
      </nav>

      {/* Κουτάκι Προφίλ (Κάτω-Κάτω) */}
      <div className={styles.profileBox}>
        <FaUserCircle className={styles.profileAvatar} />
        <div className={styles.profileInfo}>
          <span className={styles.childName}>{user.fullname} ({user.age})</span>
          <span className={styles.parentName}>Γονέας: {user.parentName || 'Γιώργος Π.'}</span>
        </div>
      </div>
    </aside>
  );
};

export default Menu;
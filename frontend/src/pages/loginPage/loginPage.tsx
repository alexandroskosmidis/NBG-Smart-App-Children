// src/pages/loginPage/loginPage.tsx
import { useNavigate } from 'react-router-dom';
import { FaUsers, FaChild } from 'react-icons/fa'; // Εισαγωγή των εικονιδίων
import styles from './loginPage.module.css';

const LoginPage = () => {
  const navigate = useNavigate();

  const mockChildUser = {
    id: 'child-uuid-1234',
    fullname: 'Μαρία Κ.',
    email: 'maria@email.com',
    age: 14,
    parent_id: 'd6874e64-1621-4f9e-b851-4c1206c9e076',
    available_balance: 124.50,
    savings_balance: 45.00,
    total_points: 340
  };

  const handleChildLogin = () => {
    navigate('/dashboard', { state: { user: mockChildUser } });
  };

  const handleParentLogin = () => {
    navigate('/parent-page'); 
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <h1 className={styles.title}>Καλώς ήρθες στο PocketWise!</h1>
        <p className={styles.subtitle}>Επίλεξε ποιος συνδέεται για να συνεχίσεις:</p>

        <div className={styles.cardsWrapper}>
          <div className={styles.roleCard} onClick={handleParentLogin}>
            <FaUsers className={styles.icon} />
            <h2>Γονιός</h2>
            <p>Διαχείριση & Έλεγχος</p>
          </div>

          <div className={styles.roleCard} onClick={handleChildLogin}>
            <FaChild className={styles.icon} />
            <h2>Παιδί</h2>
            <p>Μαθαίνω & Κερδίζω</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
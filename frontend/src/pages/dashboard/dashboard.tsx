import { useLocation } from 'react-router-dom';
import Menu from '../../components/menu/menu';
import Goals from '../../components/goals/goals';  
import Transactions from '../../components/transactions/transactions';
import styles from './dashboard.module.css';


const Dashboard = () => {
  const location = useLocation();
  
  // Πιάνουμε τα δεδομένα του χρήστη, αλλιώς βάζουμε κάποια default για να μη σκάσει
  const user = location.state?.user || {
    fullname: 'Μαρία Κ.',
    age: 14,
    parentName: 'Γιώργος Π.',
  };

  return (
    <div className={styles.dashboardContainer}>
      <Menu user={user} />
      
      <main className={styles.mainContent}>
        <header className={styles.header}>
          <h1>Πίνακας Ελέγχου</h1>
          <p>Γεια σου, {user.fullname}! 👋</p>
        </header>
        
        <Goals />
        <Transactions />
      </main>
    </div>
  );
};

export default Dashboard;
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiGift, FiShoppingBag, FiDollarSign } from 'react-icons/fi';
import { IoGameControllerOutline, IoFastFoodOutline } from 'react-icons/io5';
import styles from './transactions.module.css';

interface Transaction { id: string; child_id: string; title: string; amount: string | number; category: string; type: 'income' | 'expense'; inserted_at: string; }

const Transactions = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const CHILD_ID = 'ΒΑΛΕ_ΤΟ_ID_ΤΟΥ_ΠΑΙΔΙΟΥ_ΕΔΩ';

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/children/${CHILD_ID}/transactions`);
        if (response.ok) {
          const data = await response.json();
          setTransactions(data);
        }
      } catch (error) {
        console.error("Σφάλμα:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  // Υπολογισμός Ημερών (Σήμερα, Χθες, Χ ημέρες)
  const formatTimeAgo = (dateString: string) => {
    const txDate = new Date(dateString);
    const today = new Date();
    txDate.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);
    
    const diffTime = today.getTime() - txDate.getTime();
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Σήμερα';
    if (diffDays === 1) return 'Χθες';
    return `${diffDays} ημέρες`;
  };

  // Εικονίδιο και Χρώμα ανάλογα με την κατηγορία/τύπο (όπως στη φωτογραφία)
  const getIconStyle = (category: string, type: string) => {
    if (type === 'income') {
      return { icon: <FiGift />, bgColor: '#E6F2ED', color: '#10B981' }; // Πράσινο
    }
    switch (category.toLowerCase()) {
      case 'gaming': return { icon: <IoGameControllerOutline />, bgColor: '#FDECE8', color: '#E87D65' }; // Πορτοκαλί
      case 'shopping': return { icon: <FiShoppingBag />, bgColor: '#FEEDE6', color: '#D9735A' }; // Απαλό κεραμιδί/σομόν (από φωτό)
      case 'food': return { icon: <IoFastFoodOutline />, bgColor: '#FEF4E6', color: '#EAA13A' };
      default: return { icon: <FiDollarSign />, bgColor: '#EAEFF4', color: '#627D98' };
    }
  };

  return (
    <div className={styles.transactionsWidget}>
      <div className={styles.header}>
        <h3 className={styles.title}>Πρόσφατες Κινήσεις 💸</h3>
        <Link to="/transactions" className={styles.seeAllBtn}>Όλες</Link>
      </div>

      <div className={styles.listCard}>
        {loading ? (
          <p className={styles.loadingText}>Φόρτωση κινήσεων...</p>
        ) : (
          transactions.map((tx, index) => {
            const { icon, bgColor, color } = getIconStyle(tx.category, tx.type);
            const isLast = index === transactions.length - 1;
            const formattedAmount = Number(tx.amount).toFixed(2);

            return (
              <div key={tx.id} className={`${styles.transactionRow} ${!isLast ? styles.borderBottom : ''}`}>
                
                <div className={styles.iconBox} style={{ backgroundColor: bgColor, color: color }}>
                  {icon}
                </div>
                
                <div className={styles.details}>
                  <h4 className={styles.txTitle}>{tx.title}</h4>
                  <span className={styles.txDate}>{formatTimeAgo(tx.inserted_at)}</span>
                </div>
                
                <div className={tx.type === 'income' ? styles.amountIncome : styles.amountExpense}>
                  {tx.type === 'income' ? '+' : '-'}€{formattedAmount}
                </div>
                
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Transactions;
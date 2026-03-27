import { useState, useEffect } from 'react';
import { FiEye } from 'react-icons/fi';
import { FaPiggyBank } from 'react-icons/fa';
import { supabase } from '../../utils/supabase';
import styles from '../card/card.module.css'; // Χρησιμοποιούμε το ΙΔΙΟ CSS αρχείο!

const SavingCard = () => {
  const [savings, setSavings] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  const CHILD_ID = 'ΒΑΛΕ_ΕΔΩ_ΤΟ_ID_ΤΗΣ_ΜΑΡΙΑΣ';

  useEffect(() => {
    const fetchSavings = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('children')
        .select('savings_balance')
        .eq('id', CHILD_ID)
        .single();
        
      if (data) setSavings(data.savings_balance);
      if (error) console.error("Σφάλμα αποταμίευσης:", error);
      
      setLoading(false);
    };

    fetchSavings();
  }, []);

  if (loading) return <div className={`${styles.card} ${styles.savingsCard}`}>Φόρτωση...</div>;

  return (
    <div className={`${styles.card} ${styles.savingsCard}`}>
      <div className={styles.header}>
        <span className={styles.title}>Αποταμιεύσεις</span>
        <FiEye className={styles.eyeIcon} />
      </div>
      
      <div className={styles.balance}>
        €{savings.toFixed(2).replace('.', ',')}
      </div>

      <div className={styles.statsRow}>
        <div className={styles.statBadge}>
          <FaPiggyBank className={styles.statIcon} style={{marginRight: '8px'}} />
          <span>Συνέχισε έτσι!</span>
        </div>
      </div>
    </div>
  );
};

export default SavingCard;
import { Link } from 'react-router-dom';
import styles from './goals.module.css';

// 1. Προσαρμόζουμε το Interface ώστε να ταιριάζει ΑΚΡΙΒΩΣ με το SQL table σου
interface Goal {
  id: string;
  child_id: string;
  item_name: string;
  category: 'gaming' | 'shopping' | 'food' | 'general';
  target_amount: number;
  current_saved: number;
  ai_suggestion?: string | null; // Προαιρετικό γιατί μπορεί να είναι null στη βάση
  inserted_at: string;
}

const Goals = () => {
  // 2. Ενημερώνουμε τα Mock δεδομένα με τα σωστά κλειδιά (keys) της βάσης
  const mockGoals: Goal[] = [
    { 
      id: '1', 
      child_id: 'child-uuid-1234', 
      item_name: 'Nintendo Switch', 
      current_saved: 180, 
      target_amount: 300, 
      category: 'gaming',
      ai_suggestion: 'Αν αποταμιεύεις €5 την εβδομάδα από το χαρτζιλίκι σου, θα το πάρεις σε 6 μήνες!',
      inserted_at: '2026-03-27T10:00:00Z'
    },
    { 
      id: '2', 
      child_id: 'child-uuid-1234', 
      item_name: 'Νέο Κινητό', 
      current_saved: 45, 
      target_amount: 200, 
      category: 'shopping',
      inserted_at: '2026-03-20T10:00:00Z'
    },
    { 
      id: '3', 
      child_id: 'child-uuid-1234', 
      item_name: 'Σχολική Εκδρομή', 
      current_saved: 60, 
      target_amount: 80, 
      category: 'general',
      inserted_at: '2026-03-15T10:00:00Z'
    }
  ];

  // Η συνάρτηση παραμένει ίδια, επιλέγει στυλ με βάση το category
  const getCategoryDetails = (category: string) => {
    switch (category) {
      case 'gaming': return { emoji: '🎮', color: '#F28C28' }; // Πορτοκαλί
      case 'shopping': return { emoji: '🛍️', color: '#9B66CC' }; // Μωβ
      case 'food': return { emoji: '🍔', color: '#E4A11B' };
      case 'general':
      default: return { emoji: '🎯', color: '#5A9C86' }; // Το βασικό teal
    }
  };

  return (
    <div className={styles.goalsWidget}>
      <div className={styles.header}>
        <h3 className={styles.title}>Στόχοι Αποταμίευσης 🎯</h3>
        <Link to="/savings" className={styles.newBtn}>+ Νέος</Link>
      </div>

      <div className={styles.goalsList}>
        {mockGoals.map((goal) => {
          const { emoji, color } = getCategoryDetails(goal.category);
          // 3. Υπολογίζουμε το ποσοστό με τα νέα ονόματα μεταβλητών
          const progressPercentage = Math.round((goal.current_saved / goal.target_amount) * 100);

          return (
            <div key={goal.id} className={styles.goalCard}>
              <div className={styles.goalInfo}>
                <div className={styles.emojiBox}>{emoji}</div>
                <div className={styles.textDetails}>
                  {/* 4. Εμφανίζουμε το item_name αντί για title */}
                  <h4 className={styles.goalTitle}>{goal.item_name}</h4>
                  <span className={styles.amounts}>
                    €{goal.current_saved.toFixed(0)} / €{goal.target_amount.toFixed(0)}
                  </span>
                </div>
                <div className={styles.percentage} style={{ color: color }}>
                  {progressPercentage}%
                </div>
              </div>

              <div className={styles.progressBarTrack}>
                <div 
                  className={styles.progressBarFill} 
                  style={{ width: `${progressPercentage}%`, backgroundColor: color }}
                ></div>
              </div>
              
              {/* (Προαιρετικό) Αν υπάρχει AI συμβουλή, μπορούμε να την εμφανίσουμε διακριτικά από κάτω */}
              {goal.ai_suggestion && (
                <div style={{ marginTop: '12px', fontSize: '12px', color: '#7B968B', fontStyle: 'italic' }}>
                  💡 {goal.ai_suggestion}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Goals;
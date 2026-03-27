import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './goals.module.css';

interface Goal { id: string; child_id: string; item_name: string; category: 'gaming' | 'shopping' | 'food' | 'general'; target_amount: number; current_saved: number; ai_suggestion?: string | null; inserted_at: string; }

const Goals = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const CHILD_ID = 'ΒΑΛΕ_ΤΟ_ID_ΤΟΥ_ΠΑΙΔΙΟΥ_ΕΔΩ';

  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/children/${CHILD_ID}/goals`);
        if (response.ok) {
          const data = await response.json();
          setGoals(data);
        }
      } catch (error) {
        console.error("Σφάλμα:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchGoals();
  }, []);
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
        {loading ? (
          <div>Φόρτωση...</div>
        ) : goals.length === 0 ? (
          <div>Δεν υπάρχουν στόχοι.</div>
        ) : (
          goals.map((goal) => {
            const { emoji, color } = getCategoryDetails(goal.category);
            const progressPercentage = Math.round((goal.current_saved / goal.target_amount) * 100);

            return (
              <div key={goal.id} className={styles.goalCard}>
                <div className={styles.goalInfo}>
                  <div className={styles.emojiBox}>{emoji}</div>
                  <div className={styles.textDetails}>
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
                {goal.ai_suggestion && (
                  <div style={{ marginTop: '12px', fontSize: '12px', color: '#7B968B', fontStyle: 'italic' }}>
                    💡 {goal.ai_suggestion}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Goals;
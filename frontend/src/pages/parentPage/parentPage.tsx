import { useState } from 'react';
import { FaUser } from 'react-icons/fa';
import styles from './parentPage.module.css';

// Interfaces βάσει της SQL βάσης σου
interface ParentProfile {
  id: string;
  parent_name: string;
  email: string;
}

interface SpendingCap {
  id: string;
  category: string;
  limit_amount: number;
  current_spent: number;
  period: string;
}

const ParentPage = () => {
  // Mock Δεδομένα Γονέα (Από το INSERT σου)
  const parent: ParentProfile = {
    id: 'd6874e64-1621-4f9e-b851-4c1206c9e076',
    parent_name: 'Γιώργος Παπαδόπουλος',
    email: 'george@email.com'
  };

  // Mock Δεδομένα Ορίων (Από το INSERT σου)
  const [caps, setCaps] = useState<SpendingCap[]>([
    { id: 'cap1', category: 'Gaming', limit_amount: 50.00, current_spent: 15.00, period: 'monthly' },
    { id: 'cap2', category: 'Food', limit_amount: 30.00, current_spent: 12.00, period: 'monthly' }
  ]);

  // State για τη Φόρμα
  const [formData, setFormData] = useState({
    category: 'General',
    limit_amount: '',
    period: 'monthly'
  });

  // Διαχείριση αλλαγών στη φόρμα
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Υποβολή φόρμας (Προσομοίωση αποθήκευσης στη βάση)
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.limit_amount) return;

    const newCap: SpendingCap = {
      id: Math.random().toString(), // Τυχαίο ID για το mock
      category: formData.category,
      limit_amount: parseFloat(formData.limit_amount),
      current_spent: 0, // Ξεκινάει από 0
      period: formData.period
    };

    setCaps([...caps, newCap]);
    setFormData({ ...formData, limit_amount: '' }); // Καθαρισμός πεδίου ποσού
    alert('Το όριο αποθηκεύτηκε με επιτυχία!');
  };

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        
        {/* Κάρτα Προφίλ Γονέα */}
        <div className={styles.profileCard}>
          <FaUser className={styles.icon} />
          <div className={styles.profileInfo}>
            <h2>{parent.parent_name}</h2>
            <p>{parent.email}</p>
          </div>
        </div>

        <div className={styles.dashboardGrid}>
          {/* Φόρμα Δημιουργίας Νέου Ορίου */}
          <div className={styles.formCard}>
            <h3>Ορισμός Νέου Ορίου Κατανάλωσης</h3>
            <p className={styles.subtitle}>Επίλεξε κατηγορία και ποσό για τη Μαρία Κ.</p>
            
            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label>Κατηγορία</label>
                <select name="category" value={formData.category} onChange={handleChange}>
                  <option value="General">Γενικά (General)</option>
                  <option value="Gaming">Παιχνίδια (Gaming)</option>
                  <option value="Food">Φαγητό (Food)</option>
                  <option value="Shopping">Ψώνια (Shopping)</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Όριο Ποσού (€)</label>
                <input 
                  type="number" 
                  name="limit_amount" 
                  min="1" 
                  step="0.5" 
                  placeholder="π.χ. 20.50" 
                  value={formData.limit_amount} 
                  onChange={handleChange} 
                  required 
                />
              </div>

              <div className={styles.formGroup}>
                <label>Χρονική Περίοδος</label>
                <select name="period" value={formData.period} onChange={handleChange}>
                  <option value="daily">Ημερήσιο</option>
                  <option value="weekly">Εβδομαδιαίο</option>
                  <option value="monthly">Μηνιαίο</option>
                </select>
              </div>

              <button type="submit" className={styles.submitBtn}>Αποθήκευση Ορίου</button>
            </form>
          </div>

          {/* Λίστα με τα τρέχοντα όρια */}
          <div className={styles.capsListCard}>
            <h3>Ενεργά Όρια της Μαρίας</h3>
            <div className={styles.capsList}>
              {caps.map(cap => (
                <div key={cap.id} className={styles.capItem}>
                  <div className={styles.capHeader}>
                    <span className={styles.capCategory}>{cap.category}</span>
                    <span className={styles.capPeriod}>
                      {cap.period === 'monthly' ? 'Μήνα' : cap.period === 'weekly' ? 'Εβδομάδα' : 'Ημέρα'}
                    </span>
                  </div>
                  <div className={styles.capProgress}>
                    <div className={styles.capAmounts}>
                      <span>Ξόδεψε: €{cap.current_spent.toFixed(2)}</span>
                      <span>Όριο: €{cap.limit_amount.toFixed(2)}</span>
                    </div>
                    {/* Απλή μπάρα προόδου */}
                    <div className={styles.progressBar}>
                      <div 
                        className={styles.progressFill} 
                        style={{ width: `${Math.min((cap.current_spent / cap.limit_amount) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ParentPage;
import { useState, useEffect } from 'react';
import { FaUser } from 'react-icons/fa';
import styles from './parentPage.module.css';

interface ParentProfile { id: string; parent_name: string; email: string; }
interface SpendingCap { id: string; category: string; limit_amount: number; current_spent: number; period: string; }

const ParentPage = () => {
  const PARENT_ID = 'd6874e64-1621-4f9e-b851-4c1206c9e076'; // Προσωρινά καρφωτό
  const CHILD_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'; // Βάλε το ID της Μαρίας

  const [parent, setParent] = useState<ParentProfile | null>(null);
  const [caps, setCaps] = useState<SpendingCap[]>([]);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({ category: 'General', limit_amount: '', period: 'monthly' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Τραβάμε ταυτόχρονα το προφίλ και τα όρια από το backend μας
        const [parentRes, capsRes] = await Promise.all([
          fetch(`http://localhost:8000/api/parents/${PARENT_ID}`),
          fetch(`http://localhost:8000/api/parents/${PARENT_ID}/caps`)
        ]);

        if (parentRes.ok) setParent(await parentRes.json());
        if (capsRes.ok) setCaps(await capsRes.json());
      } catch (error) {
        console.error("Σφάλμα σύνδεσης με το backend:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.limit_amount) return;

    try {
      const response = await fetch('http://localhost:8000/api/caps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: PARENT_ID,
          child_id: CHILD_ID,
          category: formData.category,
          limit_amount: parseFloat(formData.limit_amount),
          period: formData.period
        })
      });

      if (response.ok) {
        const newCap = await response.json();
        setCaps([...caps, newCap]); // Προσθήκη του νέου ορίου στη λίστα μας
        setFormData({ ...formData, limit_amount: '' });
        alert('Το όριο αποθηκεύτηκε!');
      } else {
        alert('Αποτυχία αποθήκευσης.');
      }
    } catch (error) {
      console.error("Σφάλμα:", error);
    }
  };

  if (loading) return <div>Φόρτωση...</div>;
  if (!parent) return <div>Δεν βρέθηκε προφίλ.</div>;

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.profileCard}>
          <FaUser className={styles.icon} />
          <div className={styles.profileInfo}>
            <h2>{parent.parent_name}</h2>
            <p>{parent.email}</p>
          </div>
        </div>

        <div className={styles.dashboardGrid}>
          <div className={styles.formCard}>
            <h3>Ορισμός Νέου Ορίου Κατανάλωσης</h3>
            <form onSubmit={handleSubmit} className={styles.form}>
              <label>
                Κατηγορία:
                <select name="category" value={formData.category} onChange={handleChange}>
                  <option value="General">Γενικά</option>
                  <option value="Gaming">Gaming</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Food">Φαγητό</option>
                </select>
              </label>
              <label>
                Ποσό Ορίου (€):
                <input
                  type="number"
                  name="limit_amount"
                  value={formData.limit_amount}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
                  required
                />
              </label>
              <label>
                Περίοδος:
                <select name="period" value={formData.period} onChange={handleChange}>
                  <option value="monthly">Μηνιαίο</option>
                  <option value="weekly">Εβδομαδιαίο</option>
                </select>
              </label>
              <button type="submit" className={styles.submitBtn}>Αποθήκευση</button>
            </form>
          </div>

          <div className={styles.capsListCard}>
            <h3>Ενεργά Όρια</h3>
            <div className={styles.capsList}>
              {caps.length === 0 ? <p>Δεν υπάρχουν ενεργά όρια.</p> : caps.map(cap => (
                <div key={cap.id} className={styles.capItem}>
                  <div className={styles.capCategory}><b>Κατηγορία:</b> {cap.category}</div>
                  <div className={styles.capAmounts}>
                    <span><b>Όριο:</b> €{cap.limit_amount.toFixed(2)}</span>
                    <span><b>Ξοδεύτηκαν:</b> €{cap.current_spent.toFixed(2)}</span>
                  </div>
                  <div className={styles.capPeriod}><b>Περίοδος:</b> {cap.period === 'monthly' ? 'Μηνιαίο' : 'Εβδομαδιαίο'}</div>
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
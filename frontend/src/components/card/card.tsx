// import { useState, useEffect } from 'react';
// import { FiEye, FiArrowUpRight, FiArrowDownRight } from 'react-icons/fi';
// import styles from './card.module.css';

// const Card = () => {
//   const [balance, setBalance] = useState<number>(0);
//   const [income, setIncome] = useState<number>(0);
//   const [expense, setExpense] = useState<number>(0);
//   const [loading, setLoading] = useState(true);

//   // Προσωρινό ID παιδιού
//   const CHILD_ID = 'ΒΑΛΕ_ΕΔΩ_ΤΟ_ID_ΤΗΣ_ΜΑΡΙΑΣ';

//   useEffect(() => {
//     const fetchCardData = async () => {
//       setLoading(true);
      
//       // 1. Τραβάμε το διαθέσιμο υπόλοιπο
//       const { data: childData, error: childError } = await supabase
//         .from('children')
//         .select('available_balance')
//         .eq('id', CHILD_ID)
//         .single();
        
//       if (childData) setBalance(childData.available_balance);
//       if (childError) console.error("Σφάλμα υπολοίπου:", childError);

//       // 2. Τραβάμε τις συναλλαγές για να υπολογίσουμε έσοδα/έξοδα
//       const { data: txData, error: txError } = await supabase
//         .from('transactions')
//         .select('amount, type')
//         .eq('child_id', CHILD_ID);

//       if (txData) {
//         let totalIncome = 0;
//         let totalExpense = 0;

//         txData.forEach(tx => {
//           if (tx.type === 'income') {
//             totalIncome += Number(tx.amount);
//           } else if (tx.type === 'expense') {
//             totalExpense += Number(tx.amount);
//           }
//         });

//         setIncome(totalIncome);
//         setExpense(totalExpense);
//       }
//       if (txError) console.error("Σφάλμα συναλλαγών:", txError);

//       setLoading(false);
//     };

//     fetchCardData();
//   }, []);

//   if (loading) return <div className={`${styles.card} ${styles.mainCard}`}>Φόρτωση...</div>;

//   return (
//     <div className={`${styles.card} ${styles.mainCard}`}>
//       <div className={styles.header}>
//         <span className={styles.title}>Διαθέσιμο Υπόλοιπο</span>
//         <FiEye className={styles.eyeIcon} />
//       </div>
      
//       <div className={styles.balance}>
//         €{balance.toFixed(2).replace('.', ',')}
//       </div>

//       <div className={styles.statsRow}>
//         <div className={styles.statBadge}>
//           <FiArrowUpRight className={styles.statIcon} />
//           <span>+€{income.toFixed(2).replace('.', ',')} εισροή</span>
//         </div>
//         <div className={styles.statBadge}>
//           <FiArrowDownRight className={styles.statIcon} />
//           <span>-€{expense.toFixed(2).replace('.', ',')} έξοδα</span>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Card;
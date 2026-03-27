
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import Dashboard from './pages/dashboard/dashboard';
import LoginPage from './pages/loginPage/loginPage';
// import Quiz from './pages/quiz/quiz';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Η αρχική σελίδα θα είναι το Login (ή το Dashboard αν είναι ήδη συνδεδεμένος) */}
        <Route path="/" element={<LoginPage />} />
        
        {/* Οι υπόλοιπες σελίδες */}
        {/* <Route path="/dashboard" element={<Dashboard />} /> */}
        {/* <Route path="/quiz" element={<Quiz />} /> */}
        
        {/* Αν ο χρήστης βάλει λάθος URL, μπορείς να τον στείλεις κάπου αλλού */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </Router>
  );
}

export default App;
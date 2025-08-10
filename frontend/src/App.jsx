import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header'; 
import Register_Form from './components/Register_Form'; 
import NotFoundPage from './components/notfoundpage';
import HeroSection from './components/LandingPage';
import Login_Form from './components/Login_Form';
import MainDashboard from './components/Dashboard/MainDashboard';
import Workout_Form_Layout from './components/layouts/Workout_Form_Layout';


function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<HeroSection />} />
        <Route path="/register" element={<Register_Form />} />
        <Route path= "*" element={<NotFoundPage/>} />
        <Route path="Login" element={<Login_Form/>} />
        <Route path="/Dashboard/MainDashboard" element={<MainDashboard/>} />
        <Route path="Workout_Form" element={<Workout_Form_Layout />} />
      </Routes>
    </Router>
  );
}

export default App;

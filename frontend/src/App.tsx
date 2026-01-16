import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login"
import Register from "./pages/Register"
import NotFound from "./pages/NotFound"
import Home from "./pages/Home"
import ProtectedRoute from "./components/protected_route";
import type React from "react";


// Navigate to login page on logout
const Logout: React.FC = () => {
  localStorage.clear()
  return <Navigate to="/login" />
}

// Clear local storage before registering to avoid sending pre-existing tokens
const PreRegister: React.FC = () => {
  localStorage.clear()
  return <Register />
}



const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login/>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/register" element={<PreRegister />} />
        <Route path="*" element={<NotFound />} />

      </Routes>
    </BrowserRouter>
  )
}

export default App;

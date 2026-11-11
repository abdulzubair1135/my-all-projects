import { useEffect, useState, useContext } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";

import { BrowserRouter, Routes, Route } from "react-router-dom";

// ✅ FIXED PATHS
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";

import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";

// ✅ components
import DMChat from "./components/DMChat";
import SearchUser from "./components/SearchUser";
import Profile from "./components/Profile";

import { ThemeContext } from "./context/ThemeContext";

function App() {
  const [user, setUser] = useState(null);
  const { dark, toggleTheme } = useContext(ThemeContext);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    return () => unsubscribe();
  }, []);

  return (
    <BrowserRouter>
      <div
        style={{
          background: dark ? "#111" : "#fff",
          color: dark ? "#fff" : "#000",
          minHeight: "100vh",
        }}
      >
        <h1>🔥 Interact App</h1>

        <button onClick={toggleTheme}>🌙 Toggle</button>

        <Routes>
          {/* PUBLIC */}
          <Route
            path="/login"
            element={
              <PublicRoute user={user}>
                <Login />
              </PublicRoute>
            }
          />
          <Route path="/dm/:userId" element={<DMChat />} />
<Route path="/profile/:id" element={<Profile />} />
          <Route
            path="/signup"
            element={
              <PublicRoute user={user}>
                <Signup />
              </PublicRoute>
            }
          />

          {/* PROTECTED */}
          <Route
            path="/"
            element={
              <ProtectedRoute user={user}>
                <Dashboard user={user} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dm/:email"
            element={
              <ProtectedRoute user={user}>
                <DMChat />
              </ProtectedRoute>
            }
          />

          <Route
            path="/search"
            element={
              <ProtectedRoute user={user}>
                <SearchUser />
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute user={user}>
                <Profile />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
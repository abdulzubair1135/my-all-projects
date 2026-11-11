import { useState, useEffect } from "react";
import { signInWithEmailAndPassword, onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
  const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
    setUser(currentUser);

    if (currentUser) {
      navigate("/"); // 🔥 agar already login hai → dashboard
    }
  });

  return () => unsubscribe();
}, []);
  const handleGoogleLogin = async () => {
  const provider = new GoogleAuthProvider();

  try {
    const result = await signInWithPopup(auth, provider);
    console.log(result.user);

    alert("Google Login Successful 🚀");
    navigate("/"); // dashboard
  } catch (error) {
    alert(error.message);
  }
};
  const handleLogin = async () => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      alert("Login Successful 🚀");
      navigate("/");
    } catch (error) {
      alert("Error: " + error.message);
    }
  };

  const handleLogout = () => {
    signOut(auth)
      .then(() => {
        alert("Logged out");
        navigate("/login");
      })
      .catch((err) => alert(err.message));
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Login</h2>

      {user && <h3>Welcome {user.email} 👋</h3>}

      <input
        type="email"
        placeholder="Email"
        onChange={(e) => setEmail(e.target.value)}
      /><br /><br />

      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      /><br /><br />

      <button onClick={handleLogin}>Login</button>

      <br /><br />
      <br /><br />
        <button onClick={handleGoogleLogin}>
          Continue with Google
        </button>
      {/* ✅ Signup navigation */}
      <p>Don't have an account?</p>
      <button onClick={() => navigate("/signup")}>Go to Signup</button>

      <br /><br />

      {user && <button onClick={handleLogout}>Logout</button>}
    </div>
  );
}

export default Login;
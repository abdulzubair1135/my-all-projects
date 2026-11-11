import { useState } from "react";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth, db } from "../firebase"; // ✅ single import
import { useNavigate } from "react-router-dom";
import { setDoc, doc } from "firebase/firestore";

function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleSignup = async () => {
    try {
      const res = await createUserWithEmailAndPassword(auth, email, password);

    await setDoc(doc(db, "users", res.user.uid), {
  email: email,
  bio: "Hey 👋 I am new!",
  avatar: "😎",
  following: [],
  followers: [] // ✅ ADD THIS
});

      alert("Signup Successful 🚀");
      navigate("/");
    } catch (error) {
      alert("Error: " + error.message);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Signup</h2>

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

      <button onClick={handleSignup}>Signup</button>

      <br /><br />

      <p>Already have an account?</p>
      <button onClick={() => navigate("/login")}>Go to Login</button>
    </div>
  );
}

export default Signup;
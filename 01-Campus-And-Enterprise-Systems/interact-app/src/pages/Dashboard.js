import { signOut } from "firebase/auth";
import Chat from "../components/Chat";
import Feed from "../components/Feed";
import Post from "../components/Post";
import { auth } from "../firebase";


import { useNavigate } from "react-router-dom"; // ✅ add
function Dashboard({ user }) {
  const navigate = useNavigate(); // ✅ add

  const handleLogout = () => {
    signOut(auth)
      .then(() => {
        alert("Logged out");
        navigate("/login"); // 🔥 IMPORTANT
      })
      .catch((err) => alert(err.message));
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>🎉 Dashboard</h2>
      <h3>Welcome {user.email} 👋</h3>
     <h4>👤 Profile</h4>
    <button onClick={() => navigate("/search")}>🔍 Search Users</button>
    <button onClick={() => navigate("/profile")}>👤 Profile</button>
    <button onClick={() => navigate(`/dm/test@gmail.com`)}>💬 DM Test</button>

      <Post user={user} />
      <Chat />
      <Feed />
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;
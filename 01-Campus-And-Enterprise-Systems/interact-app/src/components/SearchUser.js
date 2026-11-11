import { useState, useEffect } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  getDocs,
  doc,
  setDoc,
  arrayUnion,
  arrayRemove,
  onSnapshot
} from "firebase/firestore";
import { useNavigate } from "react-router-dom";

function SearchUser() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [currentUser, setCurrentUser] = useState(null);

  const navigate = useNavigate();

  // 🔥 Fetch all users
  useEffect(() => {
    const fetchUsers = async () => {
      const snap = await getDocs(collection(db, "users"));

      const data = snap.docs.map((doc) => ({
        id: doc.id,
        ...doc.data()
      }));

      setUsers(data);
    };

    fetchUsers();
  }, []);

  // 🔥 Realtime current user (for follow UI)
  useEffect(() => {
    const ref = doc(db, "users", auth.currentUser.uid);

    const unsub = onSnapshot(ref, (snap) => {
      setCurrentUser(snap.data());
    });

    return () => unsub();
  }, []);

  // ✅ FOLLOW
  const handleFollow = async (userId) => {
    await setDoc(
      doc(db, "users", auth.currentUser.uid),
      {
        following: arrayUnion(userId)
      },
      { merge: true }
    );

    await setDoc(
      doc(db, "users", userId),
      {
        followers: arrayUnion(auth.currentUser.uid)
      },
      { merge: true }
    );
  };

  // ❌ UNFOLLOW
  const handleUnfollow = async (userId) => {
    await setDoc(
      doc(db, "users", auth.currentUser.uid),
      {
        following: arrayRemove(userId)
      },
      { merge: true }
    );

    await setDoc(
      doc(db, "users", userId),
      {
        followers: arrayRemove(auth.currentUser.uid)
      },
      { merge: true }
    );
  };

  // 🔍 SAFE FILTER (NO CRASH)
  const filtered = users.filter((u) => {
    if (!u?.email) return false;

    return (
      u.email.toLowerCase().includes(search.toLowerCase()) &&
      u.id !== auth.currentUser.uid
    );
  });

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: "auto" }}>
      <h2>🔍 Search Users</h2>

      <input
        placeholder="Search by email..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          padding: 12,
          width: "100%",
          borderRadius: 8,
          border: "1px solid #ccc",
          marginBottom: 20
        }}
      />

      {filtered.length === 0 && <p>No users found 😢</p>}

      {filtered.map((u) => {
        const isFollowing = currentUser?.following?.includes(u.id);

        return (
          <div
            key={u.id}
            style={{
              padding: 15,
              marginBottom: 15,
              borderRadius: 12,
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}
          >
            {/* USER INFO */}
            <div>
              <h4 style={{ margin: 0 }}>
                {u.avatar || "👤"} {u.email || "No Email"}
              </h4>
            </div>

            {/* ACTIONS */}
            <div style={{ display: "flex", gap: 10 }}>
              {isFollowing ? (
                <button onClick={() => handleUnfollow(u.id)}>
                  ❌ Unfollow
                </button>
              ) : (
                <button onClick={() => handleFollow(u.id)}>
                  ➕ Follow
                </button>
              )}

              <button onClick={() => navigate(`/dm/${u.id}`)}>
                💬
              </button>

              <button onClick={() => navigate(`/profile/${u.id}`)}>
                👤
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default SearchUser;
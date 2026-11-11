import { useEffect, useState } from "react";
import { db } from "../firebase";
import {
  doc,
  getDoc,
  collection,
  query,
  where,
  getDocs
} from "firebase/firestore";
import { useParams } from "react-router-dom";

function Profile() {
  const { id } = useParams();

  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const load = async () => {
      const snap = await getDoc(doc(db, "users", id));
      setUser(snap.data());

      const q = query(
        collection(db, "posts"),
        where("userId", "==", id)
      );

      const postSnap = await getDocs(q);
      setPosts(postSnap.docs.map(d => d.data()));
    };

    load();
  }, [id]);

  if (!user) return <p>Loading...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h2>{user.avatar} {user.email}</h2>
      <p>{user.bio}</p>

      <p>Followers: {user.followers?.length || 0}</p>
      <p>Following: {user.following?.length || 0}</p>

      <h3>Posts</h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
        {posts.map((p, i) => (
          <div key={i} style={{ border: "1px solid gray", padding: 10 }}>
            {p.text}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Profile;
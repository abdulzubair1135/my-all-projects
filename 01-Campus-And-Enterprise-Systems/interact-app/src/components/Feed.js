import { useEffect, useState } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  onSnapshot,
  query,
  orderBy,
  doc,
  updateDoc,
  increment,
  arrayUnion,
  arrayRemove,
  deleteDoc
} from "firebase/firestore";

function Feed() {
  const [posts, setPosts] = useState([]);
  const [commentText, setCommentText] = useState("");

 useEffect(() => {
  const q = query(collection(db, "posts"), orderBy("createdAt", "desc"));

  const unsubscribe = onSnapshot(q, (snapshot) => {
    const now = Date.now();

    const data = snapshot.docs
      .map(doc => ({
        id: doc.id,
        ...doc.data()
      }))
      .filter(post => {
        if (!post.createdAt) return false;

        const postTime = post.createdAt.toDate().getTime();
        return now - postTime < 24 * 60 * 60 * 1000;
      });

    setPosts(data);
  });

  return () => unsubscribe(); // ✅ only once
}, []);
    

  const handleLike = async (post) => {
    const postRef = doc(db, "posts", post.id);
    const userEmail = auth.currentUser.email;

    if (post.likedBy?.includes(userEmail)) {
      await updateDoc(postRef, {
        likes: increment(-1),
        likedBy: arrayRemove(userEmail),
      });
    } else {
      await updateDoc(postRef, {
        likes: increment(1),
        likedBy: arrayUnion(userEmail),
      });
    }
  };

  const handleDelete = async (post) => {
    if (post.user !== auth.currentUser.email) {
      return alert("You can't delete this post 😅");
    }

    await deleteDoc(doc(db, "posts", post.id));
  };

  const handleComment = async (post) => {
    if (!commentText) return;

    const postRef = doc(db, "posts", post.id);

    await updateDoc(postRef, {
      comments: arrayUnion({
        text: commentText,
        user: auth.currentUser.email,
      }),
    });

    setCommentText("");
  };

  return (
    <div style={{
  borderRadius: 12,
  padding: 15,
  marginBottom: 15,
  boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
}}>
      <h3>📺 Live Feed</h3>

      {posts.map((post) => (
        <div key={post.id} style={{ border: "1px solid gray", margin: 10, padding: 10 }}>
          <p>{post.text}</p>
          <small>by {post.user}</small>

          <br />

          ❤️ {post.likes || 0}

          <br />

          <button onClick={() => handleLike(post)}>
            {post.likedBy?.includes(auth.currentUser.email)
              ? "💔 Unlike"
              : "❤️ Like"}
          </button>

          <br />

          {post.user === auth.currentUser.email && (
            <button onClick={() => handleDelete(post)}>🗑 Delete</button>
          )}

          <br />

          <input
            type="text"
            placeholder="Write comment..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
          />

          <button onClick={() => handleComment(post)}>Comment</button>

          {post.comments?.map((c, i) => (
            <p key={i}>
              💬 {c.text} — <b>{c.user}</b>
            </p>
          ))}
        </div>
      ))}
    </div>
  );
}

export default Feed;
import { useState } from "react";
import { db } from "../firebase";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";

function Post({ user }) {
  const [text, setText] = useState("");

  const handlePost = async () => {
    if (!text) return alert("Write something 😅");

    try {
      await addDoc(collection(db, "posts"), {
        text: text,
        user: user.email,
        createdAt: serverTimestamp(), // 🔥 IMPORTANT
        likes: 0,
        comments: [],
        likedBy: []
      });

      alert("Post added 🚀");
      setText("");
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <h3>Create Post</h3>

      <input
        type="text"
        placeholder="Write something..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={handlePost}>Post</button>
    </div>
  );
}

export default Post;
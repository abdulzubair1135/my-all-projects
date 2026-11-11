import { useState, useEffect } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  addDoc,
  onSnapshot,
  query,
  orderBy,
  serverTimestamp
} from "firebase/firestore";

function Chat() {
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);

  // 🔄 real-time messages
  useEffect(() => {
  const q = query(collection(db, "messages"), orderBy("createdAt", "asc"));

  const unsubscribe = onSnapshot(q, (snapshot) => {
    const now = Date.now();

    const data = snapshot.docs
      .map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }))
      .filter((msg) => {
        if (!msg.createdAt) return false;

        const msgTime = msg.createdAt.toDate().getTime();

        // 🔥 only show messages < 24h old
        return now - msgTime < 24 * 60 * 60 * 1000;
      });

    setMessages(data);
  });

  return () => unsubscribe();
}, []);

  // 💬 send message
  const sendMessage = async () => {
    if (!text) return;

    await addDoc(collection(db, "messages"), {
      text: text,
      sender: auth.currentUser.email,
      createdAt: serverTimestamp()
    });

    setText("");
  };

  return (
    <div style={{ border: "2px solid black", padding: 10, marginTop: 20 }}>
      <h3>💬 Chat</h3>

      {messages.map((msg) => (
        <p key={msg.id}>
          <b>{msg.sender}:</b> {msg.text}
        </p>
      ))}

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type message..."
      />

      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default Chat;
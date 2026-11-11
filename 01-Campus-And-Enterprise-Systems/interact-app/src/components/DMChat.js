import { useState, useEffect } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  addDoc,
  onSnapshot,
  query,
  orderBy,
  serverTimestamp,
  doc,
  getDoc
} from "firebase/firestore";
import { useParams } from "react-router-dom";

function DMChat() {
  const { userId } = useParams();

  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [allowed, setAllowed] = useState(false);

  // ✅ check follow
  useEffect(() => {
    const check = async () => {
      const snap = await getDoc(doc(db, "users", auth.currentUser.uid));

      if (snap.exists()) {
        const data = snap.data();

        if (data.following?.includes(userId)) {
          setAllowed(true);
        }
      }
    };

    check();
  }, [userId]);

  // ✅ chat
  useEffect(() => {
    if (!allowed) return;

    const chatId =
      auth.currentUser.uid < userId
        ? auth.currentUser.uid + "_" + userId
        : userId + "_" + auth.currentUser.uid;

    const q = query(
      collection(db, "chats", chatId, "messages"),
      orderBy("createdAt")
    );

    const unsub = onSnapshot(q, (snap) => {
      setMessages(snap.docs.map(d => ({ id: d.id, ...d.data() })));
    });

    return () => unsub();
  }, [allowed, userId]);

  const sendMessage = async () => {
    if (!text) return;

    const chatId =
      auth.currentUser.uid < userId
        ? auth.currentUser.uid + "_" + userId
        : userId + "_" + auth.currentUser.uid;

    await addDoc(collection(db, "chats", chatId, "messages"), {
      text,
      senderId: auth.currentUser.uid,
      createdAt: serverTimestamp()
    });

    setText("");
  };

  if (!allowed) return <h3>❌ Follow user first</h3>;

  return (
    <div style={{ padding: 20 }}>
      <h2>💬 Chat</h2>

      <div style={{ height: 400, overflowY: "auto" }}>
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              textAlign:
                m.senderId === auth.currentUser.uid ? "right" : "left",
              margin: 10
            }}
          >
            <span
              style={{
                padding: 10,
                borderRadius: 10,
                background:
                  m.senderId === auth.currentUser.uid
                    ? "#4caf50"
                    : "#ddd"
              }}
            >
              {m.text}
            </span>
          </div>
        ))}
      </div>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default DMChat;
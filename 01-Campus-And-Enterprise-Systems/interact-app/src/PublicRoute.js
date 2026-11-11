import { Navigate } from "react-router-dom";

function PublicRoute({ user, children }) {
  if (user) {
    return <Navigate to="/" />; // 🔥 already login → dashboard
  }

  return children;
}

export default PublicRoute;
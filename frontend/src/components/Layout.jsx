// The header, the navigation, and the page area under it.
// Links change with the role: an applicant, an officer and a manager each
// see only what they can use (D-06, D-07).

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { label } from "../utils/format";

export default function Layout() {
  const { user, logout, isApplicant, isStaff, isManager } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">₹</span>
          <span>Loan Application Management</span>
        </div>
        <nav className="nav">
          {isApplicant && (
            <>
              <NavLink to="/applications">My applications</NavLink>
              <NavLink to="/applications/new">Apply</NavLink>
              <NavLink to="/profile">My profile</NavLink>
            </>
          )}
          {isStaff && (
            <>
              <NavLink to="/applications">Applications</NavLink>
              <NavLink to="/applications/new">New application</NavLink>
              <NavLink to="/dashboard">Dashboard</NavLink>
            </>
          )}
          {isManager && <NavLink to="/activity">Activity</NavLink>}
        </nav>
        <div className="whoami">
          <span className="whoami-name">{user?.name}</span>
          <span className="whoami-role">{label(user?.role)}</span>
          <button type="button" className="btn btn-ghost" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}

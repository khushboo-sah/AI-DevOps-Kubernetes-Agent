import { Link } from "react-router-dom";
import { clearAuth, getEmail } from "../auth";

export default function Navbar() {
  const email = getEmail();

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-lg font-semibold text-sky-300">
          AI Cloud Cost Detective
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/" className="text-slate-300 hover:text-white">
            Dashboard
          </Link>
          <Link to="/history" className="text-slate-300 hover:text-white">
            History
          </Link>
          {email ? (
            <div className="flex items-center gap-3">
              <span className="text-slate-400">{email}</span>
              <button
                type="button"
                onClick={() => {
                  clearAuth();
                  window.location.href = "/login";
                }}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-slate-200 hover:border-slate-500"
              >
                Logout
              </button>
            </div>
          ) : null}
        </nav>
      </div>
    </header>
  );
}

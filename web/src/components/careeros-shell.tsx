"use client";

import { usePathname } from "next/navigation";

const navigation = [
  { label: "Overview", href: "/" },
  { label: "Opportunities", href: "/opportunities" },
  { label: "Candidate Truth", href: "/candidate" },
  { label: "Evidence", href: "/evidence" },
  { label: "Applications", href: "/applications" },
];

export default function CareerOSShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">C</div>
          <div>
            <strong>CareerOS</strong>
            <span>Career operating system</span>
          </div>
        </div>

        <nav className="nav">
          {navigation.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <a
                className={`nav-item${active ? " active" : ""}`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </a>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          CareerOS engine connected
        </div>
      </aside>

      <section className="content">{children}</section>
    </main>
  );
}

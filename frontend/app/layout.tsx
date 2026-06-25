import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Internship Pipeline",
  description: "Team dashboard for coordinating international internship applications"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="shell">
          <header className="topbar">
            <Link href="/">
              <strong>⚡ Internship Pipeline</strong>
            </Link>
            <nav className="nav" aria-label="Primary navigation">
              <Link href="/">Dashboard</Link>
              <Link href="/companies">Companies</Link>
              <Link href="/users">Team</Link>
              <Link href="/contacts">Contacts</Link>
              <Link href="/applications">Applications</Link>
              <Link href="/discovery">Discovery</Link>
              <Link href="/reminders">Reminders</Link>
              <Link href="/job-postings">Job Postings</Link>
              <Link href="/interviews">Interviews</Link>
              <Link href="/visa">Visa</Link>
              <Link href="/templates">Templates</Link>
              <Link href="/outreach">Outreach</Link>
            </nav>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}

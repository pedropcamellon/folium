import { ReactNode } from "react";
import Sidebar from "./Sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b flex items-center px-6 justify-between">
          <div className="flex items-center space-x-4">
            <input className="border rounded px-3 py-1 w-64" placeholder="Search patients, appointments..." />
            <button className="relative p-2 rounded hover:bg-slate-100">
              <span className="sr-only">Notifications</span>
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="text-blue-700"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
              <span className="absolute top-0 right-0 inline-block w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-slate-200" />
            <span className="font-medium">Dr. Admin</span>
            <button className="ml-2 px-2 py-1 text-xs rounded bg-slate-100 hover:bg-slate-200">Logout</button>
          </div>
        </header>
        {/* Main dashboard content */}
        <main className="flex-1 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

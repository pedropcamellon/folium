"use client";

import { useState } from "react";
import { FaTachometerAlt, FaUserInjured, FaCalendarAlt, FaPhoneAlt, FaXRay, FaFileAlt, FaCog, FaChevronLeft, FaChevronRight } from "react-icons/fa";

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <aside className={`bg-white border-r flex flex-col justify-between transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}`}>
            <div>
                <div className="flex items-center h-16 px-4 border-b justify-between">
                    <span className={`font-bold text-xl text-blue-700 transition-opacity duration-200 ${collapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}`}>SouthDrift</span>
                    <button
                        className="p-2 rounded hover:bg-slate-100 ml-2"
                        onClick={() => setCollapsed(!collapsed)}
                        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                        tabIndex={0}
                    >
                        {collapsed ? <FaChevronRight size={20} /> : <FaChevronLeft size={20} />}
                    </button>
                </div>
                <nav className="mt-4 flex-1">
                    <ul className="space-y-2 px-2">
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaTachometerAlt size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Dashboard</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaUserInjured size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Patients</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaCalendarAlt size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Appointments</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaPhoneAlt size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Medical Calls</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaXRay size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Imaging AI</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaFileAlt size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Reports</span>
                            </a>
                        </li>
                        <li>
                            <a className="flex items-center px-3 py-2 rounded hover:bg-slate-100 font-medium" href="#">
                                <FaCog size={20} />
                                <span className={`ml-3 ${collapsed ? 'hidden' : 'inline'}`}>Settings</span>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div className="p-4 border-t">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-slate-200" />
                    <div className={`${collapsed ? 'hidden' : 'block'}`}>
                        <div className="font-semibold">Dr. Admin</div>
                        <div className="text-xs text-slate-500">Administrator</div>
                    </div>
                </div>
            </div>
        </aside>
    );
}

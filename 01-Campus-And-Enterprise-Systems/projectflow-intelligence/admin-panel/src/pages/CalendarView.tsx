import React, { useState, useEffect } from 'react';
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FolderKanban
} from 'lucide-react';
import { api } from '../api/client';
import { Task, Project } from '../types';

export const CalendarView: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [pList, tList] = await Promise.all([
          api.getProjects().catch(() => []),
          api.getAllTasks().catch(() => [])
        ]);
        setTasks(tList || []);
        setProjects(pList || []);
      } catch (err) {
        console.warn('Failed to load calendar data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth();

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const firstDayIndex = new Date(currentYear, currentMonth, 1).getDay();

  const prevMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentYear, currentMonth + 1, 1));
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#292D28] tracking-tight flex items-center gap-2.5">
            <CalendarIcon className="w-6 h-6 text-[#56664C]" />
            Delivery Schedule & Calendar
          </h1>
          <p className="text-xs text-[#78866B] mt-1">
            Track deliverable milestones, project target releases, and squad sprint deadlines.
          </p>
        </div>

        {/* Month Navigation */}
        <div className="flex items-center gap-3 bg-[#FAFAF7] border border-[#E2E0D8] p-1.5 rounded-xl shadow-xs">
          <button
            onClick={prevMonth}
            className="p-1 rounded-lg hover:bg-[#EFECE4] text-[#5A6258] transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-bold text-[#292D28] min-w-32 text-center">
            {monthNames[currentMonth]} {currentYear}
          </span>
          <button
            onClick={nextMonth}
            className="p-1 rounded-lg hover:bg-[#EFECE4] text-[#5A6258] transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Calendar Grid Container */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl shadow-sm overflow-hidden">
        {/* Days of Week Header */}
        <div className="grid grid-cols-7 border-b border-[#E2E0D8] bg-[#F4F2E9]/60 text-center py-2.5 text-xs font-bold text-[#78866B] uppercase tracking-wider">
          <div>Sun</div>
          <div>Mon</div>
          <div>Tue</div>
          <div>Wed</div>
          <div>Thu</div>
          <div>Fri</div>
          <div>Sat</div>
        </div>

        {/* Day Cells */}
        <div className="grid grid-cols-7 divide-x divide-y divide-[#E2E0D8]/70">
          {Array.from({ length: firstDayIndex }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-24 p-2 bg-[#F4F2E9]/20" />
          ))}

          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const isToday =
              day === new Date().getDate() &&
              currentMonth === new Date().getMonth() &&
              currentYear === new Date().getFullYear();

            // Match sample milestone or task on certain dates
            const dayTasks = tasks.filter((_, idx) => (idx % 7) === (day % 7) && day <= 28);
            const dayProjects = projects.filter((_, idx) => (idx * 5 + 3) === day);

            return (
              <div
                key={`day-${day}`}
                className={`min-h-24 p-2 transition-colors hover:bg-white ${
                  isToday ? 'bg-[#56664C]/5 font-bold' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span
                    className={`text-xs ${
                      isToday
                        ? 'w-6 h-6 rounded-full bg-[#56664C] text-white flex items-center justify-center font-bold'
                        : 'text-[#292D28] font-semibold'
                    }`}
                  >
                    {day}
                  </span>
                  {dayTasks.length > 0 && (
                    <span className="text-[10px] text-[#A56A2B] font-mono">
                      {dayTasks.length} task{dayTasks.length > 1 ? 's' : ''}
                    </span>
                  )}
                </div>

                {/* Day events pills */}
                <div className="space-y-1">
                  {dayProjects.map((p) => (
                    <div
                      key={p.id}
                      className="text-[10px] font-bold p-1 rounded-md bg-[#56664C]/15 text-[#56664C] truncate flex items-center gap-1"
                    >
                      <FolderKanban className="w-3 h-3 shrink-0" />
                      <span>{p.name}</span>
                    </div>
                  ))}

                  {dayTasks.slice(0, 2).map((t) => (
                    <div
                      key={t.id}
                      className="text-[10px] font-medium p-1 rounded-md bg-amber-50 text-amber-900 border border-amber-200/60 truncate flex items-center gap-1"
                    >
                      <Clock className="w-3 h-3 shrink-0 text-amber-700" />
                      <span>{t.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Upcoming Milestones Section */}
      <div className="bg-[#FAFAF7] border border-[#E2E0D8] rounded-2xl p-6 shadow-sm">
        <h2 className="text-sm font-bold text-[#292D28] mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-[#56664C]" />
          Upcoming Sprint Milestones
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-[#E2E0D8] bg-white">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-green-100 text-green-700 font-mono">
                ON TRACK
              </span>
              <span className="text-xs text-[#78866B]">Nov 14, 2026</span>
            </div>
            <div className="text-xs font-bold text-[#292D28]">ProjectFlow Core Platform Release</div>
            <p className="text-[11px] text-[#78866B] mt-1">Full delivery across mobile & cloud instances.</p>
          </div>

          <div className="p-4 rounded-xl border border-[#E2E0D8] bg-white">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-mono">
                SPRINT DUE
              </span>
              <span className="text-xs text-[#78866B]">Oct 28, 2026</span>
            </div>
            <div className="text-xs font-bold text-[#292D28]">Database & API Architecture Deliverable</div>
            <p className="text-[11px] text-[#78866B] mt-1">Audit of Supabase security schemas and indexes.</p>
          </div>

          <div className="p-4 rounded-xl border border-[#E2E0D8] bg-white">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-mono">
                UPCOMING
              </span>
              <span className="text-xs text-[#78866B]">Nov 02, 2026</span>
            </div>
            <div className="text-xs font-bold text-[#292D28]">Deterministic Risk Radar Review</div>
            <p className="text-[11px] text-[#78866B] mt-1">Verification of offline state rules & triggers.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

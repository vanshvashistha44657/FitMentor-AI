"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Dumbbell, Apple, MessageCircle, TrendingUp, ClipboardCheck, LayoutDashboard, LogOut } from "lucide-react";
import { useAuthStore } from "@/store/authStore";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/checkin", label: "Daily Check-in", icon: ClipboardCheck },
  { href: "/dashboard/workouts", label: "Workouts", icon: Dumbbell },
  { href: "/dashboard/nutrition", label: "Nutrition", icon: Apple },
  { href: "/dashboard/coach", label: "AI Coach", icon: MessageCircle },
  { href: "/dashboard/progress", label: "Progress", icon: TrendingUp },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((s) => s.logout);

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 border-r border-white/[0.06] p-6 flex flex-col gap-1 fixed h-screen">
        <span className="font-display font-bold text-lg mb-8 px-2">
          FitMentor <span className="text-ember-500">AI</span>
        </span>

        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors ${
                active ? "bg-ember-500/15 text-ember-400" : "text-mute hover:text-bone hover:bg-white/5"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}

        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-mute hover:text-bone hover:bg-white/5 mt-auto transition-colors"
        >
          <LogOut size={18} />
          Log out
        </button>
      </aside>

      <main className="flex-1 ml-64 px-10 py-10 max-w-5xl">{children}</main>
    </div>
  );
}

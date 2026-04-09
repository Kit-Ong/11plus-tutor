"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";

// Pages that should not show the sidebar
const FULL_WIDTH_PAGES = ["/welcome"];

export default function LayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isFullWidth = FULL_WIDTH_PAGES.includes(pathname);

  if (isFullWidth) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      <Sidebar />
      <main className="flex-1">
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">{children}</div>
      </main>
    </div>
  );
}

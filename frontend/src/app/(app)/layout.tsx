import { AppNav } from "@/components/layout/AppNav";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <AppNav />
      <div className="flex min-h-0 flex-1 flex-col">{children}</div>
    </div>
  );
}

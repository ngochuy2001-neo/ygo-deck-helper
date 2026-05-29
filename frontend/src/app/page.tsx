import { redirect } from "next/navigation";

/** Vào app luôn mở Dashboard. */
export default function Home() {
  redirect("/dashboard");
}

import type { Metadata } from "next";
import FlashCardsClient from "@/components/tools/FlashCardsClient";

export const metadata: Metadata = {
  title: "Flash Cards | Math Tools | Plug N Play",
  description:
    "Voice-powered math fact flash cards. Speak the answer and the app checks it instantly. Configure the operation, number range, and pace.",
};

export default function MathFlashCardsPage() {
  return <FlashCardsClient />;
}

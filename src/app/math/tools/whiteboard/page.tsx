import type { Metadata } from "next";
import WhiteboardClient from "@/components/tools/WhiteboardClient";

export const metadata: Metadata = {
  title: "Whiteboard | Math Tools | Plug N Play",
  description:
    "Full-screen digital whiteboard for math classrooms with built-in virtual manipulatives. Draw with pen, highlighter, shapes, and math text; drag out counters, fraction tiles, algebra tiles, and base-ten blocks; annotate PDFs — projector-ready.",
};

export default function MathWhiteboardPage() {
  return <WhiteboardClient />;
}

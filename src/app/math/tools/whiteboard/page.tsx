import type { Metadata } from "next";
import WhiteboardClient from "@/components/tools/WhiteboardClient";

export const metadata: Metadata = {
  title: "Whiteboard | Math Tools | Plug N Play",
  description:
    "Full-screen digital whiteboard for math classrooms. Draw, sketch, and demonstrate with pen, highlighter, and eraser — projector-ready.",
};

export default function MathWhiteboardPage() {
  return <WhiteboardClient />;
}

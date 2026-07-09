import type { Metadata } from "next";
import FormGroupsView from "@/components/groups/FormGroupsView";

// Next 16 — dynamic route params are async.

export async function generateMetadata({
  params,
}: {
  params: Promise<{ classId: string }>;
}): Promise<Metadata> {
  await params;
  return {
    title: "Form groups | Plug N Play",
    description: "Randomize a class into groups with an on-screen animation.",
  };
}

export default async function FormGroupsPage({
  params,
}: {
  params: Promise<{ classId: string }>;
}) {
  const { classId } = await params;
  // Full-bleed surface: the client component handles the navy chrome
  // and the animation canvas. The site header stays mounted because
  // we don't apply the project-mode body class here — the teacher
  // might want to bail back to Classes without going through the X.
  return <FormGroupsView classId={classId} />;
}

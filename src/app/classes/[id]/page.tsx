import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import ClassDetail from "@/components/classes/ClassDetail";

// Next 16 — dynamic route params are async. See node_modules/next/dist/docs.

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  // The class itself lives in browser localStorage, so we can't read it
  // here on the server — the metadata stays generic. The client renders
  // the class name in the H1.
  await params;
  return {
    title: "Class roster | Plug N Play",
    description: "Edit a saved class roster.",
  };
}

export default async function ClassDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <section className="bg-pnp-gray-50 py-8 md:py-10">
      <Container>
        <ClassDetail classId={id} />
      </Container>
    </section>
  );
}

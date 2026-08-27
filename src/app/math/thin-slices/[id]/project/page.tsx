import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllThinSlices, getThinSliceById } from "@/lib/library/thin-slices";
import type { ThinSliceBody } from "@/lib/core/types";
import ThinSliceRunner from "@/components/thin-slices/ThinSliceRunner";

export async function generateStaticParams() {
  const slices = await getAllThinSlices();
  return slices.map((s) => ({ id: s.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const slice = await getThinSliceById(id);
  if (!slice) return { title: "Thin Slice Not Found | Plug N Play" };
  return {
    title: `${slice.title} (Project) | Plug N Play`,
    description: slice.preview,
  };
}

export default async function ThinSliceProjectPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const slice = await getThinSliceById(id);
  if (!slice) notFound();

  const body = slice.body as ThinSliceBody;

  return (
    <ThinSliceRunner
      sliceId={slice.id}
      title={slice.title}
      stem={body.stem}
      shape={body.shape}
      steps={body.steps ?? []}
      enrichmentSteps={body.enrichmentSteps}
      prerequisiteSteps={body.prerequisiteSteps}
      prerequisiteLabel={body.prerequisiteLabel}
    />
  );
}

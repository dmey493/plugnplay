import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllTasks, getTaskById } from "@/lib/tasks";
import { primaryStandard as primaryStandardOf } from "@/lib/tasks-filter";
import type { TaskBody } from "@/lib/types";
import ProjectionView from "@/components/tasks/ProjectionView";

export async function generateStaticParams() {
  const tasks = await getAllTasks();
  return tasks.map((t) => ({ id: t.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const task = await getTaskById(id);
  if (!task) return { title: "Task Not Found | Plug N Play" };
  return {
    title: `${task.title} (Project) | Plug N Play`,
    description: task.preview,
  };
}

export default async function TaskProjectionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const task = await getTaskById(id);
  if (!task) notFound();

  const body = task.body as TaskBody;
  const primaryStandard = primaryStandardOf(task);

  return (
    <ProjectionView
      taskId={task.id}
      title={task.title}
      studentPrompt={body.studentPrompt}
      primaryStandard={primaryStandard}
      extensions={body.extensions}
      image={body.image}
    />
  );
}

import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllTasks, getTaskById } from "@/lib/tasks";
import { primaryStandard as primaryStandardOf } from "@/lib/tasks-filter";
import type { TaskBody, TaskType } from "@/lib/types";
import ProjectionView from "@/components/tasks/ProjectionView";

const TASK_TYPE_LABELS: Record<TaskType, string> = {
  anchor: "Anchor Task",
  investigation: "Investigation",
  "three-act": "Three-Act",
  warmup: "Warm-Up",
  performance: "Performance",
  "problem-set": "Problem Set",
};

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
  const typeLabel = TASK_TYPE_LABELS[body.taskType] ?? body.taskType;
  const durationLabel = `${task.time.minMinutes}-${task.time.maxMinutes} min`;
  const primaryStandard = primaryStandardOf(task);

  return (
    <ProjectionView
      taskId={task.id}
      title={task.title}
      studentPrompt={body.studentPrompt}
      primaryStandard={primaryStandard}
      durationLabel={durationLabel}
      taskTypeLabel={typeLabel}
      extensions={body.extensions}
      image={body.image}
    />
  );
}

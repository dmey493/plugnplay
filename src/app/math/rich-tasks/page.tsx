import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Button from "@/components/ui/Button";
import { getAllTasks } from "@/lib/tasks";
import { getAllThinSlices } from "@/lib/thin-slices";
import TasksLibrary from "@/components/tasks/TasksLibrary";

export const metadata: Metadata = {
  title: "Lesson Activities | Math | Plug N Play",
  description:
    "Classroom-ready math tasks for grades 6–8 — projectable, printable, and aligned to Indiana and Common Core standards.",
};

export default async function RichTasksPage() {
  // Unified library: rich tasks + thin slices in one collection, sorted by
  // title so the two formats interleave naturally. The type filter lives in
  // TasksLibrary; there's no separate Thin Slices page.
  const [tasks, slices] = await Promise.all([getAllTasks(), getAllThinSlices()]);
  const combined = [...tasks, ...slices];
  const mathTasks = combined
    .filter((t) => t.subjects.includes("math"))
    .sort((a, b) => a.title.localeCompare(b.title));

  return (
    <>
      <PageBanner
        back={{ href: "/math", label: "Back to math" }}
        title="Lesson activities"
        subtitle="Get every student thinking from the first minute. Classroom-ready tasks for grades 6–8 — projectable, printable, and built for vertical whiteboards."
      />

      <section className="bg-pnp-gray-50 py-8 md:py-12">
        <Container>
          {mathTasks.length === 0 ? (
            <div className="rounded-xl border-2 border-dashed border-pnp-gray-300 bg-white py-16 text-center">
              <p className="text-lg font-semibold text-pnp-gray-700">
                Tasks are on the way
              </p>
              <p className="mx-auto mt-1 max-w-sm text-sm text-pnp-gray-600">
                New tasks land every unit. Browse by unit to see what&rsquo;s
                ready to teach now.
              </p>
              <div className="mt-4 flex justify-center">
                <Button href="/math/units" tier="secondary">
                  Browse math units
                </Button>
              </div>
            </div>
          ) : (
            <TasksLibrary tasks={mathTasks} />
          )}
        </Container>
      </section>
    </>
  );
}

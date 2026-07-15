import { redirect } from "next/navigation";

/** The manipulatives board merged into the whiteboard — one canvas tool.
 *  Keep old bookmarks/links working. */
export default function MathManipulativesPage() {
  redirect("/math/tools/whiteboard");
}

import { redirect } from "next/navigation";

/**
 * /math/thin-slices is retired. Thin slices now live inside the unified
 * Rich Tasks library, filterable by the "Thin Slice" type. We keep the
 * route as a permanent redirect so legacy bookmarks (and any internal
 * links we may have missed) still land somewhere useful.
 *
 * The per-slice `/math/thin-slices/[id]/project` projection runner still
 * works and is what every "play this slice" button in the app points to —
 * only the library landing page is gone.
 */
export default function ThinSlicesPageRedirect() {
  redirect("/math/rich-tasks?type=thin-slice");
}

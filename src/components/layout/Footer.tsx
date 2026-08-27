import Link from "next/link";
import Image from "next/image";
import { NAV_ITEMS } from "@/lib/core/constants";

export default function Footer() {
  return (
    <footer className="bg-pnp-navy text-white/70">
      <div className="mx-auto max-w-[1296px] px-4 py-12 md:px-6">
        <div className="grid gap-8 md:grid-cols-3">
          {/* Brand */}
          <div>
            <Image
              src="/logo.png"
              alt="Plug N Play"
              width={160}
              height={42}
              className="mb-4 h-9 w-auto"
            />
            {/* Footer line gets its own trust/outcome beat instead of
                repeating the hero subhead. */}
            <p className="text-sm leading-relaxed">
              Made by middle-school teachers who got tired of building it all
              from scratch each year.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">
              Subjects
            </h3>
            <ul className="space-y-2">
              {NAV_ITEMS.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="inline-flex items-center gap-2 text-sm transition-colors hover:text-white"
                  >
                    {item.label}
                    {item.soon && (
                      <span className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white/70">
                        Soon
                      </span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tools */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">
              Resources
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/library"
                  className="text-sm transition-colors hover:text-white"
                >
                  Strategies
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 border-t border-white/10 pt-6 text-center text-xs">
          <p>
            &copy; {new Date().getFullYear()} Plug N Play. Built for teachers, by
            teachers.
          </p>
          <p className="mt-2">
            Original Plug N Play content is licensed under{" "}
            <a
              href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
              target="_blank"
              rel="noreferrer"
              className="underline transition-colors hover:text-white"
            >
              CC BY-NC-SA 4.0
            </a>
            . Curated tasks retain their original sources&rsquo; licenses;
            attribution appears on each task page.
          </p>
        </div>
      </div>
    </footer>
  );
}

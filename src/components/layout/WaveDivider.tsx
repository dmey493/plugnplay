export default function WaveDivider({
  fillColor = "var(--pnp-yellow)",
  className = "",
}: {
  fillColor?: string;
  className?: string;
}) {
  return (
    <div className={`w-full overflow-hidden leading-[0] ${className}`}>
      <svg
        viewBox="0 0 1440 60"
        preserveAspectRatio="none"
        className="block w-full"
        style={{ height: "clamp(30px, 4vw, 60px)" }}
      >
        <path
          d="M0,30 C240,55 480,5 720,30 C960,55 1200,5 1440,30 L1440,60 L0,60 Z"
          fill={fillColor}
        />
      </svg>
    </div>
  );
}

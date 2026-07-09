export default function Container({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`mx-auto max-w-[1296px] px-4 md:px-6 ${className}`}>
      {children}
    </div>
  );
}

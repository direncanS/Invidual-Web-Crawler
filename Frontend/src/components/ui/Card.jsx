export default function Card({ children, className = '', ...props }) {
  return (
    <div
      className={`rounded-xl bg-white p-6 shadow ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

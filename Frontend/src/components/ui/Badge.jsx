const statusStyles = {
  queued: 'bg-gray-100 text-gray-700',
  running: 'bg-yellow-100 text-yellow-800 animate-pulse',
  done: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
};

export default function Badge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-700'}`}
    >
      {status}
    </span>
  );
}

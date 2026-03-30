import { Inbox } from 'lucide-react';

export default function EmptyState({ title, description, icon: Icon = Inbox, children }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <Icon size={48} className="mb-4 text-gray-300" />
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}

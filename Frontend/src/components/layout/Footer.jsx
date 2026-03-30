export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-4">
      <div className="mx-auto max-w-7xl px-4 text-center text-sm text-gray-500 sm:px-6 lg:px-8">
        Web Crawler &copy; {new Date().getFullYear()}
      </div>
    </footer>
  );
}

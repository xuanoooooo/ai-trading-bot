import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { Sun, Moon, Home, Settings } from 'lucide-react'; // Example icons

const Layout: React.FC = () => {
  const [darkMode, setDarkMode] = React.useState(false);

  React.useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="flex min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-800 shadow-md p-4">
        <Link to="/dashboard" className="block text-2xl font-bold mb-8 text-indigo-600 dark:text-indigo-400">
          AI Trading
        </Link>
        <nav>
          <ul>
            <li className="mb-4">
              <Link
                to="/dashboard"
                className="flex items-center p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <Home className="mr-2" size={20} /> 仪表盘
              </Link>
            </li>
            <li className="mb-4">
              <Link
                to="/settings"
                className="flex items-center p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <Settings className="mr-2" size={20} /> 系统设置
              </Link>
            </li>
          </ul>
        </nav>
        <div className="absolute bottom-4 left-4">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <Outlet /> {/* Renders nested routes */}
      </main>
    </div>
  );
};

export default Layout;

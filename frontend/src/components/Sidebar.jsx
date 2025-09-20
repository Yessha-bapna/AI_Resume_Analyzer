import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Briefcase, 
  FileText, 
  Upload, 
  Settings,
  Users,
  BarChart3,
  ClipboardList
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'My Applications', href: '/my-applications', icon: ClipboardList },
  { name: 'My Resumes', href: '/my-resumes', icon: FileText },
  { name: 'Upload Resume', href: '/upload-resume', icon: Upload },
]

const adminNavigation = [
  { name: 'Admin Dashboard', href: '/admin', icon: BarChart3 },
  { name: 'Create Job', href: '/admin/create-job', icon: Briefcase },
]

export default function Sidebar() {
  const { user } = useAuth()

  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 bg-white overflow-y-auto border-r border-gray-200">
        <div className="flex items-center flex-shrink-0 px-4">
          <h1 className="text-xl font-bold text-gray-900">Resume Analyzer</h1>
        </div>
        
        <div className="mt-8 flex-grow flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`
                }
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
            
            {user?.is_admin && (
              <>
                <div className="border-t border-gray-200 my-4"></div>
                <div className="px-2">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Admin
                  </h3>
                </div>
                {adminNavigation.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={({ isActive }) =>
                      `group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                        isActive
                          ? 'bg-primary-100 text-primary-900'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`
                    }
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </NavLink>
                ))}
              </>
            )}
          </nav>
        </div>
        
        <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
          <div className="flex items-center">
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">{user?.username}</p>
              <p className="text-xs text-gray-500">
                {user?.is_admin ? 'Administrator' : 'User'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

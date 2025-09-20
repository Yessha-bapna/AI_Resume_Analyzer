import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import MyApplications from './pages/MyApplications'
import MyResumes from './pages/MyResumes'
import UploadResume from './pages/UploadResume'
import AdminDashboard from './pages/admin/AdminDashboard'
import JobRankings from './pages/admin/JobRankings'
import CreateJob from './pages/admin/CreateJob'

function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" />
  }

  if (requireAdmin && !user.is_admin) {
    return <Navigate to="/dashboard" />
  }

  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
              <Route index element={<Navigate to="/dashboard" />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="jobs" element={<Jobs />} />
              <Route path="my-applications" element={<MyApplications />} />
              <Route path="my-resumes" element={<MyResumes />} />
              <Route path="upload-resume" element={<UploadResume />} />
        
        {/* Admin routes */}
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="admin/jobs/:jobId/rankings" element={<JobRankings />} />
        <Route path="admin/create-job" element={<CreateJob />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <Router future={{ 
      v7_relativeSplatPath: true,
      v7_startTransition: true 
    }}>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <AppRoutes />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App

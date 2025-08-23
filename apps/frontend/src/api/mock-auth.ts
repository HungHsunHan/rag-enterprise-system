// Mock authentication for development when backend is not available
export const mockLogin = {
  admin: async (email: string, password: string) => {
    // Mock admin login
    if (email === 'admin@dev.com' && password === 'admin123') {
      return {
        access_token: 'mock-admin-token-' + Date.now(),
        token_type: 'bearer'
      }
    }
    throw new Error('Invalid email or password')
  },
  
  user: async (employeeId: string) => {
    // Mock user login - accept any of our dev employee IDs
    const validIds = ['EMP001', 'EMP002', 'DEV001', 'TEST001']
    if (validIds.includes(employeeId)) {
      return {
        access_token: 'mock-user-token-' + employeeId + '-' + Date.now(),
        token_type: 'bearer'
      }
    }
    throw new Error('Invalid employee ID')
  }
}
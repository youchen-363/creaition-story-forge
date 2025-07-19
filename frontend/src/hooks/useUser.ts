import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_URL } from '@/lib/config';

interface UserData {
  id: string;
  username: string;
  email: string;
  credits: number;
}

interface UseUserReturn {
  userData: UserData | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
  updateCredits: (newCredits: number) => Promise<boolean>;
}

export const useUser = (): UseUserReturn => {
  const { user } = useAuth();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const syncUserWithBackend = async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);

      console.log('useUser: Syncing user with backend:', user.email);

      // Test if API is available first
      try {
        const baseUrl = API_URL.replace('/api/', '');
        console.log('useUser: Testing API availability at:', `${baseUrl}/health`);
        const healthResponse = await fetch(`${baseUrl}/health`);
        if (!healthResponse.ok) {
          throw new Error('API not available');
        }
        console.log('useUser: API is available');
      } catch (apiError) {
        console.warn('useUser: API not available, working offline mode');
        // Don't set error state - work silently
        return;
      }

      // First try to get existing user by email
      console.log('useUser: Fetching user from:', `${API_URL}users/email/${user.email}`);
      const getUserResponse = await fetch(`${API_URL}users/email/${user.email}`);
      
      if (!getUserResponse.ok) {
        console.error('useUser: Get user request failed:', getUserResponse.status, getUserResponse.statusText);
        throw new Error(`HTTP ${getUserResponse.status}: ${getUserResponse.statusText}`);
      }
      
      const getUserData = await getUserResponse.json();

      console.log('useUser: Get user response:', getUserData);

      if (getUserData.success) {
        setUserData(getUserData.user);
        console.log('useUser: User data found:', getUserData.user);
      } else {
        console.log('useUser: User not found, creating new user');
        // User doesn't exist, create them
        const createResponse = await fetch(`${API_URL}users/create`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: user.user_metadata?.username || user.email?.split('@')[0] || 'User',
            email: user.email,
            credits: 999 // Default credits
          }),
        });

        const createData = await createResponse.json();
        console.log('useUser: Create response:', createData);
        
        if (createData.success) {
          setUserData(createData.user);
          console.log('useUser: User created successfully:', createData.user);
        } else {
          console.error('useUser: Failed to create user data:', createData.message);
          // Don't show error to user - work silently
        }
      }
    } catch (err) {
      console.error('useUser: Error syncing user:', err);
      // Don't show error to user - work silently
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    await syncUserWithBackend();
  };

  const updateCredits = async (newCredits: number): Promise<boolean> => {
    if (!user || !user.email) return false;

    try {
      const response = await fetch(`${API_URL}users/email/${user.email}/credits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credits: newCredits }),
      });

      const data = await response.json();
      if (data.success) {
        // Update local state
        setUserData(prev => prev ? { ...prev, credits: newCredits } : null);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error updating credits:', err);
      return false;
    }
  };

  useEffect(() => {
    if (user) {
      syncUserWithBackend();
    } else {
      setUserData(null);
      setError(null);
    }
  }, [user]);

  return {
    userData,
    loading,
    error,
    refreshUser,
    updateCredits,
  };
};

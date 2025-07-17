import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface SimpleUserData {
  email: string;
  username: string;
  credits: number;
}

interface UseSimpleUserReturn {
  userData: SimpleUserData | null;
  updateCredits: (newCredits: number) => void;
  loading: boolean;
}

export const useSimpleUser = (): UseSimpleUserReturn => {
  const { user } = useAuth();
  const [userData, setUserData] = useState<SimpleUserData | null>(null);
  const [loading, setLoading] = useState(false);

  const getEmailBasedCredits = (email: string): number => {
    // Simple hash function to generate consistent credits based on email
    const hash = email.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    return Math.abs(hash % 500) + 100; // Random between 100-600 based on email
  };

  const updateCredits = (newCredits: number) => {
    if (user?.email) {
      const storageKey = `credits_${user.email}`;
      localStorage.setItem(storageKey, newCredits.toString());
      setUserData(prev => prev ? { ...prev, credits: newCredits } : null);
    }
  };

  useEffect(() => {
    if (user?.email) {
      setLoading(true);
      
      // Get credits from localStorage or use email-based default
      const storageKey = `credits_${user.email}`;
      const savedCredits = localStorage.getItem(storageKey);
      const credits = savedCredits ? parseInt(savedCredits, 10) : getEmailBasedCredits(user.email);

      // Create user data
      const simpleUserData: SimpleUserData = {
        email: user.email,
        username: user.user_metadata?.username || user.email.split('@')[0] || 'User',
        credits: credits
      };

      setUserData(simpleUserData);
      setLoading(false);
    } else {
      setUserData(null);
      setLoading(false);
    }
  }, [user]);

  return {
    userData,
    updateCredits,
    loading,
  };
};

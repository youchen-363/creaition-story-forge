
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { User, Settings, History, CreditCard, LogOut, Coins } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useUser } from "@/hooks/useUser";
import { useSimpleUser } from "@/hooks/useSimpleUser";
import DatabaseTest from "./DatabaseTest";

interface HeaderProps {
  // Remove hardcoded credits prop
}

const Header = ({}: HeaderProps) => {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { userData, loading: userLoading } = useUser();
  const { userData: simpleUserData } = useSimpleUser();

  const handleLogout = async () => {
    try {
      await signOut();
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const getUserInitial = () => {
    if (user?.user_metadata?.username) {
      return user.user_metadata.username.charAt(0).toUpperCase();
    }
    if (user?.email) {
      return user.email.charAt(0).toUpperCase();
    }
    return "U";
  };

  const getDisplayName = () => {
    // Use userData from custom User table if available, otherwise fallback to Supabase auth, then simple user data
    if (userData?.username) {
      return userData.username;
    }
    if (simpleUserData?.username) {
      return simpleUserData.username;
    }
    return user?.user_metadata?.username || user?.email?.split('@')[0] || "User";
  };

  const getUserCredits = () => {
    // ONLY use credits from the database
    if (userData?.credits !== undefined) {
      return userData.credits;
    }
    
    // If database data is loading, show loading state
    if (userLoading) {
      return '...';
    }
    
    // Default to 0 if no data available
    return 0;
  };

  const isAuthenticated = !!user;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <img 
              src="/favicon.ico" 
              alt="CreAItion Logo" 
              className="w-8 h-8"
            />
            <span className="text-xl font-bold text-gray-900">CreAItion</span>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/about" className="text-gray-600 hover:text-gray-900 transition-colors">
              About Us
            </Link>
            <Link to="/pricing" className="text-gray-600 hover:text-gray-900 transition-colors">
              Pricing
            </Link>
            <Link to="/contact" className="text-gray-600 hover:text-gray-900 transition-colors">
              Contact Us
            </Link>
            <Link to="/faq" className="text-gray-600 hover:text-gray-900 transition-colors">
              FAQ
            </Link>
          </nav>

          {/* User Section */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center space-x-2 hover:bg-gray-100">
                    <Avatar className="w-8 h-8">
                      <AvatarImage src={user?.user_metadata?.avatar_url} alt={getDisplayName()} />
                      <AvatarFallback className="bg-gradient-to-br from-purple-600 to-blue-600 text-white">
                        {getUserInitial()}
                      </AvatarFallback>
                    </Avatar>
                    <span className="hidden sm:block text-sm font-medium">{getDisplayName()}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-2 py-1.5">
                    <p className="text-sm font-medium">{getDisplayName()}</p>
                    <p className="text-xs text-gray-500 flex items-center">
                      <Coins className="w-3 h-3 mr-1" />
                      Credits: {getUserCredits()}
                    </p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile/edit" className="w-full flex items-center">
                      <Settings className="w-4 h-4 mr-2" />
                      Edit Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/history" className="w-full flex items-center">
                      <History className="w-4 h-4 mr-2" />
                      History
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Link to="/pricing" className="w-full flex items-center">
                      <CreditCard className="w-4 h-4 mr-2" />
                      Add Credit
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-2">
                <Button variant="ghost" asChild>
                  <Link to="/login">Login</Link>
                </Button>
                <Button asChild>
                  <Link to="/signup">Sign Up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

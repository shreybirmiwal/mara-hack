import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [message, setMessage] = useState('');

  useEffect(() => {
    checkBackendHealth();
    fetchHelloMessage();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setBackendStatus(response.data.message);
    } catch (error) {
      setBackendStatus('Backend not responding');
    }
  };

  const fetchHelloMessage = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/hello`);
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Failed to fetch message from backend');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">MARA Hackathon 2025</h1>
          <p className="text-blue-100 mt-2">Clean Template - Ready for Development</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">

          {/* Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

            {/* Backend Status Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Backend Status</h2>
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 ${backendStatus === 'Backend is running' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                <span className="text-gray-700">{backendStatus}</span>
              </div>
            </div>

            {/* Message Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Backend Message</h2>
              <p className="text-gray-700">{message}</p>
            </div>

          </div>

          {/* Welcome Section */}
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome to MARA</h2>
            <p className="text-gray-600 mb-6">
              This is a clean template with a React frontend and Flask backend ready for development.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800">Frontend</h3>
                <p className="text-blue-600 text-sm">React + Tailwind CSS</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800">Backend</h3>
                <p className="text-green-600 text-sm">Flask + CORS</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800">Ready</h3>
                <p className="text-purple-600 text-sm">Start building!</p>
              </div>
            </div>

            <button
              onClick={() => window.location.reload()}
              className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh Status
            </button>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-4 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 MARA Hackathon - Clean Template</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

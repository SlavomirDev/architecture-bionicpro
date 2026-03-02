import React, { useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';

interface ReportData {
  username: string;
  reportDate: string;
  data: any;
}

interface HistoryReportData {
  startDate: string;
  endDate: string;
  reports: any[];
}

const ReportPage: React.FC = () => {
  const { keycloak, initialized } = useKeycloak();
  const [loading, setLoading] = useState({
    current: false,
    history: false
  });
  const [error, setError] = useState<string | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [historyData, setHistoryData] = useState<HistoryReportData | null>(null);
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });

  const handleDateChange = (field: 'startDate' | 'endDate') => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setDateRange(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const validateDates = (): boolean => {
    if (!dateRange.startDate || !dateRange.endDate) {
      setError('Please enter both start date and end date');
      return false;
    }

    if (dateRange.startDate > dateRange.endDate) {
      setError('Start date cannot be after end date');
      return false;
    }

    return true;
  };

  const downloadReport = async () => {
    if (!keycloak?.token) {
      setError('Not authenticated');
      return;
    }

    try {
      setLoading(prev => ({ ...prev, current: true }));
      setError(null);
      setReportData(null);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/reports/user-report`, {
        headers: {
          'Authorization': `Bearer ${keycloak.token}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ReportData = await response.json();
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(prev => ({ ...prev, current: false }));
    }
  };

  const downloadHistoryReport = async () => {
    if (!keycloak?.token) {
      setError('Not authenticated');
      return;
    }

    if (!validateDates()) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, history: true }));
      setError(null);
      setHistoryData(null);

      const url = `${process.env.REACT_APP_API_URL}/reports/user-report/history?startDate=${encodeURIComponent(
        dateRange.startDate
      )}&endDate=${encodeURIComponent(dateRange.endDate)}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${keycloak.token}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: HistoryReportData = await response.json();
      setHistoryData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(prev => ({ ...prev, history: false }));
    }
  };

  const clearError = () => setError(null);

  if (!initialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-lg text-gray-600">Loading application...</div>
      </div>
    );
  }

  if (!keycloak.authenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <div className="p-8 bg-white rounded-lg shadow-md text-center">
          <h1 className="text-2xl font-bold mb-6">Welcome to Report System</h1>
          <p className="text-gray-600 mb-6">Please log in to access your reports</p>
          <button
            onClick={() => keycloak.login()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Usage Reports</h1>
          <button
            onClick={() => keycloak.logout()}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Report Section */}
          <section className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Current User Report</h2>
            </div>
            
            <div className="p-6">
              <button
                onClick={downloadReport}
                disabled={loading.current}
                className={`w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
                  loading.current ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading.current ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </span>
                ) : 'Generate Current Report'}
              </button>

              {reportData && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-700 mb-2">Latest Report:</h3>
                  <pre className="text-sm overflow-auto max-h-96 p-2 bg-white rounded border">
                    {JSON.stringify(reportData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </section>

          {/* History Report Section */}
          <section className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Historical Reports</h2>
            </div>
            
            <div className="p-6">
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date *
                  </label>
                  <input
                    type="date"
                    value={dateRange.startDate}
                    onChange={handleDateChange('startDate')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date *
                  </label>
                  <input
                    type="date"
                    value={dateRange.endDate}
                    onChange={handleDateChange('endDate')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <button
                onClick={downloadHistoryReport}
                disabled={loading.history || !dateRange.startDate || !dateRange.endDate}
                className={`w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors ${
                  (loading.history || !dateRange.startDate || !dateRange.endDate) ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading.history ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </span>
                ) : 'Load Historical Reports'}
              </button>

              {historyData && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-700 mb-2">
                    Reports from {historyData.startDate} to {historyData.endDate}:
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Total reports: {historyData.reports.length}
                  </p>
                  <pre className="text-sm overflow-auto max-h-96 p-2 bg-white rounded border">
                    {JSON.stringify(historyData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4 relative">
            <button
              onClick={clearError}
              className="absolute top-2 right-2 text-red-400 hover:text-red-600"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <p className="text-red-700 pr-8">{error}</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default ReportPage;
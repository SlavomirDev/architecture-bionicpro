using BionicproReports.Models;

namespace ReportingApi.Services;

public interface IReportService
{
    Task<CustomerReport?> GetCustomerReportAsync(string username);
    Task<List<CustomerReport>> GetCustomerReportHistoryAsync(string username, string startDate, string endDate);
}

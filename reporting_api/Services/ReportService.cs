using BionicproReports.Models;
using BionicproReports.Repositories;

using ReportingApi.Services;

namespace BionicproReports.Services;

public class ReportService : IReportService
{
    private readonly IReportRepository _reportRepository;

    public ReportService(IReportRepository reportRepository)
    {
        _reportRepository = reportRepository;
    }

    public async Task<CustomerReport?> GetCustomerReportAsync(string username)
    {
        return await _reportRepository.FindLatestByUsernameAsync(username);
    }

    public async Task<List<CustomerReport>> GetCustomerReportHistoryAsync(string username, string startDate, string endDate)
    {
        return await _reportRepository.FindByUsernameAndDateRangeAsync(username, startDate, endDate);
    }
}
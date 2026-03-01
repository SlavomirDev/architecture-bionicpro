using BionicproReports.Models;

namespace BionicproReports.Repositories;

public interface IReportRepository
{
    Task<CustomerReport?> FindLatestByUsernameAsync(string username);
    Task<List<CustomerReport>> FindByUsernameAndDateRangeAsync(string username, string startDate, string endDate);
}

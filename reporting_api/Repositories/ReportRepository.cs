using BionicproReports.Models;

using Dapper;

using System.Data;

namespace BionicproReports.Repositories;

public class ReportRepository : IReportRepository
{
    private readonly IDbConnection _connection;
    private readonly ILogger<ReportRepository> _logger;

    public ReportRepository(IDbConnection connection, ILogger<ReportRepository> logger)
    {
        _connection = connection;
        _logger = logger;
    }

    public async Task<CustomerReport?> FindLatestByUsernameAsync(string username)
    {
        const string sql = @"
            SELECT * FROM customer_telemetry_mart 
            WHERE username = @Username 
            ORDER BY report_date DESC, last_updated DESC 
            LIMIT 1";

        try
        {
            return await _connection.QueryFirstOrDefaultAsync<CustomerReport>(sql, new { Username = username });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, ex.Message);
            return null;
        }
    }

    public async Task<List<CustomerReport>> FindByUsernameAndDateRangeAsync(string username, string startDate, string endDate)
    {
        const string sql = @"
            SELECT * FROM customer_telemetry_mart 
            WHERE username = @Username AND report_date BETWEEN @StartDate AND @EndDate
            ORDER BY report_date DESC";

        try
        {
            var result = await _connection.QueryAsync<CustomerReport>(sql,
                new { Username = username, StartDate = startDate, EndDate = endDate });
            return result.AsList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, ex.Message);
            return new List<CustomerReport>();
        }
    }
}
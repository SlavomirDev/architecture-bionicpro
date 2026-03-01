using ClickHouse.Client.ADO;

using System.Data;

namespace BionicproReports.Configuration;

public static class ClickHouseConfig
{
    public static IDbConnection CreateClickHouseConnection(IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("ClickHouse");
        Console.WriteLine($"Connecting to ClickHouse with URL: {connectionString}");

        return new ClickHouseConnection(connectionString);
    }
}
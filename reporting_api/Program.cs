using BionicproReports.Configuration;
using BionicproReports.Repositories;
using BionicproReports.Services;

using ClickHouse.Client.ADO;

using ReportingApi.Services;

using System.Data;

try
{
    var builder = WebApplication.CreateBuilder(args);

    var services = builder.Services;

    // Add services to the container
    services.AddControllers();
    services.AddEndpointsApiExplorer();

    // JWT Authentication
    services.AddJwtAuthentication(builder.Configuration);

    // ClickHouse Connection
    services.AddScoped<IDbConnection>(provider =>
    {
        var connectionString = builder.Configuration.GetConnectionString("ClickHouse");
        return new ClickHouseConnection(connectionString);
    });

    services.AddScoped(provider =>
    {
        var connection = provider.GetRequiredService<ClickHouseConnection>();
        connection.Open();
        return connection;
    });

    // Repositories and Services
    services.AddScoped<IReportRepository, ReportRepository>();
    services.AddScoped<IReportService, ReportService>();

    // CORS
    services.AddCors(options =>
    {
        options.AddPolicy("AllowAll", policy =>
        {
            policy.AllowAnyOrigin()
                  .AllowAnyMethod()
                  .AllowAnyHeader();
        });
    });

    var app = builder.Build();

    // Configure the HTTP request pipeline
    app.UseHttpsRedirection();
    app.UseCors("AllowAll");
    app.UseAuthentication();
    app.UseAuthorization();
    app.MapControllers();

    app.Run();
}
catch (Exception ex)
{
    Console.WriteLine($"Application stopped due to exception: {ex.Message}");
    throw;
}
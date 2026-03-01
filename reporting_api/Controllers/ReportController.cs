using BionicproReports.Models;

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

using ReportingApi.Services;

using System.Security.Claims;

namespace BionicproReports.Controllers;

[Route("reports")]
[Authorize, ApiController]
public class ReportController : ControllerBase
{
    private readonly IReportService _reportService;

    public ReportController(IReportService reportService)
    {
        _reportService = reportService;
    }

    [HttpGet("user-report")]
    public async Task<ActionResult<ApiResponse<CustomerReport>>> GetCustomerReport()
    {
        var username = User.FindFirst("preferred_username")?.Value ??
                      User.FindFirst(ClaimTypes.Name)?.Value;

        if (string.IsNullOrEmpty(username))
        {
            return Unauthorized(ApiResponse<CustomerReport>.Error("User not authenticated"));
        }

        var report = await _reportService.GetCustomerReportAsync(username);

        if (report != null)
        {
            return Ok(ApiResponse<CustomerReport>.GetSuccess(report));
        }
        else
        {
            return Ok(ApiResponse<CustomerReport>.Error($"Отчет для пользователя {username} не найден"));
        }
    }

    [HttpGet("user-report/history")]
    public async Task<ActionResult<ApiResponse<List<CustomerReport>>>> GetCustomerReportHistory(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate)
    {
        var username = User.FindFirst("preferred_username")?.Value ??
                      User.FindFirst(ClaimTypes.Name)?.Value;

        if (string.IsNullOrEmpty(username))
        {
            return Unauthorized(ApiResponse<List<CustomerReport>>.Error("User not authenticated"));
        }

        var reports = await _reportService.GetCustomerReportHistoryAsync(
            username,
            startDate.ToString("yyyy-MM-dd"),
            endDate.ToString("yyyy-MM-dd")
        );

        if (reports.Any())
        {
            return Ok(ApiResponse<List<CustomerReport>>.GetSuccess(reports));
        }
        else
        {
            return Ok(ApiResponse<List<CustomerReport>>.Error($"Отчеты для пользователя {username} за указанный период не найдены"));
        }
    }

    [HttpGet("health")]
    [AllowAnonymous]
    public ActionResult<ApiResponse<string>> HealthCheck()
    {
        return Ok(ApiResponse<string>.GetSuccess("Service is healthy"));
    }
}
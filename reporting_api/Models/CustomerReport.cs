namespace BionicproReports.Models;

public class CustomerReport
{
    public long MartId { get; set; }
    public int CustomerId { get; set; }
    public string? Username { get; set; }
    public string? Email { get; set; }
    public string? CustomerRole { get; set; }
    public DateTime ReportDate { get; set; }
    public int TotalUsageMinutes { get; set; }
    public double AvgDailyUsageMinutes { get; set; }
    public int TotalMovements { get; set; }
    public double AvgSuccessRate { get; set; }
    public double AvgResponseTimeMs { get; set; }
    public int TotalErrors { get; set; }
    public double AvgBatteryLevel { get; set; }
    public double AvgSignalQuality { get; set; }
    public DateTime RegistrationDate { get; set; }
    public string? ProductType { get; set; }
    public int TotalOrders { get; set; }
    public decimal TotalOrderAmount { get; set; }
    public double UsageEfficiencyScore { get; set; }
    public double MovementAccuracyScore { get; set; }
    public DateTime LastUpdated { get; set; }
}
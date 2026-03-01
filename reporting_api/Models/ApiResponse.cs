namespace BionicproReports.Models;

public class ApiResponse<T>
{
    public bool Success { get; set; }
    public string Message { get; set; }
    public T? Data { get; set; }

    public ApiResponse(bool success, string message, T? data)
    {
        Success = success;
        Message = message;
        Data = data;
    }

    public static ApiResponse<T> GetSuccess(T data)
    {
        return new ApiResponse<T>(true, "Success", data);
    }

    public static ApiResponse<T> Error(string message)
    {
        return new ApiResponse<T>(false, message, default);
    }
}

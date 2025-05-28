using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

namespace CSharpService.Services
{
    public class CodeExecutionService
    {
        public async Task<string> ExecuteCodeAsync(string code, string fileName)
        {
            string filePath = Path.Combine(Path.GetTempPath(), fileName);
            await File.WriteAllTextAsync(filePath, code);

            var processStartInfo = new ProcessStartInfo
            {
                FileName = "dotnet",
                Arguments = $"run {filePath}",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (var process = new Process { StartInfo = processStartInfo })
            {
                process.Start();
                string output = await process.StandardOutput.ReadToEndAsync();
                string error = await process.StandardError.ReadToEndAsync();
                process.WaitForExit();

                if (process.ExitCode != 0)
                {
                    return $"Error: {error}";
                }

                return output;
            }
        }
    }
}
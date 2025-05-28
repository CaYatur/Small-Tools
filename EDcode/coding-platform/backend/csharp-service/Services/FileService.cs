using System.IO;
using System.Threading.Tasks;

namespace CSharpService.Services
{
    public class FileService
    {
        private readonly string basePath;

        public FileService(string basePath)
        {
            this.basePath = basePath;
        }

        public async Task<string> SaveFileAsync(string fileName, byte[] content)
        {
            var filePath = Path.Combine(basePath, fileName);
            await File.WriteAllBytesAsync(filePath, content);
            return filePath;
        }

        public async Task<byte[]> ReadFileAsync(string fileName)
        {
            var filePath = Path.Combine(basePath, fileName);
            return await File.ReadAllBytesAsync(filePath);
        }

        public bool FileExists(string fileName)
        {
            var filePath = Path.Combine(basePath, fileName);
            return File.Exists(filePath);
        }

        public void DeleteFile(string fileName)
        {
            var filePath = Path.Combine(basePath, fileName);
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
        }
    }
}
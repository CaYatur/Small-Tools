using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;

namespace CSharpService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PackageController : ControllerBase
    {
        // GET: api/package
        [HttpGet]
        public ActionResult<IEnumerable<string>> GetPackages()
        {
            // Logic to retrieve the list of installed packages
            return Ok(new List<string> { "Package1", "Package2" });
        }

        // POST: api/package/install
        [HttpPost("install")]
        public ActionResult InstallPackage([FromBody] string packageName)
        {
            // Logic to install the specified package
            return Ok($"Package {packageName} installed successfully.");
        }

        // POST: api/package/uninstall
        [HttpPost("uninstall")]
        public ActionResult UninstallPackage([FromBody] string packageName)
        {
            // Logic to uninstall the specified package
            return Ok($"Package {packageName} uninstalled successfully.");
        }
    }
}
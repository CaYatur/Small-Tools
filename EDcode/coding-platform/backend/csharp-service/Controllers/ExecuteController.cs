using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace CSharpService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ExecuteController : ControllerBase
    {
        private readonly CodeExecutionService _codeExecutionService;

        public ExecuteController(CodeExecutionService codeExecutionService)
        {
            _codeExecutionService = codeExecutionService;
        }

        [HttpPost("run")]
        public IActionResult RunCode([FromBody] ExecutionRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Code))
            {
                return BadRequest("Invalid execution request.");
            }

            try
            {
                var result = _codeExecutionService.ExecuteCode(request.Code, request.References);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
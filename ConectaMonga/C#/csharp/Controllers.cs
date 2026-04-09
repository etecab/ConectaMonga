// =============================================
//  ConectaMonga — Controllers.cs
//  Controladores da API REST em C#
// =============================================

using ConectaMonga.API.Models;
using ConectaMonga.API.Services;
using Microsoft.AspNetCore.Mvc;

namespace ConectaMonga.API.Controllers
{
    // ── EVENTOS ──
    [ApiController]
    [Route("api/[controller]")]
    public class EventosController : ControllerBase
    {
        private readonly IEventoService _eventoService;

        public EventosController(IEventoService eventoService)
        {
            _eventoService = eventoService;
        }

        /// <summary>Lista todos os eventos ativos.</summary>
        [HttpGet]
        public async Task<IActionResult> GetAll(
            [FromQuery] int? categoriaId,
            [FromQuery] int? empresaId)
        {
            var eventos = await _eventoService.ListarAsync(categoriaId, empresaId);
            return Ok(eventos);
        }

        /// <summary>Obtém um evento por ID.</summary>
        [HttpGet("{id:int}")]
        public async Task<IActionResult> GetById(int id)
        {
            var evento = await _eventoService.ObterPorIdAsync(id);
            if (evento is null) return NotFound(new { erro = "Evento não encontrado" });
            return Ok(evento);
        }

        /// <summary>Cria um novo evento. Foto obrigatória.</summary>
        [HttpPost]
        public async Task<IActionResult> Create([FromBody] EventoCriarDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            if (string.IsNullOrWhiteSpace(dto.FotoUrl))
                return BadRequest(new { erro = "A foto de divulgação é obrigatória" });

            var id = await _eventoService.CriarAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id }, new { id, mensagem = "Evento publicado com sucesso" });
        }

        /// <summary>Remove um evento.</summary>
        [HttpDelete("{id:int}")]
        public async Task<IActionResult> Delete(int id)
        {
            var ok = await _eventoService.DeletarAsync(id);
            if (!ok) return NotFound(new { erro = "Evento não encontrado" });
            return Ok(new { mensagem = "Evento removido com sucesso" });
        }
    }

    // ── EMPRESAS ──
    [ApiController]
    [Route("api/[controller]")]
    public class EmpresasController : ControllerBase
    {
        private readonly IEmpresaService _empresaService;

        public EmpresasController(IEmpresaService empresaService)
        {
            _empresaService = empresaService;
        }

        /// <summary>Lista todas as empresas.</summary>
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var empresas = await _empresaService.ListarAsync();
            return Ok(empresas);
        }

        /// <summary>Obtém empresa por ID.</summary>
        [HttpGet("{id:int}")]
        public async Task<IActionResult> GetById(int id)
        {
            var empresa = await _empresaService.ObterPorIdAsync(id);
            if (empresa is null) return NotFound(new { erro = "Empresa não encontrada" });
            return Ok(empresa);
        }

        /// <summary>Cadastra uma nova empresa (CNPJ obrigatório).</summary>
        [HttpPost("cadastro")]
        public async Task<IActionResult> Cadastrar([FromBody] EmpresaCadastroDto dto)
        {
            if (!ModelState.IsValid) return BadRequest(ModelState);

            var (id, erro) = await _empresaService.CadastrarAsync(dto);
            if (erro is not null) return Conflict(new { erro });
            return CreatedAtAction(nameof(GetById), new { id }, new { id, mensagem = "Empresa cadastrada com sucesso" });
        }

        /// <summary>Autentica uma empresa.</summary>
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] EmpresaLoginDto dto)
        {
            if (!ModelState.IsValid) return BadRequest(ModelState);
            var empresa = await _empresaService.AutenticarAsync(dto.Email, dto.Senha);
            if (empresa is null) return Unauthorized(new { erro = "Credenciais inválidas" });
            return Ok(new { mensagem = "Login realizado", empresa });
        }
    }

    // ── CATEGORIAS ──
    [ApiController]
    [Route("api/[controller]")]
    public class CategoriasController : ControllerBase
    {
        private readonly AppDbContext _db;
        public CategoriasController(AppDbContext db) => _db = db;

        [HttpGet]
        public IActionResult GetAll() => Ok(_db.Categorias.OrderBy(c => c.Nome).ToList());

        [HttpPost]
        public IActionResult Create([FromBody] Categoria cat)
        {
            _db.Categorias.Add(cat);
            _db.SaveChanges();
            return CreatedAtAction(nameof(GetAll), new { id = cat.Id }, cat);
        }
    }

    // ── CIDADES ──
    [ApiController]
    [Route("api/[controller]")]
    public class CidadesController : ControllerBase
    {
        private readonly AppDbContext _db;
        public CidadesController(AppDbContext db) => _db = db;

        [HttpGet]
        public IActionResult GetAll() => Ok(_db.Cidades.OrderBy(c => c.Nome).ToList());

        [HttpPost]
        public IActionResult Create([FromBody] Cidade cidade)
        {
            _db.Cidades.Add(cidade);
            _db.SaveChanges();
            return CreatedAtAction(nameof(GetAll), new { id = cidade.Id }, cidade);
        }
    }

    // ── SEGMENTOS ──
    [ApiController]
    [Route("api/[controller]")]
    public class SegmentosController : ControllerBase
    {
        private readonly AppDbContext _db;
        public SegmentosController(AppDbContext db) => _db = db;

        [HttpGet]
        public IActionResult GetAll() => Ok(_db.Segmentos.OrderBy(s => s.Nome).ToList());

        [HttpPost]
        public IActionResult Create([FromBody] Segmento seg)
        {
            _db.Segmentos.Add(seg);
            _db.SaveChanges();
            return CreatedAtAction(nameof(GetAll), new { id = seg.Id }, seg);
        }
    }
}

// =============================================
//  AppDbContext.cs
// =============================================

namespace ConectaMonga.API.Data
{
    using ConectaMonga.API.Models;
    using Microsoft.EntityFrameworkCore;

    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<Cidade>    Cidades    { get; set; }
        public DbSet<Segmento>  Segmentos  { get; set; }
        public DbSet<Categoria> Categorias { get; set; }
        public DbSet<Empresa>   Empresas   { get; set; }
        public DbSet<Evento>    Eventos    { get; set; }

        protected override void OnModelCreating(ModelBuilder mb)
        {
            mb.Entity<Empresa>().HasIndex(e => e.Email).IsUnique();
            mb.Entity<Empresa>().HasIndex(e => e.Cnpj).IsUnique();
            mb.Entity<Categoria>().HasIndex(c => c.Slug).IsUnique();
        }
    }
}

// =============================================
//  Services.cs — Interfaces e Implementações
// =============================================

namespace ConectaMonga.API.Services
{
    using ConectaMonga.API.Data;
    using ConectaMonga.API.Models;
    using Microsoft.EntityFrameworkCore;
    using System.Security.Cryptography;
    using System.Text;
    using System.Text.RegularExpressions;

    // ── INTERFACE EVENTO ──
    public interface IEventoService
    {
        Task<IEnumerable<object>> ListarAsync(int? categoriaId, int? empresaId);
        Task<Evento?>             ObterPorIdAsync(int id);
        Task<int>                 CriarAsync(EventoCriarDto dto);
        Task<bool>                DeletarAsync(int id);
    }

    // ── IMPLEMENTAÇÃO EVENTO ──
    public class EventoService : IEventoService
    {
        private readonly AppDbContext _db;
        public EventoService(AppDbContext db) => _db = db;

        public async Task<IEnumerable<object>> ListarAsync(int? categoriaId, int? empresaId)
        {
            var query = _db.Eventos
                .Include(e => e.Categoria)
                .Include(e => e.Empresa)
                .Where(e => e.ExpiraEm == null || e.ExpiraEm >= DateTime.UtcNow);

            if (categoriaId.HasValue) query = query.Where(e => e.CategoriaId == categoriaId);
            if (empresaId.HasValue)   query = query.Where(e => e.EmpresaId   == empresaId);

            return await query.OrderBy(e => e.DataEvento).Select(e => new
            {
                e.Id, e.Titulo, e.Descricao, e.DataEvento, e.Horario,
                e.Local, e.ContatoWhatsapp, e.PublicadoEm,
                Categoria  = e.Categoria!.Nome,
                CorHex     = e.Categoria!.CorHex,
                Empresa    = e.Empresa!.Nome,
                EmpresaId  = e.EmpresaId
            }).ToListAsync<object>();
        }

        public async Task<Evento?> ObterPorIdAsync(int id) =>
            await _db.Eventos.Include(e => e.Categoria).Include(e => e.Empresa)
                .FirstOrDefaultAsync(e => e.Id == id);

        public async Task<int> CriarAsync(EventoCriarDto dto)
        {
            var ev = new Evento
            {
                EmpresaId        = dto.EmpresaId,
                CategoriaId      = dto.CategoriaId,
                Titulo           = dto.Titulo,
                Descricao        = dto.Descricao,
                DataEvento       = DateTime.Parse(dto.DataEvento),
                Horario          = dto.Horario is not null ? TimeSpan.Parse(dto.Horario) : null,
                Local            = dto.Local,
                ContatoWhatsapp  = dto.ContatoWhatsapp,
                PublicadoEm      = DateTime.UtcNow,
                ExpiraEm         = dto.ExpiraEm is not null ? DateTime.Parse(dto.ExpiraEm) : null
            };
            _db.Eventos.Add(ev);
            await _db.SaveChangesAsync();
            return ev.Id;
        }

        public async Task<bool> DeletarAsync(int id)
        {
            var ev = await _db.Eventos.FindAsync(id);
            if (ev is null) return false;
            _db.Eventos.Remove(ev);
            await _db.SaveChangesAsync();
            return true;
        }
    }

    // ── INTERFACE EMPRESA ──
    public interface IEmpresaService
    {
        Task<IEnumerable<object>>     ListarAsync();
        Task<Empresa?>                ObterPorIdAsync(int id);
        Task<(int Id, string? Erro)>  CadastrarAsync(EmpresaCadastroDto dto);
        Task<Empresa?>                AutenticarAsync(string email, string senha);
    }

    // ── IMPLEMENTAÇÃO EMPRESA ──
    public class EmpresaService : IEmpresaService
    {
        private readonly AppDbContext _db;
        public EmpresaService(AppDbContext db) => _db = db;

        public async Task<IEnumerable<object>> ListarAsync() =>
            await _db.Empresas.Include(e => e.Cidade).Include(e => e.Segmento)
                .OrderBy(e => e.Nome).Select(e => new
                {
                    e.Id, e.Nome, e.Email, e.Telefone, e.CriadoEm,
                    Cidade    = e.Cidade!.Nome,
                    Segmento  = e.Segmento!.Nome
                }).ToListAsync<object>();

        public async Task<Empresa?> ObterPorIdAsync(int id) =>
            await _db.Empresas.Include(e => e.Cidade).Include(e => e.Segmento)
                .FirstOrDefaultAsync(e => e.Id == id);

        public async Task<(int, string?)> CadastrarAsync(EmpresaCadastroDto dto)
        {
            // Valida CNPJ
            var cnpjDigits = Regex.Replace(dto.Cnpj, @"\D", "");
            if (cnpjDigits.Length != 14)
                return (0, "CNPJ inválido");

            // Verifica duplicidade
            var existe = await _db.Empresas
                .AnyAsync(e => e.Email == dto.Email || e.Cnpj == cnpjDigits);
            if (existe) return (0, "Email ou CNPJ já cadastrado");

            var empresa = new Empresa
            {
                CidadeId   = dto.CidadeId,
                SegmentoId = dto.SegmentoId,
                Nome       = dto.Nome,
                Cnpj       = cnpjDigits,
                Email      = dto.Email,
                SenhaHash  = HashSenha(dto.Senha),
                Telefone   = dto.Telefone,
                CriadoEm   = DateTime.UtcNow
            };
            _db.Empresas.Add(empresa);
            await _db.SaveChangesAsync();
            return (empresa.Id, null);
        }

        public async Task<Empresa?> AutenticarAsync(string email, string senha) =>
            await _db.Empresas
                .FirstOrDefaultAsync(e => e.Email == email && e.SenhaHash == HashSenha(senha));

        private static string HashSenha(string senha)
        {
            var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(senha));
            return Convert.ToHexString(bytes).ToLower();
        }
    }
}

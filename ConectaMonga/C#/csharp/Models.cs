// =============================================
//  ConectaMonga — Models.cs
//  Modelos do banco de dados (Entity Framework)
// =============================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ConectaMonga.API.Models
{
    // ── CIDADE ──
    [Table("cidade")]
    public class Cidade
    {
        [Key]
        public int Id { get; set; }

        [Required, MaxLength(100)]
        public string Nome { get; set; } = string.Empty;

        [MaxLength(2)]
        public string Estado { get; set; } = "SP";

        // Navegação
        public ICollection<Empresa> Empresas { get; set; } = new List<Empresa>();
    }

    // ── SEGMENTO ──
    [Table("segmento")]
    public class Segmento
    {
        [Key]
        public int Id { get; set; }

        [Required, MaxLength(100)]
        public string Nome { get; set; } = string.Empty;

        [MaxLength(255)]
        public string? Descricao { get; set; }

        // Navegação
        public ICollection<Empresa> Empresas { get; set; } = new List<Empresa>();
    }

    // ── CATEGORIA ──
    [Table("categoria")]
    public class Categoria
    {
        [Key]
        public int Id { get; set; }

        [Required, MaxLength(50)]
        public string Nome { get; set; } = string.Empty;

        [Required, MaxLength(50)]
        public string Slug { get; set; } = string.Empty;

        [MaxLength(7)]
        public string CorHex { get; set; } = "#3a7fa0";

        // Navegação
        public ICollection<Evento> Eventos { get; set; } = new List<Evento>();
    }

    // ── EMPRESA ──
    [Table("empresa")]
    public class Empresa
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public int CidadeId { get; set; }

        [Required]
        public int SegmentoId { get; set; }

        [Required, MaxLength(150)]
        public string Nome { get; set; } = string.Empty;

        [Required, MaxLength(14)]
        public string Cnpj { get; set; } = string.Empty;

        [Required, MaxLength(150)]
        public string Email { get; set; } = string.Empty;

        [Required, MaxLength(255)]
        public string SenhaHash { get; set; } = string.Empty;

        [MaxLength(20)]
        public string? Telefone { get; set; }

        public DateTime CriadoEm { get; set; } = DateTime.UtcNow;

        // Navegação
        [ForeignKey("CidadeId")]
        public Cidade? Cidade { get; set; }

        [ForeignKey("SegmentoId")]
        public Segmento? Segmento { get; set; }

        public ICollection<Evento> Eventos { get; set; } = new List<Evento>();
    }

    // ── EVENTO ──
    [Table("evento")]
    public class Evento
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public int EmpresaId { get; set; }

        [Required]
        public int CategoriaId { get; set; }

        [Required, MaxLength(200)]
        public string Titulo { get; set; } = string.Empty;

        public string? Descricao { get; set; }

        [Required]
        public DateTime DataEvento { get; set; }

        public TimeSpan? Horario { get; set; }

        [Required, MaxLength(200)]
        public string Local { get; set; } = string.Empty;

        [MaxLength(20)]
        public string? ContatoWhatsapp { get; set; }

        public DateTime PublicadoEm { get; set; } = DateTime.UtcNow;

        public DateTime? ExpiraEm { get; set; }

        // Navegação
        [ForeignKey("EmpresaId")]
        public Empresa? Empresa { get; set; }

        [ForeignKey("CategoriaId")]
        public Categoria? Categoria { get; set; }
    }

    // ── DTOs ──
    public class EmpresaCadastroDto
    {
        [Required] public string Nome       { get; set; } = string.Empty;
        [Required] public string Cnpj       { get; set; } = string.Empty;
        [Required] public string Email      { get; set; } = string.Empty;
        [Required] public string Senha      { get; set; } = string.Empty;
        [Required] public int    CidadeId   { get; set; }
        [Required] public int    SegmentoId { get; set; }
        public string? Telefone { get; set; }
    }

    public class EmpresaLoginDto
    {
        [Required] public string Email { get; set; } = string.Empty;
        [Required] public string Senha { get; set; } = string.Empty;
    }

    public class EventoCriarDto
    {
        [Required] public int    EmpresaId   { get; set; }
        [Required] public int    CategoriaId { get; set; }
        [Required] public string Titulo      { get; set; } = string.Empty;
        [Required] public string DataEvento  { get; set; } = string.Empty;
        [Required] public string Local       { get; set; } = string.Empty;
        [Required] public string FotoUrl     { get; set; } = string.Empty; // Obrigatório
        public string? Descricao        { get; set; }
        public string? Horario          { get; set; }
        public string? ContatoWhatsapp  { get; set; }
        public string? ExpiraEm         { get; set; }
    }
}

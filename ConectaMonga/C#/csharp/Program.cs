// =============================================
//  ConectaMonga — Program.cs
//  Backend C# ASP.NET Core Web API
//  Requer: .NET 8 + Pomelo.EntityFrameworkCore.MySql
// =============================================

using ConectaMonga.API.Data;
using ConectaMonga.API.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ── SERVICES ──
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// CORS — permite chamadas do frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
        policy.WithOrigins("http://localhost:3000", "http://localhost:5500")
              .AllowAnyHeader()
              .AllowAnyMethod());
});

// Banco de dados MySQL via Entity Framework
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString)));

// Serviços de negócio
builder.Services.AddScoped<IEventoService, EventoService>();
builder.Services.AddScoped<IEmpresaService, EmpresaService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowFrontend");
app.UseAuthorization();
app.MapControllers();
app.Run();

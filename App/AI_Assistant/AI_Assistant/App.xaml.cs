using AI_Assistant.Services;
using AI_Assistant.Services.Messages;
using AI_Assistant.ViewModels;
using AI_Assistant.ViewModels.Messages;
using AI_Assistant.Views;
using AI_Assistant.Views.Messages;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace AI_Assistant;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{
	public static IHost? AppHost { get; private set; }

	public App()
	{
		AppHost = Host.CreateDefaultBuilder()
			.ConfigureServices((hostContext, services) =>
			{
				this.RegisterServices(services);
				this.RegisterViewModels(services);
				this.RegisterViews(services);
			})
			.Build();
	}

	private void RegisterViews(IServiceCollection services)
	{
		services.AddSingleton<MainWindow>();
		services.AddSingleton<ChatView>();
		
		services.AddSingleton<ExplorerView>();
		services.AddSingleton<SettingsView>();

        services.AddTransient<MessageView>();
		services.AddTransient<MessageCodeView>();
		services.AddTransient<MessageTextView>();
	}

	private void RegisterViewModels(IServiceCollection services)
	{
		services.AddSingleton<MainWindowViewModel>();
		services.AddSingleton<ChatViewModel>();

		services.AddSingleton<ExplorerViewModel>();
		services.AddSingleton<SettingsViewModel>();

		services.AddTransient<MessageViewModel>();
		services.AddTransient<CodeMessagePart>();
		services.AddTransient<TextMessagePart>();
	}

	private void RegisterServices(IServiceCollection services)
	{
		services.AddSingleton<AIChatService>();
		services.AddSingleton<FileService>();
		services.AddSingleton<CodeExecutionService>();

		services.AddSingleton<MessageFactory>();
		services.AddSingleton<MessagePartFactory>();
	}

	protected override async void OnStartup(StartupEventArgs e)
	{
		await AppHost!.StartAsync();

		var startupViewModel = AppHost.Services.GetRequiredService<MainWindowViewModel>();
		startupViewModel.View.Show();

		base.OnStartup(e);
	}
	protected override async void OnExit(ExitEventArgs e)
	{
		await AppHost!.StopAsync();
		base.OnExit(e);
	}
}

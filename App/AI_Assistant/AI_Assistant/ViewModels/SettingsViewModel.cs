using AI_Assistant.Models;
using AI_Assistant.Views;
using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.ViewModels;

public partial class SettingsViewModel : ViewModelBase<SettingsView>
{
	public SettingsViewModel(SettingsView view) : base(view)
	{
		this.Temperature = 1;
		this.TopP = 0.5;
		this.TopK = 50;
		this.MaxNewTokens = 150;
	}

	[ObservableProperty]
	[NotifyPropertyChangedFor(nameof(SettingsNotVisible))]
	private bool settingsVisible;

	public bool SettingsNotVisible => !SettingsVisible;

	[ObservableProperty]
	private double temperature;

	[ObservableProperty]
	private double topP;

	[ObservableProperty]
	private int topK;

	[ObservableProperty]
	private int maxNewTokens;

	public GenerationSettings GetGenerationSettings()
	{
		return new GenerationSettings
		{
			Temperature = this.Temperature,
			TopP = this.TopP,
			TopK = this.TopK,
			MaxNewTokens = this.MaxNewTokens,
		};
	}

	public void ToggleSettingsVisibility()
	{
		SettingsVisible = !SettingsVisible;
	}
}

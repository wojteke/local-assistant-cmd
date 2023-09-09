using AI_Assistant.Views;
using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AI_Assistant.ViewModels;

public partial class ViewModelBase<TView> : ObservableObject where TView : IView
{
    public ViewModelBase(TView view)
    {
		view.DataContext = this;
		View = view;
	}

	public TView View { get; }
}

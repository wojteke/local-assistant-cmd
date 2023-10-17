# Local Assistant :robot::computer:

Local Assistant is your personal AI chat-bot designed to assist with daily computer tasks. Instead of fumbling with various tasks on your computer, just ask the Local Assistant. It responds with the appropriate windows cmd commands to get the job done!

### Supported languages
- English :us: :uk:

## Current State
This is my Master's degree project.\
It serves as a proof of concept - not a production-quality project.\
No new features will be added to this repository (I'll try to keep it up to date with libraries) - as I want to keep it as it was described in paper.\
I'll add the thesis paper 6 months after my graduation.

I plan to create a new repo with a new (better :rocket:) version of this project. See [Roadmap](#Roadmap)


## Description

At the core of Local Assistant are a set of fine-tuned GPT-2 models (small, medium, and large) from Huggingface [Transformers](https://huggingface.co/docs/transformers/index) library using [PyTorch](https://pytorch.org/) implementation. Each of these models was trained using both normal fine-tuning and parameter-efficient tuning [PEFT](https://huggingface.co/docs/peft/index) via the LoRA algorithm.

The models are hosted locally using FastAPI. The user interface, built using a simple WPF chat application, offers a clean and intuitive way to interact with these models.

## Working Demo

1. Simple question - what is my IP?
    ![What is my IP?](examples\example_ip.gif)
2. Files manipulation
    ![Files manipulation](examples\example_files.gif)
3. Generation options
    ![Generation option](examples\example_generation_options.gif)
## Installation

1. Requirements:
    - Python 3.8+
    - .NET 7
2. Installation & running
    1. Install python requirements (use `venv` or `conda` if you prefer)
        ```bash
        pip install -r requirements.txt
        ```
    2. Run `server.py`
        ```
        python server.py
        ```
    3. Build and open WPF App (Visual Studio/.NET required)



## Contributing

This repo is maintained for archival purposes only.

## Roadmap

Below are features that I plan to add to the new version of this project.

1. Clean up the code - use newest versions of transformers api
2. Change cmd command to custom python functions and python in general (that way the project will be cross-platform)
3. Change the UI to cross-platform framework (maybe something electron-based?)
4. Add additional features
    - Web search
    - Multiple language support

## License

This project is licensed under the [MIT License](LICENSE).
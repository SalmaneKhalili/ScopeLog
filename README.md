<div align="center">
  <h1>ScopeLog</h1>
  <p><b>A  Terminal UI to make logs easier to deal with.</b></p>
</div>

<div align="center">
  <div>
    Fast, lightweight log investigation tool built with <a href="https://textual.textualize.io/">Textual</a> and <a href="https://rich.readthedocs.io/">Rich</a>.
  </div>
  <p></p>
  <a href="#features">Features</a>
  <span> • </span>
  <a href="#screenshots">Screenshots</a>
  <span> • </span>
  <a href="#install">Install</a>
  <span> • </span>
  <a href="#usage">Usage</a>
  <p></p>
</div>

---
### About

This is a personal project i built for the https://www.boot.dev/lessons/d4dc954b-06cf-4f7b-bc36-fa9936c245ec ,  The idea is to making dealing with logs a bit easier and where it is supposed to be done, in the terminal. the ui is inspired by the Lazygit ui.

I had to figure out a lot of things while coding this project including, css, how to reap and spawn subprocesses in python, the code is still not in the best shape i want it to be. but i'll keep working on improvements to see where i can take it. 

### Features

- Real-time streaming of log content 

- Filtering options

- Highlighting

-  Tabbed views

- Integrated sidebar for quick log file selection and switching.


### Screenshots

<img width="1916" height="1036" alt="image" src="https://github.com/user-attachments/assets/985b1736-e47b-469e-9f08-b6a1e0d8b844" />


<img width="961" height="1032" alt="image" src="https://github.com/user-attachments/assets/f8d1db2a-dff6-4788-9d7e-75f8c3ab9c89" />


<img width="977" height="1045" alt="image" src="https://github.com/user-attachments/assets/d49cbd23-943b-4398-9e20-5e237a566556" />


### Install

Make sure you have [uv](https://github.com/astral-sh/uv) installed on your system.

Clone the repository and install dependencies:

```bash
git clone git@github.com:SalmaneKhalili/scopelogs.git
cd scopelogs
uv sync

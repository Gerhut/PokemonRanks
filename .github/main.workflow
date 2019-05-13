workflow "Scheduled" {
  on = "schedule(* * 0 0 0)"
  resolves = ["Scheduled.run"]
}

action "Scheduled.install" {
  uses = "docker://python:3.5"
  args = "install -r requirements.txt"
  runs = "pip"
}

action "Scheduled.run" {
  uses = "docker://python:3.5"
  needs = ["Scheduled.install"]
  args = "."
  runs = "python"
  secrets = ["GITHUB_TOKEN", "GIST_ID", "GIST_FILENAME"]
}

workflow "Pushed" {
  on = "push"
  resolves = ["Pushed.run"]
}

action "Pushed.install" {
  uses = "docker://python:3.5"
  runs = "pip"
  args = "install -r requirements.txt"
}

action "Pushed.lint" {
  uses = "docker://python:3.5"
  needs = ["Pushed.install"]
  runs = "flake8"
  args = "*.py"
}

action "Pushed.run" {
  uses = "docker://python:3.5"
  needs = ["Pushed.lint"]
  runs = "python"
  args = "."
  secrets = ["GITHUB_TOKEN", "GIST_ID", "GIST_FILENAME"]
}

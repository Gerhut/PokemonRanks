workflow "Scheduled" {
  on = "schedule(* * 0 0 0)"
  resolves = ["Scheduled.run"]
}

action "Scheduled.run" {
  uses = "docker://python:3.5"
  args = "pip install -r requirements.txt && python ."
  secrets = ["GITHUB_TOKEN", "GIST_ID", "GIST_FILENAME"]
}

workflow "Pushed" {
  on = "push"
  resolves = ["Pushed.run"]
}

action "Pushed.run" {
  uses = "docker://python:3.5"
  args = "pip install -r requirements.txt && flake8 *.py && python ."
  secrets = ["GITHUB_TOKEN", "GIST_ID", "GIST_FILENAME"]
}

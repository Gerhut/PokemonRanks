workflow "Scheduled" {
  on = "schedule(* * 0 0 0)"
  resolves = "install"
}

workflow "Pushed" {
  on = "push"
  resolves = "install"
}

action "install" {
  uses = "docker://python:3.5"
  args = "python -m pip install -r requirements.txt"
}

action "lint" {
  needs = "install"
  uses = "docker://python:3.5"
  args = "python -m flake8 *.py"
}

action "run" {
  needs = "lint"
  uses = "docker://python:3.5"
  args = "python ."
  secrets = ["GITHUB_TOKEN"]
  env = {
    GIST_ID = "051c57ee1f79ba84835809dc2664fac1"
    GIST_FILENAME = "Pokemon Global Link 今日排名"
  }
}

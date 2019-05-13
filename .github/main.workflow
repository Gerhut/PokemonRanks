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
  args = "-m pip install -r requirements.txt"
}

action "lint" {
  uses = "docker://python:3.5"
  args = "-m flake8 *.py"
}

action "run" {
  uses = "docker://python:3.5"
  args = "."
  secrets = ["GITHUB_TOKEN"]
  env = {
    GIST_ID = "051c57ee1f79ba84835809dc2664fac1"
    GIST_FILENAME = "Pokemon Global Link 今日排名"
  }
}

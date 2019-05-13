workflow "Main" {
  on = "schedule(* * 0 0 0)"
  resolves = "Update gist"
}

action "Update gist" {
  uses = "docker://python:3.5"
  runs = ["sh", "-c"]
  args = "pip install -r requirements.txt && python ."
  secrets = ["GITHUB_TOKEN", "GIST_ID"]
  env = {
    GIST_FILENAME = "Pokemon Global Link 今日排名"
  }
}

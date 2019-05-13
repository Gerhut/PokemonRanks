workflow "Scheduled" {
  on = "schedule(* * 0 0 0)"
  resolves = "Update gist"
}

workflow "Pushed" {
  on = "push"
  resolves = "Update gist"

}

action "Update gist" {
  uses = "docker://python:3.5"
  runs = ["sh", "-c"]
  args = "pip install -r requirements.txt && python ."
  secrets = ["GITHUB_TOKEN"]
  env = {
    GIST_ID = "051c57ee1f79ba84835809dc2664fac1"
    GIST_FILENAME = "Pokemon Global Link 今日排名"
  }
}

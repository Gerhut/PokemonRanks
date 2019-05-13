workflow "Update gist" {
  on = "schedule(0 0 * * *)"
  resolves = ["Run"]
}

action "Run" {
  uses = "./"
  secrets = ["GITHUB_TOKEN", "GIST_ID"]
  env = {
    GIST_FILENAME = "Pokemon Global Link 今日排名"
  }
}

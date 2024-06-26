from common import *

class CortexGithub:
  def __init__(self,
               url=os.getenv('GH_URL'), 
               org=os.getenv('GH_ORG'),
               repo_name=os.getenv('GH_REPO'),
               cortex_alias=os.getenv('CORTEX_GH_ALIAS'),
               webhook_url=os.getenv('CORTEX_GH_WEBHOOK_URL')):

    auth = Auth.Token(os.getenv('GH_PAT'))
    g = Github(base_url=url, auth=auth)

    organization = g.get_organization(org)
    if not any(repo.name == repo_name for repo in organization.get_repos()):
        organization.create_repo(repo_name, private=True)

    repo = organization.get_repo(repo_name)

    self.org = org
    self.alias = cortex_alias
    self.repo = repo
    self.webhook_url = webhook_url

  def delete_personal_configuration(self):
      output = io.StringIO()
      with redirect_stdout(output):
          cli(["-q", "integrations", "github", "get-all"])
      response = json.loads(output.getvalue())
      if any(configuration['alias'] == self.alias for configuration in response['configurations']):
          cli(["-q", "integrations", "github", "delete-personal", "-a", self.alias])

  def create_integration(self):
      fd, path = tempfile.mkstemp()
      template = Template("""
          {
            "accessToken": "${gh_pat}",
            "alias": "${cortex_gh_alias}",
            "isDefault": false
          }
          """)
      content = template.substitute(gh_pat=os.getenv('GH_PAT'), cortex_gh_alias=self.alias)
      with open(path, 'w') as f:
          f.write(content)

      os.close(fd)
      self.delete_personal_configuration()
      cli(["-q", "integrations", "github", "add-personal", "-f", path])

  def create_webhook(self):
      EVENTS = ["push", "pull_request"]

      config = {
          "url": self.webhook_url,
          "secret": os.getenv('GH_WEBHOOK_SECRET'),
          "content_type": "json"
      }

      for hook in self.repo.get_hooks():
          if hook.config['url'] == self.webhook_url:
              hook.delete()

      self.repo.create_hook("web", config, EVENTS, active=True)


  def read_entity_template(self, file):
      with open (file, 'r') as f:
         template = Template(f.read())
      return textwrap.dedent(template.substitute(today=today(), org=self.org, repo=self.repo.name, alias=self.alias))


  # Wait max_attempts * sleep_interval for git commit to appear in gitops-logs
  # Will wait for up to 10 minutes for commit to be processed.
  # TODO: find out how we can optimize, or at least understand, the processing time.
  def check_gitops_logs(self, capsys, sha):
      found = False
      #max_attempts = 120
      max_attempts = 30
      sleep_interval = 5
      for attempt in range(1, max_attempts):
          response = cli_command(capsys, ["gitops-logs", "get", "-p", "0", "-z", "25"])
          if any(log['commit'] == sha for log in response['logs']):
              found = True
              break
          else:
              if attempt == max_attempts:
                 break
              time.sleep(sleep_interval)

      return found

  def commit_cortex_entity(self, repo, content, branch, path):
      contents = repo.get_contents("")

      found = False
      while contents:
          file_content = contents.pop(0)
          if file_content.path == path:
              found = True
              break
          if file_content.type == "dir":
              contents.extend(repo.get_contents(file_content.path))

      commit_message = "commit on " + today() + "."

      # https://github.com/PyGithub/PyGithub/issues/1787
      # Seeing some 409 errors with this.  Might need a sleep here?  Doesn't seem like a great solution.
      # Maybe the python implementation gets confused when multiple invocations run in parallel, as happens
      # with the pytests running in parallel and the API is called at the same time?
      time.sleep(random.randint(1, 10))
      if found:
          contents = repo.get_contents(path, ref=branch)
          c = repo.update_file(path, commit_message, content, contents.sha, branch=branch)
      else:
          # TODO - how to create initial file in repo?
          c = repo.create_file(path, commit_message, content, branch=branch)

      return c['commit'].sha


def gitops_add(capsys, template, path):
    g = CortexGithub()
    content = g.read_entity_template(template)
    sha = g.commit_cortex_entity(g.repo, content, g.repo.default_branch, path)
    return g.check_gitops_logs(capsys, sha)

def github_setup():
    g = CortexGithub()
    g.create_webhook()
    g.create_integration()

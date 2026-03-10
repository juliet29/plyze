
push-tag end:
  git tag -a s0.1.{{end}} -m s0.1.{{end}}
  git push --tag


publish-tag end:
  @echo "Have you updated the version number for pushing to pypi?" 
  @read status;


  @echo "Have you pushed the code with this new version number?" 
  @read status;

  git tag -a v0.1.{{end}} -m v0.1.{{end}}
  git push --tag
  gh run list
  #TODO: read from the tags automatically using sed / awk 


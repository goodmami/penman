
# How to contribute

Thanks for getting involved in Penman's development!

### Reporting bugs and requesting features

Please report bugs or feature requests on the
[issues](https://github.com/goodmami/penman/issues) page.
Mention the version numbers of Penman and Python that you are using.
Also report inaccurate or missing documentation from the
[API docs](http://goodmami.github.io/penman/docs/API).

### Contributing code

If you wish to contribute code to Penman, please fork the repository to
your own account, commit your changes, and submit a
[pull request](https://github.com/goodmami/penman/compare/) to the
`develop` branch.

Please follow [PEP8](python.org/dev/peps/pep-0008/) unless you have a
good reason not to, and also try to follow the conventions set by the
Penman codebase.

I also try to follow this branching model:
http://nvie.com/posts/a-successful-git-branching-model/

Basically, each new changeset (e.g. features or bug fixes) should have
its own branch. Changeset branches (except critical bug fixes) get
merged to the develop branch, and develop gets merged back to master
when a new release is ready.

# jetpacs-site — jetpacs.org

The whole jetpacs.org docroot: a Hugo site per project plus a shared kit.

    jetpacs/            docs site       -> jetpacs.org/docs/
    ebp/                docs sub-site   -> jetpacs.org/ebp/{,docs/}
    glasspane/          docs sub-site   -> jetpacs.org/glasspane/{,docs/}
    jetpacs-composer/   docs sub-site   -> jetpacs.org/jetpacs-composer/{,docs/}
    _jetpacs-kit/       shared theme assets, landing generator, sync tooling
    _root/              root landing page (index.html + icon), committed source
    public/             assembled docroot (generated -- never committed)

## Editing docs

Content under each site's `content/` is SYNCED from the project repos
(`~/pkb/projects/jetpacs/<repo>`, branch `slop-fork/main`) — edit upstream,
then run `./sync-docs.sh` in the site dir (or `_jetpacs-kit/make-sites.py`
for the three sub-sites) and commit the result here.

## Build and preview

    ./build-all.sh              # assemble public/
    _jetpacs-kit/preview.sh     # serve it at http://localhost:8000

## Deploy

Pushing to main runs .github/workflows/deploy.yml: Hugo builds everything
and publishes public/ to GitHub Pages under the custom domain jetpacs.org.
APKs are NOT hosted here — pre-release builds belong on GitHub Releases;
the site links to them.

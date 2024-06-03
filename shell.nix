with import <nixpkgs> {};

let
  dynaconf = python312.pkgs.buildPythonPackage rec {
    pname = "dynaconf";
    version = "3.2.5";
    pyproject = true;

    src = fetchPypi {
      inherit pname version;
      hash = "sha256-QsjZNrMjMsS4Tk1N9t0WJrbvWcWpTrYMEM08Wda4gvI=";
    };

    build-system = [
      python312.pkgs.setuptools
      python312.pkgs.wheel
    ];

    # has no tests
    doCheck = false;
  };

  # last available pycharm
  ideaPkgs = import (fetchTarball https://nixos.org/channels/nixos-unstable/nixexprs.tar.xz) { };
  pycharm = ideaPkgs.jetbrains.pycharm-professional;


  in 
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [
      pycharm
      ruff
      pre-commit
      (pkgs.python312.withPackages (ps: with ps; [
        ps.fastapi
        ps.pytest
        ps.sqlalchemy
        ps.pymysql
        ps.uvicorn
        ps.alembic
        ps.httpx
        ps.pyjwt
        ps.argon2_cffi
        ps.passlib
        ps.josepy
        ps.python-multipart
        ps.testcontainers
        ps.docker
        ps.wrapt
        ps.python-on-whales
        dynaconf
      ]))
    ];
    shellHook = ''
      export DIMAIL_JWT_SECRET="a secret secret"
      export DIMAIL_STARTS_TESTS_CONTAINERS=1
    '';
  }


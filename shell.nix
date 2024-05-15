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

    meta = {
      homepage = "https://github.com/pytoolz/toolz/";
      description = "List processing tools and functional utilities";
      # [...]
    };
  };

  # last available pycharm
  ideaPkgs = import (fetchTarball https://nixos.org/channels/nixos-unstable/nixexprs.tar.xz) { };
  pycharm = ideaPkgs.jetbrains.pycharm-professional;


  in 
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [
      pycharm
      (pkgs.python312.withPackages (ps: with ps; [
        ps.fastapi
        ps.pytest
        ps.sqlalchemy
        ps.pymysql
        ps.uvicorn
        ps.flake8
        ps.black
        ps.isort
        ps.alembic
        ps.httpx
        dynaconf
      ]))
    ];
  }

